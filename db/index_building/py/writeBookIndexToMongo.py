import pymongo 
import gc 
import pickle
import os 
from dotenv import load_dotenv
from os.path import join, dirname
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
import os

def write_index():
    DB_PASS= os.environ.get("DB_PASS")
    DB_USER= os.environ.get("DB_USER")
    DB_NAME= os.environ.get("DB_NAME")
    DB_HOST= os.environ.get("DB_HOST")
    PORT = os.environ.get("PORT")
    client = pymongo.MongoClient(f'mongodb://{DB_USER}:{DB_PASS}@{DB_HOST}:{PORT}') 
    db = client["TTDS"]
    books_inverted_index = db["bookInvertedIndex"]
    directory = "/root/bookIndex/"
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".p"): 
            path = directory + filename 
            if os.path.getsize(path) > 0:
                print("Processing " + path)
                with open(path, 'rb') as handle:
                    docs = pickle.load(handle)
                    if len(docs) > 3:
                        books_inverted_index.insert_many(docs)
                        docs.clear() 
                        gc.collect()
    books_inverted_index.create_index([("term", pymongo.ASCENDING)])
    books_inverted_index.create_index([("books._id", pymongo.ASCENDING)])

write_index()