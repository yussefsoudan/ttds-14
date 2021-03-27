import pymongo 
import nltk 
from nltk.corpus import stopwords
nltk.download('stopwords')
import re
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.stem.porter import *
import pickle
import gc
from dotenv import load_dotenv
from os.path import join, dirname
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
import os

def build_index(): # each term will have 200 docs max
    stopSet = set(stopwords.words('english'))
    stemmer = PorterStemmer()
    DB_PASS= os.environ.get("DB_PASS")
    DB_USER= os.environ.get("DB_USER")
    DB_NAME= os.environ.get("DB_NAME")
    DB_HOST= os.environ.get("DB_HOST")
    PORT = os.environ.get("PORT")
    client = pymongo.MongoClient(f'mongodb://{DB_USER}:{DB_PASS}@{DB_HOST}:{PORT}') 
    db = client["TTDS"]
    quotesCollec = db["quotes"]
    loadSize = 1000
    currIndexPortion = dict()
    iterations = 0
    files_counter = 0
    
    for r in range(0, 41000):
        iterations += 1
        lowerLimit = r * loadSize
        upperLimit = lowerLimit + loadSize

        # Load 1000 quote objects at a time in memory
        quotes = quotesCollec.find({"_id" : {"$lt" : upperLimit, "$gte" : lowerLimit}})
        
        # Populate currIndexPortion with the current quotes batch
        for q in quotes:
            q_id = q['_id']
            b_id = q['book_id']
            regexForPos = re.compile("[\s.,;'\"\(\)\[\]]")
            termsSplit = regexForPos.split(q['quote'].lower())
            terms = [stemmer.stem(token.lower()) for token in re.findall(r'\w+', q['quote']) if not token.lower() in stopSet]

            for term in set(terms):
                pos = [i for i, split in enumerate(termsSplit) if term in split]
                currIndexPortion[term] = currIndexPortion.get(term, {'term' : term, 'term_freq' : 0, 'books' : {}})
                currIndexPortion[term]['term_freq'] += 1
                currIndexPortion[term]['books'][b_id] = currIndexPortion[term]['books'].get(b_id, {'_id': b_id, 'term_freq_in_book': 0, 'quotes': []})
                currIndexPortion[term]['books'][b_id]['term_freq_in_book'] += 1
                currIndexPortion[term]['books'][b_id]['quotes'].append({'_id' : q_id, 'len' : len(re.findall(r'\w+', q['quote'])), 'pos': pos})

        # Write current batch to disk once every 205 iterations: will output 200 portions of the index
        if iterations == 205:
            iterations = 0
            for value in currIndexPortion.values():
                value['books'] = list(value['books'].values())
            # Write to disk in the Mongo insert_many format
            with open("/root/index/" + str(files_counter) + '.p', 'wb') as handle:
                pickle.dump(list(currIndexPortion.values()), handle, protocol=pickle.HIGHEST_PROTOCOL)
                files_counter += 1
            currIndexPortion.clear()
            gc.collect()

    for value in currIndexPortion.values():
        value['books'] = list(value['books'].values())
    # Write to disk in the Mongo insert_many format
    with open("/root/index/" + str(files_counter) + '.p', 'wb') as handle:
        pickle.dump(list(currIndexPortion.values()), handle, protocol=pickle.HIGHEST_PROTOCOL)
    currIndexPortion.clear()
    gc.collect()

    client.close()

       
build_index()
     
