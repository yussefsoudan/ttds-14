import pymongo 
import nltk 
from nltk.corpus import stopwords
nltk.download('stopwords')
import re
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.stem.porter import *
import pickle


def build_index():
    stopSet = set(stopwords.words('english'))
    stemmer = PorterStemmer()
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["TTDS"]
    quotesCollec = db["quotes"]
    loadSize = 1000
    tempIndex = dict()
    
    for r in range(0, 57000):
        lowerLimit = r * loadSize
        upperLimit = lowerLimit + loadSize
        quotes = quotesCollec.find({"_id" : {"$lt" : upperLimit, "$gte" : lowerLimit}})
        
        for q in quotes:
            q_id = q['_id']
            b_id = q['book_id']
            terms = [stemmer.stem(token.lower()) for token in re.findall(r'\w+', q['quote']) if not token.lower() in stopSet]

            for term in set(terms):
                pos = [i for i, token in enumerate(terms) if token == term]
                tempIndex[term] = tempIndex.get(term, {'term' : term, 'term_freq' : 0, 'books' : {}})
                tempIndex[term]['term_freq'] += 1
                tempIndex[term]['books'][b_id] = tempIndex[term]['books'].get(b_id, {'_id': b_id, 'term_freq_in_book': 0, 'quotes': []})
                tempIndex[term]['books'][b_id]['term_freq_in_book'] += 1
                tempIndex[term]['books'][b_id]['quotes'].append({'_id' : q_id, 'len' : len(terms), 'pos': pos})

        if (r != 0 and r % 800 == 0):
            print(r)
            for value in tempIndex.values():
                value['books'] = list(value['books'].values())
            with open("root/index/" + str(r-800) + "-load" + '.pickle', 'wb') as handle:
                pickle.dump(list(tempIndex.values()), handle, protocol=pickle.HIGHEST_PROTOCOL)
            tempIndex.clear()
    for value in tempIndex.values():
        value['books'] = list(value['books'].values())
    with open("root/index/" + str(r-800) + "-load" + '.pickle', 'wb') as handle:
        pickle.dump(list(tempIndex.values()), handle, protocol=pickle.HIGHEST_PROTOCOL)
    tempIndex.clear()

    client.close()

       
build_index()
     
