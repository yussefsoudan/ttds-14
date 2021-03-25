import os.path
import json
import pickle
import sys
# from db.DB import get_db_instance
from MongoDB import MongoDB 
from pathlib import Path
import math
import time
import pymongo
# from ir_eval.utils.score_tracker import ScoreTracker, NaiveScoreTracker
# from ir_eval.ranking.phrase_search import phrase_search
from collections import defaultdict
import pprint
from collections import Counter


db = MongoDB()


# This function is responsible for taking a dictionary of the form
# term : {doc_id : score}
# Documents could either be books or quotes in this function
# Find all documents that are common among all search terms given
def get_common_documents(scored_docs_per_term):
    common_docs = set()
    scored_docs = {}
    for i, (term,doc_scores) in enumerate(scored_docs_per_term.items()):
        if i ==0:
            common_docs = set(doc_scores.keys())
        else:
            # Get the intersection of all quote_id or book_id between the terms of the query
            common_docs = common_docs.intersection(set(doc_scores.keys()))

    print("Common docs",common_docs)
    for term, doc_scores in scored_docs_per_term.items():
        for doc_id, score in doc_scores.items():
            if doc_id in common_docs:
                scored_docs[doc_id] = score if doc_id not in scored_docs else scored_docs[doc_id] + score


    print("scored quotes",scored_docs)
    return scored_docs

# ------------------- Book search and ranking --------------------------
# -----------------------------------------------------------------------

TOTAL_NUMBER_OF_BOOKS = 30630 
MAX_QUERY_TIME = 10  # max seconds to allow the query to run for


# # Dictionary containing for each book, the total number of terms 
# # TO-DO: Write script to iterate over books and create a pickle file
# # containing their term count
# books_total_term_counts = defaultdict(lambda: 1)
# pickle_path = Path(__file__).parent.absolute() / "utils" / 'books_term_counts.p'
# print(pickle_path)

# if os.path.isfile(pickle_path):
#     books_total_term_counts = defaultdict(lambda: 1, pickle.load(open(pickle_path, 'rb')))
#     TOTAL_NUMBER_OF_BOOKS = len(books_total_term_counts)
# else:
#     print("no pickle file for books term counts found")

# pprint.pprint(books_total_term_counts)


def get_total_term_count(book_id):
    # Technically this should return only one document back
    book_docs = db.books.find({"_id": book_id})
    for book_doc in book_docs:
        terms_count = book_doc["terms_count"]
        if terms_count ==0:
            print(f"Term counts for book {book_id} is {terms_count}")
            return 1000
        return terms_count


def tfidf(book_id, book_term_freq, term_book_count):
    """ 
    Calculate
    TF(t) = (Number of times term t appears in a document) / (Total number of terms in the document).
    IDF(t) = log_e(Total number of documents / Number of documents with term t in it).
    """
    tf = float(book_term_freq) / get_total_term_count(book_id)
    idf = math.log(float(TOTAL_NUMBER_OF_BOOKS) / term_book_count)

    return tf * idf

def ranked_book_search(query_params): #, number_results # what is the number_results used for
    tracker = book_ranking_query_TFIDF(query_params)
    return tracker

def book_ranking_query_TFIDF(query_params):
    scored_books_per_term = {} 
    terms = query_params['query']
    relevant_books = None
    if any([query_params['author'], query_params['bookTitle'], query_params['genre'], int(query_params['min_rating']) > 1,
            int(query_params['yearTo']) < 2021, int(query_params['yearFrom']) > 1990]):
        relevant_books = db.get_filtered_books_by_adv_search(query_params)
    start_time = time.time()
    for term in terms:
        scored_books_per_term[term] = {}

        print("Term for book search",term)
        # Setup
        # Since index could have multiple occurences of term
        # it might return multiple Cursor objects 
        term_docs = list(db.get_books_by_term(term))
        print(f"Number of index entries for term {term} is {len(term_docs)}")

        total_book_count = 0
        for term_doc in term_docs:
            # print(term_doc)
            total_book_count += len(term_doc['books'])

        print(f"Term {term} book count: {total_book_count}")

        # Compute
        for idx,term_doc in enumerate(term_docs):
            print(f"Index entry {idx} has {len(term_doc['books'])} books")
            for book in term_doc['books']:
                # print("Book id",book['_id'])
                # print("Book term frequency",book['term_freq_in_book'])
                book_id = book['_id']
                if relevant_books is None or book_id in relevant_books:
                    book_term_freq = book['term_freq_in_book']
                    score = tfidf(book_id,book_term_freq,total_book_count)

                    if book_id in scored_books_per_term[term] :
                       scored_books_per_term[term][book_id] += score
                    else:
                        scored_books_per_term[term][book_id] = score
            # Time control
            if time.time() - start_time > MAX_QUERY_TIME:
                print(f"Time exceeded for index entry {idx}")
                break

        # Time control
        if time.time() - start_time > MAX_QUERY_TIME:
            break
    
    scored_books = get_common_documents(scored_books_per_term)
    return Counter(scored_books).most_common(20)



