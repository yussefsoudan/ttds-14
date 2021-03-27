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
import re
import nltk 
from nltk.corpus import stopwords
nltk.download('stopwords')
import gc


db = MongoDB()
books_term_count = Counter()

def populate_terms_count_dictionary():
    books = db.books
    all_books = books.find({}, {"terms_count": 1})

    for book in all_books:
        books_term_count[book['_id']] = book['terms_count'] if book['terms_count'] > 0 else 10000


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


# def get_total_term_count(book_id):
#     # Technically this should return only one document back
#     book_doc = next(db.books.find({"_id": book_id}))
#     terms_count = book_doc["terms_count"]
#     return (terms_count if terms_count != 0 else 1000)
    # for book_doc in book_docs:
        
    #     if terms_count ==0:
    #         print(f"Term counts for book {book_id} is {terms_count}")
    #         return 1000
    #     return terms_count



# This function is responsible for taking a dictionary of the form
# term : {doc_id : score}
# Documents could either be books or quotes in this function
# Find all documents that are common among all search terms given
def get_scaled_common_documents(scored_docs_per_term):
    common_docs = set()
    tfidf_scores = {}
    scored_docs = {}
    print("scored_docs_per_term", scored_docs_per_term)

    terms = scored_docs_per_term.keys()
    num_terms = len(terms)

    # While our term list is not empty
    while(len(terms)):
        # Iterate the books for the selected terms 
        for i,term in enumerate(terms):
            doc_scores = scored_docs_per_term[term]
            print(f"Term {term} has {len(doc_scores)} books")
            if i ==0:
                common_docs = set(doc_scores.keys())
                # print(f"Common docs for term {term} are currently {len(common_docs)} ")
                tfidf_scores[term] = Counter(doc_scores).most_common(1)[0][1]
                print(f"Highest tfidf score for term {term} is {tfidf_scores[term]}")
            else:
                # Get the intersection of all quote_id or book_id between the terms of the query
                common_docs = common_docs.intersection(set(doc_scores.keys()))
                # print(f"Common docs for term {term}  are currently {len(common_docs)} ")
                tfidf_scores[term] = Counter(doc_scores).most_common(1)[0][1]
                print(f"Highest tfidf score for term {term} is {tfidf_scores[term]}")


        if len(common_docs) == 0:
            print("No common docs")
            terms = [term for term,score in Counter(tfidf_scores).most_common()]
            print("Terms sorted",str(terms))
            lowest_tfidf_term = terms.pop()
            del tfidf_scores[lowest_tfidf_term]
            print("Terms after removing last",str(terms))
        else:
            print("Common docs",common_docs)
            for term, doc_scores in scored_docs_per_term.items():
                for doc_id, score in doc_scores.items():
                    if doc_id in common_docs:
                        scored_docs[doc_id] = score if doc_id not in scored_docs else scored_docs[doc_id] + score


            print("scored quotes",scored_docs)
            return scored_docs


def tfidf(book_id, book_term_freq,book_title_length, term_book_count):
    """ 
    Calculate
    TF(t) = (Number of times term t appears in a document) / (Total number of terms in the document).
    IDF(t) = log_e(Total number of documents / Number of documents with term t in it).
    """
    tf = float(book_term_freq) / book_title_length
    idf = math.log(float(TOTAL_NUMBER_OF_BOOKS) / term_book_count)

    return tf * idf

def ranked_book_search(query_params): #, number_results # what is the number_results used for
    tracker = book_ranking_query_TFIDF(query_params)
    return tracker

