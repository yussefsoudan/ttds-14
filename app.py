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

#db = MongoDB()
#stopSet = set(stopwords.words('english'))
#stemmer = PorterStemmer()
#spell = SpellChecker()

# def merge_dict_lists (l1,l2,key):
#     merged = l1
#     for n, item1 in enumerate(l1):
#         for item2 in l2:
#             if item1[key] == item2[key]:
#                 merged[n].update(item2)
#     return merged


# def preprocess(quote):
#     terms = [stemmer.stem(token.lower()) for token in re.findall(r'\w+',quote) if not token.lower() in stopSet]
#     return terms

@app.route('/')
def serve():
    print("SERVING....")
    return send_from_directory(app.static_folder,'index.html')


# @app.route('/spellcheck', methods=['POST'])
# def get_most_likely_terms():
#     print("Spell-checking: ", request.get_json())
#     search_text = request.get_json()["search_text"]
#     terms = re.findall(r'\w+', search_text)
#     correction_exists = False
#     corrected_text = ""
#     for term in terms:
#         correction = spell.correction(term)
#         if (correction != term):
#             correction_exists = True
#             corrected_text = search_text.replace(term, correction)
    
#     result = {}
#     result['corrected_text'] = corrected_text
#     result['correction_exists'] = correction_exists
#     return result


# @app.route('/get_all_authors', methods=['POST'])
# def get_all_authors():
#     print("Finding all author names")
#     authors = db.get_all_authors()
#     print("Authors: ", authors)
#     return {"authors": authors}


# @app.route('/get_all_book_titles', methods=['POST'])
# def get_all_book_titles():
#     print("Finding all book titles")
#     book_titles = db.get_all_book_titles()
#     print("Book titles: ", book_titles)
#     return {"book_titles": book_titles}


# @app.route('/quote_from_id', methods=['POST'])
# def get_quote_from_quote_id():
#     print("Request.get_json ", request.get_json())
#     quote_id = request.get_json()["_id"]
#     result = db.get_quote_from_id(quote_id)
#     print("FROM app.py ", result)
#     return result

# # this tries out ranked_book_search function from ranking.py
# @app.route('/books_search', methods=['POST'])
# def get_books_from_terms():
#     print("request in get_books_from_terms is {}".format(request.get_json()))
#     details = request.get_json()

#     # Preprocess the quote 
#     preprocessed_terms = preprocess(details["quote"])
#     print("preprocessed terms",preprocessed_terms)

#     ranked_books = ranked_book_search({"query":preprocessed_terms, "author": details["author"], "bookTitle": details["bookTitle"],
#                                        "genre": details["genre"], "yearTo": str(details["yearTo"]), "yearFrom": str(details["yearFrom"]),
#                                        'min_rating': details['minRating']}) # ranked_book_search returns list: [(book_id, score)]
#     print("ranked books: {}".format(ranked_books))

#     # if we want book info apart from the book_ids we need to do another search - would this make sense?
#     ranked_book_ids = [i[0] for i in ranked_books]
#     book_results = db.get_books_by_book_id_list(ranked_book_ids)

#     for dic_book in book_results:
#         if dic_book is not None and 'book_id' not in dic_book:  # book_id may already be added if different quotes share the same book!
#             dic_book['book_id'] = dic_book.pop('_id')
    
#     # Responsibility of front end to determine that this object will not contain
#     # quotes and just displaying the requested quote
#     # Add the preprocessed terms for highlight
#     result = {"books": book_results, "searchTerms":preprocessed_terms}
#     print('-'*50)
#     print("returning {} from get_books_from_terms".format(result))
#     return result

# # this tries out ranked_quote_retrieval function from ranking.py
# # In this function, both simple quote search and phrase search will be handled
# @app.route('/quotes_search', methods=['POST'])
# def get_quotes_from_terms():
#     print("request in get_quotes_from_terms is {}".format(request.get_json()))
#     details = request.get_json()

#     # quote contains character " twice and they are at the beginning / end of the quote => phrase search is true
#     phrase_search = False
#     char_pos = [char.start() for char in re.finditer('"', details['quote'])]
#     if len(char_pos) == 2:
#         if char_pos[0] == 0 and char_pos[1] == len(details['quote']) - 1:
#             phrase_search = True

#     # Preprocess the quote
#     preprocessed_terms = preprocess(details["quote"])
#     print("preprocessed terms",preprocessed_terms)

#     if phrase_search:
#         ranked_quote_ids = list(quote_phrase_search({"query": preprocessed_terms})) # phrase search returns set(quote_ids)
#     else:
#         ranked_quotes = ranked_quote_retrieval({"query": preprocessed_terms, "author": details["author"], "bookTitle": details["bookTitle"],
#                                             "genre": details["genre"], "yearTo": str(details["yearTo"]), "yearFrom": str(details["yearFrom"]),
#                                            'min_rating': details['minRating']}) # ranked_quote_search returns list: [(quote_id, score)]
#         print("ranked quotes: {}".format(ranked_quotes))
#         ranked_quote_ids = [i[0] for i in ranked_quotes]

#     quotes_results = db.get_quotes_by_quote_id_list(ranked_quote_ids)
    
#     for i, dic_quote in enumerate(quotes_results):
#         dic_quote['quote_id'] = dic_quote.pop('_id')
    
#     # Get book Details for book_ids
#     book_ids = ([dic['book_id'] for dic in quotes_results])
#     books = db.get_books_by_book_id_list(book_ids)
#     for dic_book in books:
#         if dic_book is not None and 'book_id' not in dic_book:
#             dic_book['book_id'] = dic_book.pop('_id')

#     # Merge book Details with Quotes
#     # Appending the book details to the quotes object
#     query_results = merge_dict_lists(quotes_results, books, 'book_id')


#     result = {"books": query_results,"searchTerms":preprocessed_terms}

#     # print("returning {} from get_quotes_from_terms".format(result))
#     return result


if __name__ == '__main__':
    app.run(host='0.0.0.0')
