from flask import Flask, request, send_from_directory
from flask_cors import CORS
import json
import re
import time
from MongoDB import MongoDB 
from ranking import *
import os
from nltk.corpus import stopwords
import nltk 
nltk.download('stopwords')
from nltk.stem.porter import *
from spellchecker import SpellChecker

app = Flask(__name__, static_url_path = '', static_folder="website/book-search-client/build")
CORS(app)

db = MongoDB()
stopSet = set(stopwords.words('english'))
stemmer = PorterStemmer()
spell = SpellChecker()


def merge_dict_lists(l1,l2,key):
    merged = l1
    for n, item1 in enumerate(l1):
        for item2 in l2:
            if item1[key] == item2[key]:
                merged[n].update(item2)
    return merged


def preprocess(quote, remove_stop_words=True):
    if not remove_stop_words:
        return [stemmer.stem(token.lower()) for token in re.findall(r'\w+',quote)]
    terms = [stemmer.stem(token.lower()) for token in re.findall(r'\w+',quote) if not token.lower() in stopSet]
    return terms


@app.route('/')
def serve():
    print("SERVING....")
    return "Server is working."


@app.route('/spellcheck', methods=['POST'])
def get_most_likely_terms():
    print("Spell-checking: ", request.get_json())
    search_text = request.get_json()["search_text"]
    terms = re.findall(r'\w+', search_text)
    correction_exists = False
    corrected_text = ""
    for term in terms:
        correction = spell.correction(term)
        if (correction != term):
            correction_exists = True
            corrected_text = search_text.replace(term, correction)
    
    result = {}
    result['corrected_text'] = corrected_text
    result['correction_exists'] = correction_exists
    return result


@app.route('/get_all_authors', methods=['POST'])
def get_all_authors():
    print("Finding all author names")
    authors = db.get_all_authors()
    # print("Authors: ", authors)
    return {"authors": authors}


@app.route('/get_all_book_titles', methods=['POST'])
def get_all_book_titles():
    print("Finding all book titles")
    book_titles = db.get_all_book_titles()
    # print("Book titles: ", book_titles)
    return {"book_titles": book_titles}


@app.route('/quote_from_id', methods=['POST'])
def get_quote_from_quote_id():
    print("Request.get_json ", request.get_json())
    quote_id = request.get_json()["_id"]
    result = db.get_quote_from_id(quote_id)
    print("FROM app.py ", result)
    return result

@app.route('/books_search', methods=['POST'])
def get_books_from_terms():
    print("request in get_books_from_terms is {}".format(request.get_json()))
    details = request.get_json()

    # Preprocess the quote 
    preprocessed_terms = preprocess(details["quote"])
    print("preprocessed terms",preprocessed_terms)

    ranked_books = book_search_TFIDF({"query":preprocessed_terms, "author": details["author"], "bookTitle": details["bookTitle"],
                                       "genre": details["genre"], "yearTo": str(details["yearTo"]), "yearFrom": str(details["yearFrom"]),
                                       'min_rating': details['minRating']})
    # print("ranked books: {}".format(ranked_books))

    # Get book information
    ranked_book_ids = [i[0] for i in ranked_books]
    books = db.get_books_by_book_id_list(ranked_book_ids) # returns cursor

    # Traverse cursor and store documents to list
    books_list = []
    for book in books:
        book['book_id'] = book.pop('_id')
        books_list.append(book)

    result = {"books": books_list, "searchTerms":preprocessed_terms}
    print('-'*50)
    return result

# This function handle both quote and phrase search 
@app.route('/quotes_search', methods=['POST'])
def get_quotes_from_terms(): 
    print("request in get_quotes_from_terms is {}".format(request.get_json()))
    details = request.get_json()
    
    # quote contains character " twice and they are at the beginning / end of the quote => phrase search is true
    phrase_search = False
    char_pos = [char.start() for char in re.finditer('"', details['quote'].strip())]
    if len(char_pos) == 2:
        if char_pos[0] == 0 and char_pos[1] == len(details['quote']) - 1:
            phrase_search = True

    preprocessed_terms = preprocess(details["quote"])
    print("preprocessed terms",preprocessed_terms)

    if phrase_search:
        all_terms = preprocess(details['quote'], remove_stop_words=False)
        print(all_terms)
        phrase_terms = []
        for term in all_terms:
            pos_of_term = [i for i, split in enumerate(all_terms) if term in split]
            phrase_terms.append((term, pos_of_term))
 
        start_time = time.time()
        ranked_quote_ids = quote_phrase_search({"query": phrase_terms, "all_terms" : all_terms}) # phrase search returns set(quote_ids)
        end_time = time.time()
        print("time taken to return {} results".format(len(ranked_quote_ids)), end_time - start_time)
    
    else:
        q_r_time = time.time()
        ranked_quotes = quote_search_BM25({"query": preprocessed_terms, "author": details["author"], "bookTitle": details["bookTitle"],
                                            "genre": details["genre"], "yearTo": str(details["yearTo"]), "yearFrom": str(details["yearFrom"]),
                                           'min_rating': details['minRating']}) 
        print()
        # print("ranked quotes: {}".format(ranked_quotes))
        print("time taken for ranked_quote_retrieval: {}".format(time.time() - q_r_time))
        print()
        ranked_quote_ids = [i[0] for i in ranked_quotes]

    quotes = db.get_quotes_by_quote_id_list(ranked_quote_ids)
    
    # Traverse cursor
    quotes_results = []
    for quote in quotes:
        quote['quote_id'] = quote.pop('_id')
        quotes_results.append(quote)
    
    # Get book Details for book_ids
    book_ids = [quote['book_id'] for quote in quotes_results]
    books = db.get_books_by_book_id_list(book_ids)
    books_results = []
    for book in books:
        if book is not None and 'book_id' not in book: # in case different quotes shared the same book
            book['book_id'] = book.pop('_id')
            books_results.append(book)

    # Merge book Details with Quotes
    # Appending the book details to the quotes object
    query_results = merge_dict_lists(quotes_results, books_results, 'book_id')

    result = {"books": query_results,"searchTerms":preprocessed_terms}

    return result

if __name__ == '__main__':    
    app.run(host='0.0.0.0')
