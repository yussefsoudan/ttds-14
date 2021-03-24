import functools
import operator
from os import environ
from pymongo import MongoClient
from typing import List
import urllib.parse

class MongoDB:
    def __init__(self):
        super().__init__()
        DB_PASS='thenittygrittyofELnitty'
        DB_USER='readerTTDS'
        DB_NAME='TTDS' 
        DB_HOST='localhost'
        PORT = 27017
        client = MongoClient(f'mongodb://{DB_USER}:{DB_PASS}@{DB_HOST}:{PORT}') 
        db = client[DB_NAME]
        self.books = db["books"]
        self.quotes = db["quotes"]
        self.inverted_index = db["invertedIndex"] 
        # self.quotes.create_index('_id')

        # self.inverted_index = self.ttds.inverted_index
        # self.movies = self.ttds.movies
        # self.sentences.create_index('_id')
        # self.inverted_index.create_index('_id')
        # self.movies.create_index('_id')
        # self.inverted_index_gridfs = gridfs.GridFS(self.ttds)

    def get_quote_from_id(self, id: str):
        # Given a quote id, return the quote object
        quote = self.quotes.find_one({"_id": id})
        print("Quote returned from db ", quote)
        return quote

    def get_titles_by_book_id_list(self, book_ids: List[str]):
        books = list(self.books.find({"_id": {"$in": book_ids}}))
        book_titles = [book["title"] for book in books] # if return more than titles, modify this
        return book_titles

    def get_books_by_book_id_list(self, book_ids: List[str]):
        print("Book id lists:",str(book_ids))
        books = list(self.books.find({"_id": {"$in": book_ids}}))
        return books
    
    def get_quotes_by_quote_id_list(self, quote_ids: List[str]):
        quotes_obj = list(self.quotes.find({"_id": {"$in": quote_ids}}))
        # quotes = [quote["quote"] for quote in quotes_obj] 

        # need the entire object to retrieve the associated books later
        return quotes_obj

    def get_docs_by_term(self, term: str, skip: int, limit: int = 1000):
        print("Get documents by term")
        docs_for_term = self.inverted_index.find({"term": term})
        docs_for_term = docs_for_term.skip(skip).limit(limit)
        return docs_for_term
    
    def get_books_by_term(self, term: str):
        return self.inverted_index.find({"term": term}, {"books.quotes": 0})
        # return self.inverted_index.aggregate([
        #     { "$project": { "books": { "$objectToArray": "$books" } } },
        #     { "$project": { "books.v.quotes": 0} }, 
        #     { "$project": { "books": { "$arrayToObject": "$books" } } }, 
        #     { "$match": {"term": term } } ])

    def get_filtered_books_by_adv_search(self, query):
        adv_options = {}
        adv_options.update({"publishedDate": {'$lt': query["yearTo"], '$gte': query["yearFrom"]}})
        if query['author']:
            adv_options.update({'authors': query['author']})
        if query['bookTitle']:
            adv_options.update({'title': query['bookTitle']})
        if query['genre']:
            adv_options.update({'categories': query['genre']})
        if query['min_rating']:
            adv_options.update({"averageRating": {'$gte': query["min_rating"]}})
        print(adv_options)
        books = self.books.find(adv_options, {"_id": 1})
        book_ids = list(set([book['_id'] for book in list(books)]))
        return book_ids

    def get_all_authors(self):
        authors = self.books.find({}, {"authors": 1, "_id": 0})
        authors = [author["authors"] for author in authors]
        authors = functools.reduce(operator.iconcat, authors, [])
        author_names = [{"name": author} for author in sorted(list(set(authors)))]
        return author_names

    def get_all_book_titles(self):
        book_titles = self.books.find({}, {"title": 1, "_id": 0})
        book_titles = [title["title"] for title in book_titles]
        book_titles = [{"book_title": title} for title in sorted(list(set(book_titles)))]
        return book_titles
