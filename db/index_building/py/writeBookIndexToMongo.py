import pymongo 
import gc 
import pickle
import os 

def write_index():
    DB_PASS='thenittygrittyofELnitty'
    DB_USER='readerTTDS'
    DB_NAME='TTDS' 
    DB_HOST='188.166.173.191'
    PORT = '27017'
    client = pymongo.MongoClient(f'mongodb://{DB_USER}:{DB_PASS}@{DB_HOST}:{PORT}') 
    db = client["TTDS"]
    books_inverted_index = db["bookInvertedIndex"]
    directory = "/root/bookIndex/"
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".pickle"): 
            path = directory + filename 
            if os.path.getsize(path) > 0:
                print("Processing " + path)
                with open(path, 'rb') as handle:
                    docs = pickle.load(handle)
                    if len(docs) > 3:
                        books_inverted_index.insert_many(docs)
                        docs.clear() 
                        gc.collect()
    inverted_index.create_index([("term", pymongo.ASCENDING)])
    inverted_index.create_index([("books._id", pymongo.ASCENDING)])

write_index()