import os.path
import json
import pickle
import sys
# from db.DB import get_db_instance
from MongoDB import MongoDB 
# from pathlib import Path
import math
import time
import pymongo
# from ir_eval.utils.score_tracker import ScoreTracker, NaiveScoreTracker
# from ir_eval.ranking.phrase_search import phrase_search
from collections import defaultdict
import pprint
from collections import Counter

db = MongoDB()

# ------------------- Book search and ranking --------------------------
# -----------------------------------------------------------------------

TOTAL_NUMBER_OF_BOOKS = 13
MAX_QUERY_TIME = 10  # max seconds to allow the query to run for

# Dictionary containing for each book, the total number of terms 
# TO-DO: Write script to iterate over books and create a pickle file
# containing their term count
books_term_counts = defaultdict(lambda: 1)
PATH = os.getcwd() # returns path of the directory book-search-api-py
pickle_path = PATH + "/utils/book_term_counts.p"  # Path(__file__).parent.absolute() / "utils" / 'books_term_counts.p'
print(pickle_path)

if os.path.isfile(pickle_path):
    print("loading pickle file for books term counts")
    books_term_counts = defaultdict(lambda: 1, pickle.load(open(pickle_path, 'rb')))
    TOTAL_NUMBER_OF_BOOKS = len(books_term_counts)
else:
    print("no pickle file for books term counts found")

pprint.pprint(books_term_counts)

    
def tfidf(book_id, book_term_freq, term_book_count):
    """
    Computes TFIDF score for a document-term pair.
    :param book_id: the _id of a book from the inverted index
    :param book_term_freq: the term frequency of the term in the book, of the form {'term_freq_in_book': int)
    :param term_book_count: total number of books containing the term
    :return:
    """

    """ 
    Calculate
    TF(t) = (Number of times term t appears in a document) / (Total number of terms in the document).
    IDF(t) = log_e(Total number of documents / Number of documents with term t in it).
    """
    tf = 1.0 * book_term_freq['term_freq_in_book'] / books_term_counts.get(book_id, 10000) # temporary value
    idf = math.log(1.0 * TOTAL_NUMBER_OF_BOOKS / term_book_count)

    return tf * idf

def ranked_book_search(query_params): #, number_results # what is the number_results used for
    tracker = book_ranking_query_TFIDF(query_params)
    return tracker

def book_ranking_query_TFIDF(query_params):
    scored_books = {} 
    terms = query_params['query']
  
    start_time = time.time()
    for term in terms:
        print("Term for book search",term)
        # Setup
        # Since index could have multiple occurences of term
        # it might return multiple doc objects 
        term_docs = list(db.get_books_by_term(term))
        total_book_count = 0
        for term_doc in term_docs:
            # print(term_doc)
            total_book_count += len(term_doc['books'])

        print(f"Term {term} book count: {total_book_count}")

        # Compute
        for term_doc in term_docs:
            for book_id in term_doc['books']:
                book_term_freq = term_doc['books'][book_id] # returns { "term_freq_in_book" : int } 
                score = tfidf(book_id,book_term_freq,total_book_count)
                scored_books[book_id] = score

        # Time control
        if time.time() - start_time > MAX_QUERY_TIME:
            break

    return Counter(scored_books).most_common(20)


# ------------------- Quote search and ranking --------------------------
# -----------------------------------------------------------------------

MAX_INDEX_SPLITS = 5  # maximum number of different entries in the inverted_index with the same term
TOTAL_NUMBER_OF_SENTENCES = 18576 
MAX_QUERY_TIME = 10  # max seconds to allow the query to run for
MAX_TERM_TIME = 4
batch_size = 20

def ranked_quote_retrieval(query): # , number_results, search_phrase=False
    tracker = ranking_query_BM25(query, batch_size)
    return tracker # result_ids

