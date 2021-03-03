import pymongo 
import pickle
import os


def write_index():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["TTDS"]
    inverted_index = db["invertedIndex"]
    directory = "root/index/"
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".pickle"): 
            path = directory + filename 
            if os.path.getsize(path) > 0:
                with open(path, 'rb') as handle:
                    docs = pickle.load(handle)
                    if len(docs) > 3:
                        inverted_index.insert_many(docs)

write_index()
                

