from pymongo import MongoClient
from typing import List

class MongoDB:
    def __init__(self):
        super().__init__()
        client = MongoClient("mongodb://localhost:27017/")
        db = client["TTDS"]
        self.books = db["books"]
        self.quotes = db["quotes"]
        self.inverted_index = db["invertedIndex"] # carefull, might be named inverted_index in your db
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
        books = list(self.books.find({"_id": {"$in": book_ids}}))
        return books
    
    def get_quotes_by_quote_id_list(self, quote_ids: List[str]):
        quotes_obj = list(self.quotes.find({"_id": {"$in": quote_ids}}))
        # quotes = [quote["quote"] for quote in quotes_obj] 

        # need the entire object to retrieve the associated books later
        return quotes_obj

    def get_docs_by_term(self, term: str, skip: int, limit: int = 1000):
        docs_for_term = self.inverted_index.find({"_id": term})
        docs_for_term = docs_for_term.skip(skip).limit(limit)
        return docs_for_term
    
    def get_books_by_term(self, term: str):
        return self.inverted_index.aggregate([
            { "$project": { "books": { "$objectToArray": "$books" } } },
            { "$project": { "books.v.quotes": 0} }, 
            { "$project": { "books": { "$arrayToObject": "$books" } } }, 
            { "$match": {"_id": term } } ])