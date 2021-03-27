import os.path
import json
import sys
from MongoDB import MongoDB 
from pathlib import Path
import math
import time
import pymongo
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


def get_common_documents(scored_docs_per_term,greedy_approach=False):
    """  
    Helper function
    Responsible for taking a dictionary of the form
    {term : {doc_id : score}}
    Documents could either be book titles or quotes in this function
    Find all documents that are common among all search terms given
    If greedy approach is given, disregard one term every time no common docs are found and repeat 
    """
    common_docs = set()
    tfidf_scores = {}
    scored_docs = {}
    # print("scored_docs_per_term", scored_docs_per_term)

    terms = scored_docs_per_term.keys()
    num_terms = len(terms)
    print("Terms for common docs",terms)

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
            # used for quote search, when common documents among ALL search terms must be returned 
            if not greedy_approach:
                return {}
            terms = [term for term,score in Counter(tfidf_scores).most_common()]
            print("Terms sorted",str(terms))
            lowest_tfidf_term = terms.pop()
            del tfidf_scores[lowest_tfidf_term]
            print("Terms after removing last",str(terms))
        else:
            print("Common docs",len(common_docs))
            for term, doc_scores in scored_docs_per_term.items():
                for doc_id, score in doc_scores.items():
                    if doc_id in common_docs:
                        scored_docs[doc_id] = score if doc_id not in scored_docs else scored_docs[doc_id] + score


            print("scored quotes",len(scored_docs))
            return scored_docs

# ------------------- Book search and ranking --------------------------
# -----------------------------------------------------------------------

TOTAL_NUMBER_OF_BOOKS = 30630 
MAX_BOOK_SEARCH_TIME = 10  # max seconds to allow the book title query to run for


def tfidf(book_term_freq,book_title_length, term_book_count):
    """ 
    Calculate
    TF(t) = (Number of times term t appears in a document) / (Total number of terms in the document).
    IDF(t) = log_e(Total number of documents / Number of documents with term t in it).
    """
    tf = float(book_term_freq) / book_title_length
    idf = math.log(float(TOTAL_NUMBER_OF_BOOKS) / term_book_count)

    return tf * idf

def book_search_TFIDF(query_params):
    """ 
    Function responsbile for book search 
    Uses the TF-IDF score to rank book titles
    Search terms are used to match book titles 
    """

    scored_books_per_term = {} 
    terms = query_params['query']

    # Filtering
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

        term_docs = db.get_books_by_term(term) # cursor object
        print("Index entries ",term_docs.count())
        # Since only one index entry per term
        try:
            term_doc = term_docs.next()
        except StopIteration:
            continue

        # number of documents containing the term
        # documents in this case are the book_titles, or books
        doc_nums_term = term_doc['term_freq'] 
        
        for book in term_doc['books']:
            book_id = book['_id']
            if relevant_books is None or book_id in relevant_books:
                # Calculate the score for each book object 
                book_title_term_freq = book['term_freq_in_book_title']
                book_title_length = book['title_len']
                score = tfidf(book_title_term_freq,book_title_length,doc_nums_term)

                if book_id in scored_books_per_term[term] :
                    scored_books_per_term[term][book_id] += score
                else:
                    scored_books_per_term[term][book_id] = score
       
        if len(scored_books_per_term[term].keys()) == 0:
            print(f"term {term} had 0 books")
            # No need to be considered when finding common docs
            del scored_books_per_term[term]


        if time.time() - start_time > MAX_BOOK_SEARCH_TIME:
            print("Reach max book search time limit")
            break
    
    scored_books = get_common_documents(scored_books_per_term,greedy_approach=True)

    return Counter(scored_books).most_common(100)



# ------------------- Quote search and ranking --------------------------
# -----------------------------------------------------------------------

MAX_INDEX_ENTRIES_PER_TERM = 200  # maximum number of different entries in the inverted_index with the same term
TOTAL_QUOTES = 4099986  # total number of quotes in collection 
MAX_RETRIEVE_QUOTES_PER_TERM = 4000 # max quote documents retrieved per term 
MAX_QUOTE_SEARCH_TIME = 10  # max seconds to allow the query to run for
batch_size = 20


