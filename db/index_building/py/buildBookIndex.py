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


def build_book_index(): # each term will have 200 docs max
    stopSet = set(stopwords.words('english'))
    stemmer = PorterStemmer()
    DB_PASS= os.environ.get("DB_PASS")
    DB_USER= os.environ.get("DB_USER")
    DB_NAME= os.environ.get("DB_NAME")
    DB_HOST= os.environ.get("DB_HOST")
    PORT = os.environ.get("PORT")
    client = pymongo.MongoClient(f'mongodb://{DB_USER}:{DB_PASS}@{DB_HOST}:{PORT}') 
    db = client["TTDS"]
    booksCollec = db["books"]
    loadSize = 1000
    currIndexPortion = dict()
    
    for r in range(0, 27):
        lowerLimit = r * loadSize
        upperLimit = lowerLimit + loadSize
        books = booksCollec.find({"_id" : {"$lt" : upperLimit, "$gte" : lowerLimit}})
        print("Processing books from {} to {}".format(lowerLimit, upperLimit))
        
        for b in books:
            b_id = b['_id']
            regexForPos = re.compile("[\s.,;'\"\(\)\[\]]")
            termsSplit = regexForPos.split(b['title'].lower())
            terms = [stemmer.stem(token.lower()) for token in re.findall(r'\w+', b['title']) if not token.lower() in stopSet]

            for term in set(terms):
                pos = [i for i, split in enumerate(termsSplit) if term in split]
                currIndexPortion[term] = currIndexPortion.get(term, {'term' : term, 'term_freq' : 0, 'books' : {}})
                currIndexPortion[term]['term_freq'] += 1
                currIndexPortion[term]['books'][b_id] = currIndexPortion[term]['books'].get(b_id, {'_id': b_id, 'title_len' : len(re.findall(r'\w+', b['title'])), 'term_freq_in_book_title': 0, 'pos': pos})
                currIndexPortion[term]['books'][b_id]['term_freq_in_book_title'] += 1
        gc.collect()

    for value in currIndexPortion.values():
        value['books'] = list(value['books'].values())
    with open("/root/bookIndex/" + 'all' + '.p', 'wb') as handle:
        pickle.dump(list(currIndexPortion.values()), handle)
    currIndexPortion.clear()
    gc.collect()

    client.close()
build_book_index()
     