def ranking_query_BM25(query_params, batch_size=MAX_INDEX_SPLITS):
    scored_quotes = {}
    terms = query_params['query']
    print("Terms",terms)

    doc_nums = TOTAL_NUMBER_OF_SENTENCES
    total_start_time = time.time()
    for term in terms:
        print("Term",term)
        term_start_time = time.time()
        try:
            # iterate documents of this term by batches
            for i in range(0, MAX_INDEX_SPLITS, batch_size):
                print("I=",i)
                # returns doc object
                # will return objects with id:term
                term_docs = db.get_docs_by_term(term, i, batch_size)

                process_start = time.time()
                for term_doc in term_docs:
                    if time.time() - term_start_time > MAX_TERM_TIME:
                        print("Time limit")
                        break

                    # number of documents containing the term
                    # maybe the index field  should be named doc_count instead
                    doc_nums_term = term_doc['term_freq'] 
                    print("Document frequency",doc_nums_term)
                    # print(term_doc['books'])
                    for b, book_id in enumerate(term_doc['books']):
                        book  = term_doc['books'][book_id]
                        # print(book)
                        for q, quote_id in enumerate(book['quotes']):
                            quote = book['quotes'][quote_id]
                            # how many times the term appears in the quote
                            term_freq = len(quote['pos']) 
                            dl = quote['len']
                            score = score_BM25(doc_nums, doc_nums_term, term_freq, k1=1.2, b=0.75, dl=dl, avgdl=4.82) if dl < 100000 else 0
                            if score > 0:
                                scored_quotes[quote_id] = score
                            if time.time() - total_start_time > MAX_QUERY_TIME:
                                return Counter(scored_quotes).most_common(20)
        except:
            pass

    return Counter(scored_quotes).most_common(20)


def score_BM25(doc_nums, doc_nums_term, term_freq, k1, b, dl, avgdl):
    """ Source for BM25: https://en.wikipedia.org/wiki/Okapi_BM25 """
    K =  k1 * ((1-b) + b * (float(dl)/float(avgdl)) )
    idf_param = math.log( (doc_nums-doc_nums_term+0.5) / (doc_nums_term+0.5) )
    next_param = ((k1 + 1) * term_freq) / (K + term_freq)
    return float("{0:.4f}".format(next_param * idf_param))


# ------------------- Phrase search and ranking --------------------------
# ------------------------------------------------------------------------