""" 
Helper error class 
"""
class MaxQuotesError(Exception): pass

def score_BM25(doc_nums, doc_nums_term, term_freq, k1, b, dl, avgdl):
    """ Source for BM25: https://en.wikipedia.org/wiki/Okapi_BM25 """
    K =  k1 * ((1-b) + b * (float(dl)/float(avgdl)) )
    idf_param = math.log( (doc_nums-doc_nums_term+0.5) / (doc_nums_term+0.5) )
    next_param = ((k1 + 1) * term_freq) / (K + term_freq)
    return float("{0:.4f}".format(next_param * idf_param))

def quote_search_BM25(query_params, batch_size=batch_size):

    """ 
    Function responsbile for quote search 
    Uses the BM25 score to rank quote as our quote documents are esentially paragraphs
    Search terms are used to match quotes, and only quotes that contain all the terms are returned
    """
    
    scored_quotes_per_term = {} # term -> {q_id:score}
    terms = query_params['query']
    relevant_books = None

    # Filtering 
    if any([query_params['author'], query_params['bookTitle'], (query_params['genre'] != 'All' and query_params['genre'] != ''),
            int(query_params['min_rating']) > 1, int(query_params['yearTo']) != 2021, int(query_params['yearFrom']) != 1990]):
        relevant_books = db.get_filtered_books_by_adv_search(query_params)
    
    print("Quote search terms",terms)

    doc_nums = TOTAL_QUOTES
    total_start_time = time.time()
    for term in terms:
        scored_quotes_per_term[term] = {}
        print("Term:",term)
        term_start_time = time.time()
        try:
            # iterate documents of this term by batches
            for i in range(0, MAX_INDEX_ENTRIES_PER_TERM, batch_size):
                print("Index batch=",i)
                term_docs = db.get_docs_by_term(term, i, batch_size)

                process_start = time.time()

                for term_doc in term_docs:

                    # number of documents containing the term
                    # documents in this case are the quotes
                    doc_nums_term = term_doc['term_freq'] 

                    book_loop_time = time.time()
                    for book in term_doc['books']:
                        if relevant_books is not None and book['_id'] not in relevant_books:
                            continue
                        for quote in book['quotes']:
                            # how many times the term appears in the quote
                            term_freq = len(quote['pos'])
                            # document length, how many terms appear overall in this quote
                            dl = quote['len']
                            quote_id = quote['_id']

                            # k 1 and b are free parameters, usually chosen, in absence of an advanced optimization, 
                            # as k 1 ∈ [ 1.2 , 2.0 ] and b = 0.75
                            # Wikipedia
                            score = score_BM25(doc_nums, doc_nums_term, term_freq, k1=1.2, b=0.75, dl=dl, avgdl=4.82)
                            
                            if score > 0:
                                if quote_id in scored_quotes_per_term[term]:
                                    scored_quotes_per_term[term][quote_id] += score
                                else:
                                    scored_quotes_per_term[term][quote_id] = score

                            # If we have retrieve MAX_TERM_QUOTES, move on to next term
                            if  len(scored_quotes_per_term[term].keys()) > MAX_RETRIEVE_QUOTES_PER_TERM: # Brings time for hello from 7s to 0.3s
                                print("MAX_RETRIEVE_QUOTES_PER_TERM has been reached")
                                raise   MaxQuotesError()
                            
                            if time.time() - total_start_time > MAX_QUOTE_SEARCH_TIME:
                                print("MAX_QUOTE_SEARCH_TIME has been reached")
                                scored_quotes = get_common_documents(scored_quotes_per_term)
                                return Counter(scored_quotes).most_common(100)
        
        except MaxQuotesError:
            pass
    
    scored_quotes = get_common_documents(scored_quotes_per_term,greedy_approach=False)

    return Counter(scored_quotes).most_common(100)

# ------------------- Phrase search and ranking --------------------------
# ------------------------------------------------------------------------

def quote_phrase_search(query_params):
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