def book_ranking_query_TFIDF(query_params):
    scored_books_per_term = {} 
    original_terms = query_params['query']
    synonyms  = [] #query_params['synonyms']
    terms = original_terms + synonyms

    relevant_books = None
    if any([query_params['author'], query_params['bookTitle'], (query_params['genre'] != 'All' and query_params['genre'] != ''),
            int(query_params['min_rating']) > 1, int(query_params['yearTo']) != 2021, int(query_params['yearFrom']) != 1990]):
        adv_time = time.time()
        relevant_books = db.get_filtered_books_by_adv_search(query_params)
        print("time taken for adv search: {}".format(time.time() - adv_time))
    start_time = time.time()


    for term in terms:
        scored_books_per_term[term] = {}

        print("Term for book search",term)

        term_docs = db.get_books_by_term(term)
        print("Index entries ",term_docs.count())
        # Since only one index entry per term
        try:
            term_doc = term_docs.next()
        except StopIteration:
            continue
        
        # print(term_doc)

        # number of documents containing the term
        # documents in this case are the book_titles, or books

        doc_nums_term = term_doc['term_freq'] 
        
        for book in term_doc['books']:
            # print("Book id",book['_id'])
            # print("Book term frequency",book['term_freq_in_book'])
            book_id = book['_id']
            if relevant_books is None or book_id in relevant_books:
                book_title_term_freq = book['term_freq_in_book_title']
                book_title_length = book['title_len']
                score = tfidf(book_id,book_title_term_freq,book_title_length,doc_nums_term)

                if book_id in scored_books_per_term[term] :
                    scored_books_per_term[term][book_id] += score
                else:
                    scored_books_per_term[term][book_id] = score
       
        if len(scored_books_per_term[term].keys()) == 0:
            print(f"term {term} had 0 books")
            del scored_books_per_term[term]

        # Time control
        if time.time() - start_time > MAX_QUERY_TIME:
            break
    
    scored_books = get_scaled_common_documents(scored_books_per_term)
    
    return Counter(scored_books).most_common(100)



# ------------------- Quote search and ranking --------------------------
# -----------------------------------------------------------------------

MAX_INDEX_SPLITS = 200  # maximum number of different entries in the inverted_index with the same term
TOTAL_NUMBER_OF_SENTENCES = 4099986 
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
    if any([query_params['author'], query_params['bookTitle'], (query_params['genre'] != 'All' and query_params['genre'] != ''),
            int(query_params['min_rating']) > 1, int(query_params['yearTo']) != 2021, int(query_params['yearFrom']) != 1990]):
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
                    book_loop_time = time.time()
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
                            if time.time() - total_start_time > MAX_QUERY_TIME or len(scored_quotes_per_term[term].keys()) > 2000: # Brings time for hello from 7s to 0.3s
                                scored_quotes = get_common_documents(scored_quotes_per_term)
                                return Counter(scored_quotes).most_common(100)
        except:
            pass
    
    scored_quotes = get_common_documents(scored_quotes_per_term)

    return Counter(scored_quotes).most_common(100)


def score_BM25(doc_nums, doc_nums_term, term_freq, k1, b, dl, avgdl):
    """ Source for BM25: https://en.wikipedia.org/wiki/Okapi_BM25 """
    K =  k1 * ((1-b) + b * (float(dl)/float(avgdl)) )
    idf_param = math.log( (doc_nums-doc_nums_term+0.5) / (doc_nums_term+0.5) )
    next_param = ((k1 + 1) * term_freq) / (K + term_freq)
    return float("{0:.4f}".format(next_param * idf_param))


# ------------------- Phrase search and ranking --------------------------
# ------------------------------------------------------------------------
def quote_phrase_search(query):
    start_time = time.time()
    tracker = phrase_search_2(query)
    end_time = time.time()
    print("time taken to return {} results".format(len(tracker)), end_time - start_time)
    return tracker

