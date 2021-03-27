import functools
import operator
from pymongo import MongoClient
from typing import List
import urllib.parse
from dotenv import load_dotenv
from os.path import join, dirname
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
import os

class MongoDB:
    def __init__(self):
        super().__init__()
        DB_PASS= os.environ.get("DB_PASS")
        DB_USER= os.environ.get("DB_USER")
        DB_NAME= os.environ.get("DB_NAME")
        DB_HOST= os.environ.get("DB_HOST")
        PORT = os.environ.get("PORT")
        client = MongoClient(f'mongodb://{DB_USER}:{DB_PASS}@{DB_HOST}:{PORT}') 
        db = client[DB_NAME]
        self.books = db["books"]
        self.quotes = db["quotes"]
        self.inverted_index = db["invertedIndex"] 
        self.book_inverted_index = db["bookInvertedIndex"]
        print("COUNT DOCS")
        print(db["invertedIndex"].count())

    def get_quote_from_id(self, id: str):
        # Given a quote id, return the quote object
        quote = self.quotes.find_one({"_id": id})
        #print("Quote returned from db ", quote)
        return quote

    def get_titles_by_book_id_list(self, book_ids: List[str]):
        books = self.books.find({"_id": {"$in": book_ids}})
        book_titles = [book["title"] for book in books] 
        return book_titles

    def get_books_by_book_id_list(self, book_ids: List[str]):
        print("Book id lists:",str(book_ids))
        books = self.books.find({"_id": {"$in": book_ids}})
        return books
    
    def get_quotes_by_quote_id_list(self, quote_ids: List[str]):
        # need the entire object to retrieve the associated books later
        return self.quotes.find({"_id": {"$in": quote_ids}})
    
    def get_docs_by_term_list(self, term_list: List[str]):
        return self.inverted_index.find({"term" : {"$in" : term_list}}) 

    def get_docs_by_term(self, term: str, skip: int, limit: int = 1000):
        print("Get documents by term")
        docs_for_term = self.inverted_index.find({"term": term}, batch_size=100)
        docs_for_term = docs_for_term.skip(skip).limit(limit)  
        return docs_for_term
    
    def get_books_by_term(self, term: str):
        return self.book_inverted_index.find({"term": term})

    def get_filtered_books_by_adv_search(self, query):
        adv_options = {}
        if int(query['yearTo']) != 2021 or int(query['yearFrom']) != 1990:
            adv_options.update({"publishedDate": {'$lt': query["yearTo"], '$gte': query["yearFrom"]}})
        if query['author']:
            adv_options.update({'authors': query['author']})
        if query['bookTitle']:
            adv_options.update({'title': query['bookTitle']})
        if query['genre'] != 'All' and query['genre'] != '':
            adv_options.update({'categories': query['genre']})
        if query['min_rating'] != 1:
            adv_options.update({'$or': [{'averageRating': {'$gte': query['min_rating']}}, {'averageRating': ""}]})
        print(adv_options)
        books = self.books.find(adv_options, {"_id": 1})
        book_ids = set([book['_id'] for book in books]) #list()
        print("adv search number or results:", len(book_ids))
        return book_ids

    def get_all_authors(self):
        authors = self.books.find({}, {"authors": 1, "_id": 0})
        authors = [author["authors"] for author in authors]
        authors = functools.reduce(operator.iconcat, authors, [])
        authors = list(filter(bool, authors))
        author_names = [{"name": author} for author in sorted(list(set(authors)))]
        return author_names

    def get_all_book_titles(self):
        book_titles = self.books.find({}, {"title": 1, "_id": 0})
        book_titles = [title["title"] for title in book_titles]
        book_titles = [{"book_title": title} for title in sorted(list(set(book_titles)))]
        return book_titles
