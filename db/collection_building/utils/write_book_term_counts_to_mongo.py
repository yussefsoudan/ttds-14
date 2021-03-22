import pickle
import pymongo

def updateDBWithTermCounts(): 
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["TTDS"]
    books = db["books"]
    filepath = "/root/book_term_counts.p"
    with open(filepath, 'rb') as handle:
        dictt = pickle.load(handle)
        for book_id in dictt:
            term_count = int(dictt[book_id])
            book_id = int(book_id)
            books.update_one({"_id" : book_id}, {"$set" : {"term_count" : term_count}})

updateDBWithTermCounts()