def phrase_search_2(query_params):
    MAX_TO_BE_EXAMINED = 10000
    start_time = time.time()
    stopSet = set(stopwords.words('english'))
    results = list()
    terms_with_pos = query_params['query'] # tuple (term, [pos])
    all_terms = query_params['all_terms'] 
    start_time = time.time()
    root = ""
    rootPos = 0
    distancesDict = dict() # offset --> term | e.g. "wind and rain", wind is root and is at 0, so {1: and, 2: rain}

    # Assign root
    for tup in terms_with_pos:
        if tup[0] not in stopSet:
            root = tup[0]
            rootPos = tup[1][0]
            break

    # Compute distance offsets of other term occurences to root
    for tup in terms_with_pos:
            for idx in tup[1]:
                offset = idx - rootPos 
                term = tup[0]
                distancesDict[offset] = term 

    # Get all invertedIndex docs of the root term
    rootDocs = list(db.get_docs_by_term(root, 0, 100, sort=True))

    # Get books and quotes containing all non-stop terms
    booksContainingQuotesContainingAllNonStopWords = set()
    quotesContainingAllNonStopWords = set()
    for doc in rootDocs:
        for book in doc["books"]:
            for quote in book["quotes"]:
                booksContainingQuotesContainingAllNonStopWords.add(book["_id"])
                quotesContainingAllNonStopWords.add(quote["_id"])
    for tup in terms_with_pos:
        if tup[0] not in stopSet and tup[0] != root:
            term = tup[0]
            termDocs = list(db.get_docs_by_term(term, 0, 100, sort=True))
            bookSet = set()
            quoteSet = set()
            for doc in termDocs:
                for book in doc["books"]:
                    for quote in book["quotes"]:
                        bookSet.add(book["_id"])
                        quoteSet.add(quote["_id"])
            booksContainingQuotesContainingAllNonStopWords.intersection(bookSet)
            quotesContainingAllNonStopWords.intersection(quoteSet)
            termDocs=list()
            gc.collect()

    # Make dict of quote id to quote obj for faster retrieval in the next nested loop
    # Note: we limit the number of quotes to be examined for being a full match to MAX_TO_BE_EXAMINED
    dictOfQuoteIDToQuoteObj = dict()
    lengthOfQuotesSet = len(quotesContainingAllNonStopWords) - 1
    listOfQuoteObjects = db.get_quotes_by_quote_id_list(list(quotesContainingAllNonStopWords)[0:min(MAX_TO_BE_EXAMINED, lengthOfQuotesSet)])
    print(time.time() - start_time)
    for QuoteObj in listOfQuoteObjects:
        dictOfQuoteIDToQuoteObj[QuoteObj["_id"]] = QuoteObj
    print(time.time() - start_time)
    listOfQuoteObjects = list()
    gc.collect()

    quoteIDsOfQuotesContainingPhrase = set()  # i.e the result
    for doc in rootDocs:
        for book in doc["books"]:
            if (book["_id"] not in booksContainingQuotesContainingAllNonStopWords):
                continue
            for quoteIndexObj in book["quotes"]:
                if (quoteIndexObj["_id"] not in quotesContainingAllNonStopWords) or quoteIndexObj["_id"] not in dictOfQuoteIDToQuoteObj:
                    continue
                quote = dictOfQuoteIDToQuoteObj[quoteIndexObj["_id"]]
                regexForPos = re.compile("[\s.,;'\"\(\)\[\]]")
                termsSplit = regexForPos.split(quote["quote"].lower())
                foundPhrase = True
                for idx in quoteIndexObj["pos"]:
                    for offset in distancesDict.keys():
                        if (idx + offset >= 0) and (idx + offset < len(termsSplit)) and distancesDict[offset] == termsSplit[idx + offset]:
                            continue
                        else:
                            foundPhrase = False 
                            break
                    if foundPhrase == True:
                        quoteIDsOfQuotesContainingPhrase.add(quoteIndexObj["_id"])
                        break
                    else:
                        foundPhrase = True

    return list(quoteIDsOfQuotesContainingPhrase)


        