def phrase_search(query_params): 
    results = set()
    terms = query_params['query']
    start_time = time.time()

    for i in range(1, len(terms)):
        intermediate = set()

        # doing phrase search for pair of terms in phrase (so 1st,2nd / 1st,3rd / 1st,4th etc.)
        documents_1 = db.get_docs_by_term(terms[0], 0, sort=True) # get documents for first term
        documents_2 = db.get_docs_by_term(terms[i], 0, sort=True)
        doc_1 = next(documents_1, None)
        doc_2 = next(documents_2, None)

        # track the position of each book in the book arrays
        book_pos_1 = 0 
        book_pos_2 = 0

        # track position of quote in quote arrays
        quote_pos_1 = 0
        quote_pos_2 = 0
        break_doc_loop = False
        doc_time = time.time()

        while doc_1 is not None and doc_2 is not None:
            if time.time() - start_time > 10:
                break
            book_loop_time = time.time()
            # increment book position of the second doc (corresponding to second term) until 
            # second term's book id >= first term's book id
            while doc_2['books'][book_pos_2]['_id'] < doc_1['books'][book_pos_1]['_id']:
                quote_pos_2 = 0
                book_pos_2 += 1
                
                # this just checks if the end of a document has been reached
                if book_pos_2 >= len(doc_2['books']):
                    # print("moving doc_2 to the next")
                    book_pos_2 = 0 
                    doc_2 = next(documents_2, None)        

                    if doc_2 is None:
                        # print("while incrementing book ids, reached the end of the docs, setting break_doc_loop to True")
                        break_doc_loop = True
                        break   
            
            # print("time for book loop: {}".format(time.time() - book_loop_time))
            # print("book_1_id is: {}".format(doc_1['books'][book_pos_1]['_id']))
            # print("book_2_id is: {}".format(doc_2['books'][book_pos_2]['_id']))

            # at this point second term's book id should be >= first term's book id; if they are equal, enter if statement
            if not break_doc_loop and doc_1['books'][book_pos_1]['_id'] == doc_2['books'][book_pos_2]['_id']:
                quote_loop_time = time.time() 

                # do the same for the quote positions - to get second term's quote id for the book >= first term's quote id for the book
                while doc_2['books'][book_pos_2]['quotes'][quote_pos_2]['_id'] < doc_1['books'][book_pos_1]['quotes'][quote_pos_1]['_id']:
                    quote_pos_2 += 1

                    # if quotes array exceeded -> move to next book in books array -> if books array exceeded
                    # -> move to next doc in the returned documents -> if doc is None (end of documents reached), break
                    if quote_pos_2 >= len(doc_2['books'][book_pos_2]['quotes']):
                        quote_pos_2 = 0
                        # print("incremented book_pos_2 by 1")
                        book_pos_2 += 1

                        if book_pos_2 >= len(doc_2['books']):
                            book_pos_2 = 0 
                            doc_2 = next(documents_2, None)   

                            if doc_2 is None:
                                # print("while incrementing quote ids, reached the end of the docs, setting break_doc_loop to True")
                                break_doc_loop = True
                                break        
                
                # print("time for quote loop: {}".format(time.time() - quote_loop_time))
                # print("quote_1_id is: {}".format(doc_1['books'][book_pos_1]['quotes'][quote_pos_1]['_id']))
                # print("quote_2_id is: {}".format(doc_2['books'][book_pos_2]['quotes'][quote_pos_2]['_id']))

                if not break_doc_loop and doc_1['books'][book_pos_1]['quotes'][quote_pos_1]['_id'] == doc_2['books'][book_pos_2]['quotes'][quote_pos_2]['_id']:
                    # print("FOUND EQUAL QUOTE ID: {}".format(doc_1['books'][book_pos_1]['quotes'][quote_pos_1]['_id']))
                    find_pos_time = time.time()
                    
                    pos_1_list = doc_1['books'][book_pos_1]['quotes'][quote_pos_1]['pos']
                    pos_2_list = doc_2['books'][book_pos_2]['quotes'][quote_pos_2]['pos']

                    pos_check = [int(x1) - int(x2) for (x1, x2) in zip(pos_2_list, pos_1_list)]

                    # this checks if it's a phrase occurring in the common book + common quote
                    if i in pos_check:
                        intermediate.add((doc_1['books'][book_pos_1]['_id'], doc_1['books'][book_pos_1]['quotes'][quote_pos_1]['_id']))
                    
                    quote_pos_1 += 1
                    # if quotes array exceeded -> move to next book in books array -> if books array exceeded
                    # -> move to next doc in the returned documents -> if doc is None (end of documents reached), break
                    if quote_pos_1 >= len(doc_1['books'][book_pos_1]['quotes']):
                        quote_pos_1 = 0
                        book_pos_1 += 1

                        if book_pos_1 >= len(doc_1['books']):
                            book_pos_1 = 0
                            doc_1 = next(documents_1, None)
                            
                            if doc_1 is None:
                                # print("while moving doc_1 after finding a phrase, reached None; break")
                                # break_doc_loop = True
                                break
                            
                    # print("time spent finding position in quote: {}".format(time.time() - find_pos_time))
                    
                else:
                    # if quotes array exceeded -> move to next book in books array -> if books array exceeded
                    # -> move to next doc in the returned documents -> if doc is None (end of documents reached), break
                    quote_pos_1 += 1
                    if quote_pos_1 >= len(doc_1['books'][book_pos_1]['quotes']):
                        quote_pos_1 = 0
                        book_pos_1 += 1

                        if book_pos_1 >= len(doc_1['books']):
                            book_pos_1 = 0 
                            doc_1 = next(documents_1, None)

                            if doc_1 is None:
                                # print("while moving doc 1 when quote ids didnt match, reached None; break")
                                break

            else:
                # print("incremented book pos 1 by 1")
                quote_pos_1 = 0
                book_pos_1 += 1

                # if books array exceeded -> move to next doc in the returned documents -> if doc is None (end of documents reached), break
                if book_pos_1 >= len(doc_1['books']):
                    quote_pos_1 = 0
                    book_pos_1 = 0
                    doc_1 = next(documents_1, None)

                    if doc_1 is None:
                        # print("book ids didnt match and moved doc 1 forward, reached None; break")
                        break

            if break_doc_loop:
                # print("one of the previous while loops set break_doc_loop to true, break")
                break

        # for each pair of terms (e.g. 1st,2nd), intersect with what has been found so far
        # e.g. 1st,2nd returns a certain intermediate set of quote ids (containing pos diff 1 for 1st,2nd terms)
        # 1st,3rd returns a certain intermediate set of quote ids, (containing pos diff 2 for 1st,3rd terms)
        # we want intersection of the two to ensure quotes returned contains phrase 1st,2nd,3rd
        if len(intermediate) != 0:
            # print("intermediate is: {}".format(intermediate))
            if len(results) == 0:
                results = intermediate
            else:
                # comm_keys = set(results.keys()).intersection(intermediate.keys())
                results = results.intersection(intermediate)
            # print("doc time: {}".format(time.time() - doc_time))
        else:
            # print("none of this phrase found")
            results = set()
            break   
    
    # print("results are: {}".format(results))
    # results are tuples (book_id, quote_id)
    return results



