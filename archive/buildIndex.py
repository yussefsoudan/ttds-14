import pymongo 
import nltk 
from nltk.corpus import stopwords
nltk.download('stopwords')
import re
from tqdm import tqdm
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.stem import *
from nltk.stem.porter import *
stopSet = set(stopwords.words('english'))
stemmer = PorterStemmer()

stopSet = set(stopwords.words('english'))
stemmer = PorterStemmer()
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["TTDS"]
booksCollec = db["books"]
quotesCollec = db["quotes"]
inverted_index = db["inverted_index"]

quotes = quotesCollec.find({})
index = 0
for q in tqdm(quotes):
    q_id = q['_id']
    b_id = q['book_id']
    doc = {}
    terms = [stemmer.stem(token.lower()) for token in re.findall(r'\w+', q['quote']) if not token.lower() in stopSet]
    for pos, term in enumerate(terms):
        query = inverted_index.find({'_id' : term})
        
        # Unique term
        if inverted_index.count_documents({'_id' : term}) == 0: 
            doc['_id'] = term
            doc['term_freq'] = 1 # num of times term occurs across all quotes
            doc['books'] = {
                b_id : { 
                    'term_freq_in_book': 1, 
                    'quotes' : {
                        q_id : {'len' : len(terms), 'pos' : [pos] }
                    }
                }
            }
            inverted_index.insert_one(doc)

            # if index == 1:
            #     inverted_index.create_index([("term", pymongo.ASCENDING)])
        # Term already exists
        else:
            # Each term should have one entry (for now)
            updated = query[0]
            val = updated['term_freq'] + 1
            inverted_index.update_one({'_id' : term}, {"$set" : { 'term_freq': val}}, upsert=False)

            # Term already occured in this book
            if b_id in updated['books'].keys():
                key = 'books.' + b_id + '.term_freq_in_book'
                val = updated['books'][b_id]['term_freq_in_book'] + 1
                inverted_index.update_one({'_id' : term}, {"$set" : { key: val}}, upsert=False)

                # Term already occured in this particular quote
                if q_id in updated['books'][b_id]['quotes'].keys():
                    key = 'books.' + b_id + '.quotes.' + q_id + '.' + 'pos'
                    inverted_index.update_one({'_id' : term}, {"$push" : { key: pos}}, upsert=False)
                    
                # Term appeared in a new quote in this book
                else:  
                    key = 'books.' + b_id + '.quotes.' + q_id
                    obj = {'_id' : q_id, 'len' : len(terms), 'pos' : [pos]}
                    inverted_index.update_one({'_id' : term}, {"$set" : { key: obj}}, upsert=False)
            # First time term occurs in this book
            else:
                obj = {
                        'term_freq_in_book': 1, 
                        'quotes' : {
                            q_id : {'len' : len(terms), 'pos' : [pos]}
                        }
                    }
                key = 'books.' + b_id
                inverted_index.update_one({'_id' : term}, {"$set" : { key : obj}}, upsert=False)
     
client.close()