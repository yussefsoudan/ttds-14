from pymongo import MongoClient
from typing import List
import time

class MongoDB:
    def __init__(self):
        super().__init__()
        client = MongoClient("mongodb://188.166.173.191:27017") # mongodb://localhost:27017/
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

    def get_docs_by_term(self, term: str, skip: int, limit: int = 1000, sort: bool = False):
        docs_for_term = self.inverted_index.find({"term": term}, {"_id": 0})
        if sort:
            docs_for_term = docs_for_term.sort('books.0._id')
        docs_for_term = docs_for_term.skip(skip).limit(limit)
        return docs_for_term
    
    # def get_books_by_term(self, term: str):
    #     return self.inverted_index.aggregate([
    #         { "$project": { "books": { "$objectToArray": "$books" } } },
    #         { "$project": { "books.v.quotes": 0} }, 
    #         { "$project": { "books": { "$arrayToObject": "$books" } } }, 
    #         { "$match": {"_id": term } } ])


if __name__ == '__main__':
    db = MongoDB()
    cursor = db.get_docs_by_term("grand", 0, sort=True)
    print(list(next(cursor, None)))
    # start = time.time()
    # for (index, found) in enumerate(list(db.get_docs_by_term("grand", 0, sort=True))):
    #     print("element no. {}".format(index))
    #     books = found["books"]
    #     book_ids = [i['_id'] for i in books]
    #     print("number of books here: {}".format(len(books)))
    #     print("this book_ids list has minimum {} and maximum {}".format(min(book_ids), max(book_ids)))
    #     print()

    # print("time taken: {}".format(time.time() - start))