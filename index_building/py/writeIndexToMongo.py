import pymongo 
import pickle
import os


def write_index():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["TTDS"]
    inverted_index = db["invertedIndex"]
    directory = "/root/index/"
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".pickle"): 
            path = directory + filename 
            if os.path.getsize(path) > 0:
                print("Processing " + path)
                with open(path, 'rb') as handle:
                    docs = pickle.load(handle)
                    if len(docs) > 3:
                        inverted_index.insert_many(docs)
    inverted_index.create_index([("term", pymongo.ASCENDING)])
    inverted_index.create_index([("books._id", pymongo.ASCENDING)])
    inverted_index.create_index([("books.quotes._id", pymongo.ASCENDING)])

write_index()
                