# ------------------- Quote search and ranking --------------------------
# -----------------------------------------------------------------------

MAX_INDEX_SPLITS = 200  # maximum number of different entries in the inverted_index with the same term
TOTAL_NUMBER_OF_SENTENCES = 50630265  #TODO NEEDS UPDATE
MAX_QUERY_TIME = 10  # max seconds to allow the query to run for
MAX_TERM_TIME = 4
batch_size = 20



# def get_common_documents(scored_quotes_per_term):
#     common_quotes = set()
#     scored_quotes = {}
#     for i, (term,quote_scores) in enumerate(scored_quotes_per_term.items()):
#         if i ==0:
#             common_quotes = set(quote_scores.keys())
#         else:
#             # Get the intersection of all quote_ids between the terms of the query
#             common_quotes = common_quotes.intersection(set(quote_scores.keys()))

#     print("COmmon quotes",common_quotes)
#     for term, quote_scores in scored_quotes_per_term.items():
#         for quote_id, score in quote_scores.items():
#             if quote_id in common_quotes:
#                 scored_quotes[quote_id] = score if quote_id not in scored_quotes else scored_quotes[quote_id] + score


#     print("scored quotes",scored_quotes)
#     return scored_quotes


def ranked_quote_retrieval(query): # , number_results, search_phrase=False
    tracker = ranking_query_BM25(query, batch_size)
    return tracker # result_ids

def ranking_query_BM25(query_params, batch_size=MAX_INDEX_SPLITS):
    # scored_quotes = {}
    scored_quotes_per_term = {} # term -> {q_id:score}
    terms = query_params['query']
    relevant_books = None
    if any([query_params['author'], query_params['bookTitle'], query_params['genre'], int(query_params['min_rating']) > 1,
            int(query_params['yearTo']) < 2021, int(query_params['yearFrom']) > 1990]):
        relevant_books = db.get_filtered_books_by_adv_search(query_params)
    print("Terms",terms)

    doc_nums = TOTAL_NUMBER_OF_SENTENCES
    total_start_time = time.time()
    for term in terms:
        scored_quotes_per_term[term] = {}
        print("Term:",term)
        term_start_time = time.time()
        try:
            # iterate documents of this term by batches
            for i in range(0, MAX_INDEX_SPLITS, batch_size):
                print("I=",i)
                # returns cursor object
                # will return objects with id:term
                term_docs = db.get_docs_by_term(term, i, batch_size)

                process_start = time.time()
                for term_doc in term_docs:
                    if time.time() - term_start_time > MAX_TERM_TIME:
                        print("Time limit")
                        break
                        
                    # print("Term doc")
                    # print(term_doc)

                    # number of documents containing the term
                    # documents in this case are the quotes
                    doc_nums_term = term_doc['term_freq'] 
                    # print("Document frequency",doc_nums_term )

                    # return
                    # print(term_doc['books'])
                    for b,book in enumerate(term_doc['books']):
                        if relevant_books is not None and book['_id'] not in relevant_books:
                            continue
                        for q,quote in enumerate(book['quotes']):
                            # how many times the term appears in the quote
                            term_freq = len(quote['pos']) #TODO CURRENTLY THIS IS 0 ALL THE TIME !!!!
                            # document length, how many terms appear overall in this quote
                            dl = quote['len']
                            quote_id = quote['_id']

                            # print("Term frequency",term_freq)
                            # print("Document length of current quote",dl)
                            score = score_BM25(doc_nums, doc_nums_term, term_freq, k1=1.2, b=0.75, dl=dl, avgdl=4.82) if dl < 100000 else 0
                            if score > 0:
                                if quote_id in scored_quotes_per_term[term]:
                                    scored_quotes_per_term[term][quote_id] += score
                                else:
                                    scored_quotes_per_term[term][quote_id] = score
                                # scored_quotes[quote_id] = score
                            if time.time() - total_start_time > MAX_QUERY_TIME:
                                scored_quotes = get_common_documents(scored_quotes_per_term)
                                return Counter(scored_quotes).most_common(20)
        except:
            pass
    
    scored_quotes = get_common_documents(scored_quotes_per_term)

    return Counter(scored_quotes).most_common(20)


def score_BM25(doc_nums, doc_nums_term, term_freq, k1, b, dl, avgdl):
    """ Source for BM25: https://en.wikipedia.org/wiki/Okapi_BM25 """
    K =  k1 * ((1-b) + b * (float(dl)/float(avgdl)) )
    idf_param = math.log( (doc_nums-doc_nums_term+0.5) / (doc_nums_term+0.5) )
    next_param = ((k1 + 1) * term_freq) / (K + term_freq)
    return float("{0:.4f}".format(next_param * idf_param))


# ------------------- Phrase search and ranking --------------------------
# ------------------------------------------------------------------------
def quote_phrase_search(query):
    tracker = phrase_search(query)
    return tracker

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
                        intermediate.add(doc_1['books'][book_pos_1]['quotes'][quote_pos_1]['_id'])
                    
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
    
if __name__ == '__main__':

    db = MongoDB()
    batch_size = 50