# ************ WINNING TEAMS CODE USED FOR REFERENCE, DELETE SOON ****************
#     cursors = []
#     for dist, term in enumerate(terms):
#         cursor = db.get_docs_by_term(term, 0, sort=True)
#         index = next(cursor, None)
#         cursors.append({
#             'cursor': cursor,
#             'index': index,
#             'b': 0,  # movie index
#             'q': 0,  # sentence index
#             'p': 0  # position index,
#         })

#     # print("Cursors beginning:")
#     # print_cursors(cursors)

#     # while all(c['index'] is not None for c in cursors):  # continue until at least one cursor is fully exhausted
#     start_time = time.time()
#     while True:  # continue until at least one cursor is fully exhausted
#         for i in range(len(cursors) - 1):
#             cur_i = cursors[i]
#             cur_j = cursors[i+1]
#             # catch up j with i
#             # cur_j_before = cursor_to_tuple(cur_j)
#             exhausted = catchup(cur_j, cur_i)
#             # if cur_j_before != cursor_to_tuple(cur_j):
#             #     print(f"Cursor {i+1} caught up with Cursor {i}:")
#             #     print_cursors(cursors)
#             if exhausted:  # cur_j has been exhausted so there's no point in trying to find any more matches, abort.
#                 return results
#         # At this point, the term cursors should be ordered, e.g. "i" < "am" < "your" < "father".
#         # Check if an exact phrase match was found.
#         phrase_found = True
#         start_cur = cursors[0]
#         start_mov = start_cur['index']['books'][start_cur['b']]
#         start_sen = start_mov['quotes'][start_cur['q']]
#         start_pos = start_sen['pos'][start_cur['p']] if len(start_sen['pos']) != 0 else ""

#         for i in range(1, len(cursors)):
#             cur = cursors[i]
#             if start_pos == "":
#                 phrase_found = False
#                 break
#             if cur['index']['books'][cur['b']]['_id'] != start_mov['_id'] or \
#                     cur['index']['books'][cur['b']]['quotes'][cur['q']]['_id'] != start_sen['_id'] or \
#                     cur['index']['books'][cur['b']]['quotes'][cur['q']]['pos'][cur['p']] - start_pos != i:
#                 phrase_found = False
#                 break
#         if phrase_found:  # supports advanced search
#             results.append({
#                 'movie_id': start_mov['_id'],
#                 'sentence_id': start_sen['_id']
#             })
#         # # Done. Now advance the first cursor ("i") to catch up with the last cursor ("father").
#         end_cur = cursors[-1]
#         end_mov = end_cur['index']['books'][end_cur['b']]
#         end_sen = end_mov['quotes'][end_cur['q']]
#         print("end_cur['p']: {}".format(end_cur['p']))
#         print("end_sen['pos']: {}".format(end_sen['pos']))
#         end_pos = end_sen['pos'][end_cur['p']] if len(end_sen['pos']) != 0 else ""
#         pos_check = start_sen['pos'][start_cur['p']] < end_pos if end_pos != "" else False

