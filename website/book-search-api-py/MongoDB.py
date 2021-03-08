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


    def get_quotes_id(self, id: str):
        # Given a quote id, return the quote object
        quote = self.quotes.find_one({"_id": id})
        print("Quote list returned from db ", quote)

        return quote

    
    def get_docs_by_term(self, term: str, skip: int, limit: int = 1000):
        docs_for_term = self.inverted_index.find({"_id": term})
        docs_for_term = docs_for_term.skip(skip).limit(limit)
        return docs_for_term

    
    def get_books_by_term(self, term: str):
        return self.inverted_index.find({"_id": term}, {"books._id.quotes": 0}) # this doesnt remove the quotes 