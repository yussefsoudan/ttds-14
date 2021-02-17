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
    doc = {}
    terms = [stemmer.stem(token.lower()) for token in re.findall(r'\w+', q['quote']) if not token.lower() in stopSet]
    for pos, term in enumerate(terms):
        query = inverted_index.find({'term' : term})
        
        # Unique term
        if inverted_index.count_documents({'term' : term}) == 0: 
            doc['_id'] = index
            index += 1
            doc['term'] = term 
            doc['term_freq'] = 1 # num of times term occurs across all quotes
            doc['books'] = {
                q['book_id'] : { 
                    'term_freq_in_book': 1, 
                    'quotes' : {
                        q['_id'] : {'len' : len(terms), 'pos' : [pos] }
                    }
                }
            }
            inverted_index.insert_one(doc)

            if index == 1:
                inverted_index.create_index([("term", pymongo.ASCENDING)])
        # Term already exists
        else:
            # Each term should have one entry (for now)
            updated = query[0]
            val = updated['term_freq'] + 1
            inverted_index.update_one({'term' : term}, {"$set" : { 'term_freq': val}})

            # Term already occured in this book
            if q['book_id'] in updated['books'].keys():
                key = 'books.' + q['book_id']
                val = updated['books'][q['book_id']]['term_freq_in_book'] + 1
                inverted_index.update_one({'term' : term}, {"$set" : { key: val}})

                # Term already occured in this particular quote
                if q['_id'] in updated['books'][q['book_id']]['quotes'].keys():
                    key = 'books.' + q['book_id'] + '.quotes.' + q['_id'] + '.pos' 
                    inverted_index.update_one({'term' : term}, {"$push" : { key: pos}})
                    
                # Term appeared in a new quote in this book
                else:  
                    key = 'books.' + q['book_id'] + '.quotes.' + q['_id'] 
                    obj = {'_id' : q['_id'], 'len' : len(terms), 'pos' : [pos]}
                    inverted_index.update_one({'term' : term}, {"$set" : { key: obj}})
            # First time term occurs in this book
            else:
                obj = {
                        'term_freq_in_book': 1, 
                        'quotes' : {
                            q['_id'] : {'len' : len(terms), 'pos' : [pos]}
                        }
                    }
                key = 'books.' + q['book_id']
                inverted_index.update_one({'term' : term}, {"$set" : { key : obj}})


# inverted_index.create_index([("books._id", pymongo.ASCENDING)])    
# inverted_index.create_index([("books.quotes._id", pymongo.ASCENDING)])       
client.close()