def phrase_search(query_params): 
    results = set()
    terms_with_pos = query_params['query'] # tuple (term, pos_in_all_terms)
    all_terms = query_params['all_terms'] 
    start_time = time.time()

    # e.g. wind and rain => [(wind, 0), (rain, 2)]
    for i in range(1, len(terms_with_pos)):
        intermediate_counter = Counter() # 
        intermediate_set = set()
        # doing phrase search for pair of terms in phrase (so 1st,2nd / 1st,3rd / 1st,4th etc.)
        documents_1 = db.get_docs_by_term(terms_with_pos[0][0], 0, 100, sort=True) # get documents for first term
        documents_2 = db.get_docs_by_term(terms_with_pos[i][0], 0, 100, sort=True)
        # if documents_1.count() == 0 or documents_2.count() == 0:
        #     print("one of the documents returned none")
        #     break
        diff = terms_with_pos[i][1] - terms_with_pos[0][1] 
        stop_word_check = True if diff != i else False
        #print("stop_word_check: {}".format(stop_word_check))
        #print("diff considered now: {}".format(diff))

        test_time = time.time()
        doc_1 = next(documents_1, None)
        doc_2 = next(documents_2, None)
        #print("time taken for this weird thing: {}".format(time.time() - test_time))

        # track the position of each book in the book arrays
        book_pos_1 = 0 
        book_pos_2 = 0

        # track position of quote in quote arrays
        quote_pos_1 = 0
        quote_pos_2 = 0
        break_doc_loop = False
        doc_time = time.time()

        while doc_1 is not None and doc_2 is not None: 
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
            
            #print("time for book loop: {}".format(time.time() - book_loop_time))
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
                
                #print("time for quote loop: {}".format(time.time() - quote_loop_time))
                # print("quote_1_id is: {}".format(doc_1['books'][book_pos_1]['quotes'][quote_pos_1]['_id']))
                # print("quote_2_id is: {}".format(doc_2['books'][book_pos_2]['quotes'][quote_pos_2]['_id']))

                if not break_doc_loop and doc_1['books'][book_pos_1]['quotes'][quote_pos_1]['_id'] == doc_2['books'][book_pos_2]['quotes'][quote_pos_2]['_id']:
                    # print("FOUND EQUAL QUOTE ID: {}".format(doc_1['books'][book_pos_1]['quotes'][quote_pos_1]['_id']))
                    find_pos_time = time.time()
                    
                    pos_1_list = doc_1['books'][book_pos_1]['quotes'][quote_pos_1]['pos']
                    pos_2_list = doc_2['books'][book_pos_2]['quotes'][quote_pos_2]['pos']
                    # rain - wind

                    add_to_set = False
                    for (x1, x2) in zip(pos_2_list, pos_1_list):
                        if int(x1) - int(x2) == diff:
                            if not stop_word_check:
                                add_to_set = True
                            if doc_1['books'][book_pos_1]['quotes'][quote_pos_1]['_id'] in intermediate_counter:
                                intermediate_counter[doc_1['books'][book_pos_1]['quotes'][quote_pos_1]['_id']].append((x2, x1))
                            else:
                                intermediate_counter[doc_1['books'][book_pos_1]['quotes'][quote_pos_1]['_id']] = [(x2, x1)]
                    if add_to_set:
                        intermediate_set.add(doc_1['books'][book_pos_1]['quotes'][quote_pos_1]['_id'])
                        
                    # this checks if it's a phrase occurring in the common book + common quote
                    # if pos_check.get(diff) is not None:
                    #     # takes into account stop words in between - check if stop words match up with whats in quote
                    #     if stop_word_check:
                            # intermediate_counter[doc_1['books'][book_pos_1]['quotes'][quote_pos_1]['_id']] = pos_check[diff]
                            # quote = db.get_quote_from_id(doc_1['books'][book_pos_1]['quotes'][quote_pos_1]['_id'])
                            # add_to_intermediate = True

                            # # for each stop word in between
                            # # [wind, and, stop, words, rain]
                            # for j in range(1, diff):
                            #     stop_word = all_terms[terms_with_pos[0][1] + j]
                            #     print("stop word is {}".format(stop_word))
                            #     # get the positions in the quote
                            #     stop_word_pos = [index+1 for (index, token) in enumerate(re.findall(r'\w+',quote['quote'])) if token == stop_word]
                            #     print("stop_word_pos: {}".format(stop_word_pos))
                            #     print("pos_1_list: {}".format(pos_1_list))
                            #     if j not in [int(x1) - int(x2) for (x1, x2) in zip(stop_word_pos, pos_1_list)]:
                            #         add_to_intermediate = False
                            #         break

                            # if add_to_intermediate:
                            #     intermediate.add(doc_1['books'][book_pos_1]['quotes'][quote_pos_1]['_id'])
                        # else:
                            # intermediate_set.add(doc_1['books'][book_pos_1]['quotes'][quote_pos_1]['_id'])
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
                            
                    #print("time spent finding position in quote: {}".format(time.time() - find_pos_time))
                    
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

            if break_doc_loop or time.time() - doc_time > 10:
                # print("one of the previous while loops set break_doc_loop to true, break")
                break
                

        # for each pair of terms (e.g. 1st,2nd), intersect with what has been found so far
        # e.g. 1st,2nd returns a certain intermediate set of quote ids (containing pos diff 1 for 1st,2nd terms)
        # 1st,3rd returns a certain intermediate set of quote ids, (containing pos diff 2 for 1st,3rd terms)
        # we want intersection of the two to ensure quotes returned contains phrase 1st,2nd,3rd
        # intermediate_counter: {quote_id: [(pos_1, pos_2), (pos_1, pos_2)]} where pos_2 - pos_1 = diff
        if len(intermediate_set) != 0 or len(intermediate_counter) != 0:
            chk_time = time.time()
            if len(intermediate_counter) != 0:
                quote_ids = list(intermediate_counter.keys())
                quotes = db.get_quotes_by_quote_id_list(quote_ids)
                regexForPos = re.compile("[\s.,;'\"\(\)\[\]]")
                
                for quote_obj in quotes:
                    quote_id = quote_obj['_id']
                    quote = quote_obj['quote']
                    terms_split = regexForPos.split(quote.lower())
                    # print("terms_split: {}".format(terms_split))

                    # 
                    for (pos_1, pos_2) in intermediate_counter[quote_id]:
                        check = False
                        for j in range(1, diff):
                            stop_word = all_terms[terms_with_pos[0][1] + j]
                            # print("terms_split[{}] for pos_1: {}".format(pos_1 + j, terms_split[pos_1 + j]))
                            # print("terms_split[{}] for pos_2: {}".format(pos_2 - (diff - j), terms_split[pos_2 - (diff - j)]))
                            # print()
                            if terms_split[pos_1 + j] == stop_word and terms_split[pos_2 - (diff - j)] == stop_word:
                                check = True
                            else:
                                check = False
                                break
                        if check:
                            intermediate_set.add(quote_id)
                            break
            #print("time taken for this: {}".format(time.time() - chk_time))
            #print('intermediate set is {}'.format(intermediate_set))
            if len(intermediate_set) != 0:
                # print("intermediate is: {}".format(intermediate_set))
                if len(results) == 0:
                    results = intermediate_set
                else:
                    # comm_keys = set(results.keys()).intersection(intermediate.keys())
                    results = results.intersection(intermediate_set)
            # print("doc time: {}".format(time.time() - doc_time))
        
        else:
            # print("none of this phrase found")
            results = set()
            break   
    
    # print("results are: {}".format(results))
    return list(results)[:100]
    
# if __name__ == '__main__':
    # populate_time = time.time()
    # populate_terms_count_dictionary()
    # print("populated dictionary and took {} time".format(time.time() - populate_time))
    # print()

    # query_params = {"query": ['develop', 'talent'], "author": "", 'bookTitle': '', 'genre': "", 'min_rating': 5, "yearFrom": '1998', "yearTo": '2020'}
    # query_params = {"query": ['wind', 'and', 'rain']}
    # start = time.time()
    # # tracker = ranking_query_BM25(query_params)
    # tracker = phrase_search(query_params)
    # # tracker = book_ranking_query_TFIDF(query_params)
    # print(tracker)
    # print("time taken: {}".format(time.time() - start))
