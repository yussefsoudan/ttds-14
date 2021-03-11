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

# ------------------- Book search and ranking --------------------------
# -----------------------------------------------------------------------

TOTAL_NUMBER_OF_BOOKS = 13
MAX_QUERY_TIME = 10  # max seconds to allow the query to run for


# Dictionary containing for each book, the total number of terms 
# TO-DO: Write script to iterate over books and create a pickle file
# containing their term count
books_term_counts = defaultdict(lambda: 1)
pickle_path = Path(__file__).parent.absolute() / "utils" / 'books_term_counts.p'

if os.path.isfile(pickle_path):
    movie_term_counts = defaultdict(lambda: 1, pickle.load(open(pickle_path, 'rb')))
    TOTAL_NUMBER_OF_MOVIES = len(movie_term_counts)
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
        # it might return multiple Cursor objects 
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
                # returns cursor object
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
# -----------------------------------------------------------------------



if __name__ == '__main__':

    db = MongoDB()
    batch_size = 50

    # start = time.time()
    # # query_params = {'query': ["father"]} #, "boy", "girl"]}
    # query_params = {'query': ["luke", "father"]}
    # # query_params['movie_title'] = ''
    # # query_params['year'] = ''
    # # query_params['actor'] = ''

    # tracker = ranking_query_BM25(query_params, batch_size)
    # end = time.time()
    # print("Time",end-start)
    # pprint.pprint(tracker)


    # for quote_id,score in tracker:
    #     quote = db.get_quotes_id(quote_id)
    #     print(quote['quote'])
    #     print('-'*10)


    query_params = {'query': ["luke", "father"], 'movie_title': '', 'year': '', 'actor': ''}
    start = time.time()
    tracker = book_ranking_query_TFIDF(query_params)
    end = time.time()
    print(end-start)
    print(tracker)



    # # query_params = {"year": "2000-2001"}
    # query_params = {"year": "1980-1981", 'query': ["luke", "father"], 'movie_title': '', 'actor': ''}
    # query_params['query'] = ["may"]
    # query_params['movie_title'] = ''
    # query_params['actor'] = ''
    # start = time.time()
    # tracker = ranking_query_BM25(query_params, batch_size)
    # end = time.time()
    # print(end-start)
    # print(tracker.get_top(10))
