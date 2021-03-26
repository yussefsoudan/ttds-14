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


def build_book_index(): # each term will have 200 docs max
    stopSet = set(stopwords.words('english'))
    stemmer = PorterStemmer()
    DB_PASS='thenittygrittyofELnitty'
    DB_USER='readerTTDS'
    DB_NAME='TTDS' 
    DB_HOST='188.166.173.191'
    PORT = '27017'
    client = MongoClient(f'mongodb://{DB_USER}:{DB_PASS}@{DB_HOST}:{PORT}') 
    db = client["TTDS"]
    booksCollec = db["books"]
    loadSize = 1000
    tempIndex = dict()
    
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
                tempIndex[term] = tempIndex.get(term, {'term' : term, 'term_freq' : 0, 'books' : {}})
                tempIndex[term]['term_freq'] += 1
                tempIndex[term]['books'][b_id] = tempIndex[term]['books'].get(b_id, {'_id': b_id, 'title_len' : len(re.findall(r'\w+', b['title'])), 'term_freq_in_book_title': 0, 'pos': pos})
                tempIndex[term]['books'][b_id]['term_freq_in_book_title'] += 1

        books.clear()
        gc.collect()

    for value in tempIndex.values():
        value['books'] = list(value['books'].values())
    with open("/root/bookIndex/" + 'all' + "-load" + '.pickle', 'wb') as handle:
        pickle.dump(list(tempIndex.values()), handle, protocol=pickle.HIGHEST_PROTOCOL)
    tempIndex.clear()
    gc.collect()

    client.close()
build_book_index()
     
