from pymongo import MongoClient
from typing import List

class MongoDB:
    def __init__(self):
        super().__init__()
        client = MongoClient("mongodb://localhost:27017/")
        db = client["TTDS"]
        self.books = db["books"]
        self.quotes = db["quotes"]
        self.inverted_index = db["inverted_index"]
        # self.quotes.create_index('_id')

        # self.inverted_index = self.ttds.inverted_index
        # self.movies = self.ttds.movies
        # self.sentences.create_index('_id')
        # self.inverted_index.create_index('_id')
        # self.movies.create_index('_id')
        # self.inverted_index_gridfs = gridfs.GridFS(self.ttds)


    def get_quotes_by_list_of_quote_ids(self, id: str):
        # Given a list of quote ids, return a list of quote dictionaries, sorted in the same order that the ids are provided.
        print(id)
        quote = self.quotes.find_one({"_id": id})
        print("Quote list returned from db ",quote)
        # Sort results from mongodb by the ids list, since the order is not maintained
        # sorted_quote_dict = {d['_id']: d for d in quote_list}  # sentence_id -> sentence_dict
        # print("DIctionary ",sorted_quote_dict)
        # sorted_quote_list = [sorted_quote_dict[i] for i in ids]
        return quote