#         if start_mov['_id'] < end_mov['_id']:
#             advance_cursor_iterator(start_cur, 'b')
#         elif start_mov['_id'] == end_mov['_id'] and start_sen['_id'] < end_sen['_id']:
#             advance_cursor_iterator(start_cur, 'q')
#         elif start_mov['_id'] == end_mov['_id'] and start_sen['_id'] == end_sen['_id'] and pos_check:
#             advance_cursor_iterator(start_cur, 'p')

#         # print("Start cursor advanced:")
#         # print_cursors(cursors)

#         if start_cur['cursor'] is None:
#             return results

# def advance_cursor_iterator(cursor, which):
#     # which can be either 'b', 'q', 'p', or 'i' (for 'index')
#     if cursor['index'] is None:
#         return
#     if which == 'p':
#         cursor['p'] += 1
#         if cursor['p'] >= len(cursor['index']['books'][cursor['b']]['quotes'][cursor['q']]['pos']):
#             cursor['p'] = 0
#             which = 'q'
#     if which == 'q':
#         cursor['q'] += 1
#         cursor['p'] = 0
#         if cursor['q'] >= len(cursor['index']['books'][cursor['b']]['quotes']):
#             cursor['q'] = 0
#             which = 'b'
#     if which == 'b':
#         cursor['b'] += 1
#         cursor['q'] = 0
#         cursor['p'] = 0
#         if cursor['b'] >= len(cursor['index']['books']):
#             cursor['b'] = 0
#             which = 'i'
#     if which == 'i':
#         cursor['index'] = next(cursor['cursor'], None)
#         cursor['b'] = 0
#         cursor['q'] = 0
#         cursor['p'] = 0


# def catchup(cur_from, cur_to):
#     # cur_from is behind cur_to if the movie_id, sentence_id or position of cur_from is lower than cur_to
#     while cur_from['index']['books'][cur_from['b']]['_id'] < cur_to['index']['books'][cur_to['b']]['_id']:
#         # advance movie iterator
#         advance_cursor_iterator(cur_from, 'b')
#         if cur_from['index'] is None:
#             return True  # True means that the cursor has been exhausted (no more index entries)

#     movie_from = cur_from['index']['books'][cur_from['b']]
#     movie_to = cur_to['index']['books'][cur_to['b']]
#     if movie_from['_id'] == movie_to['_id']:
#         # caught up with the movie and a movie match was found. Now catch up with the sentence
#         while movie_from['quotes'][cur_from['q']]['_id'] < movie_to['quotes'][cur_to['q']]['_id']:
#             # advance sentence iterator
#             advance_cursor_iterator(cur_from, 'q')
#             if cur_from['index'] is None:
#                 return True  # True means that the cursor has been exhausted (no more index entries)
#             if cur_from['q'] == 0:  # end of sentences has been reached
#                 return False  # there's no way we'll have a movie match now (movie_from > movie_to), catch up is done.

#     sen_from = movie_from['quotes'][cur_from['q']]
#     sen_to = movie_to['quotes'][cur_to['q']]
#     if movie_from['_id'] == movie_to['_id'] and sen_from['_id'] == sen_to['_id']:
#         # caught up with the movie and sentence. Now catch up with the position
#         helper_from = sen_from['pos'] if len(sen_from['pos']) != 0 else ""
#         helper_to = sen_to['pos'] if len(sen_to['pos']) != 0 else ""
#         loop = True

#         if helper_from == "":
#             advance_cursor_iterator(cur_from, 'q')
#             loop = False
#         if helper_to == "":
#             advance_cursor_iterator(cur_to, 'q')
#             loop = False
        
#         if loop:
#             while sen_from['pos'][cur_from['p']] < sen_to['pos'][cur_to['p']]:
#                 advance_cursor_iterator(cur_from, 'p')
#                 if cur_from['index'] is None:
#                     return True  # True means that the cursor has been exhausted (no more index entries)
#                 if cur_from['p'] == 0:  # end of positions reached
#                     return False

#     return False
    
if __name__ == '__main__':
    db = MongoDB()
    query_params = {'query': ["develop", "talent"]} # ["develop", "talent"]["home", "school"]["american", "boy", "smile"]["read", "short", "stori"]
    start = time.time()
    tracker = phrase_search(query_params) 
    end = time.time()
    print(end-start)
    print(tracker)