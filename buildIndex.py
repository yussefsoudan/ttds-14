import pymongo 
import nltk 
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.stem import *
from nltk.stem.porter import *
import re

stopSet = set(stopwords.words('english'))
stemmer = PorterStemmer()
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["TTDS"]
booksCollec = db["books"]
quotesCollec = db["quotes"]
inverted_index = db["inverted_index"]

quotes = quotesCollec.find({})
index = 0
for q in quotes:
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
            doc['books'] = [
                {'_id' : q['book_id'], 
                'term_freq_in_book': 1, 
                'quotes' : [
                    {'_id' : q['_id'], 'len' : len(terms), 'pos' : [pos]}
                    ]
                }
                ]
            inverted_index.insert_one(doc)
        # Term already exists
        else:
            # Each term should have one entry (for now)
            updated = query[0]
            updated['term_freq'] += 1
            bookFound = False
            for i, book in enumerate(updated['books']):
                # Term already occured in this book
                if book['_id'] == q['book_id']:
                    bookFound = True
                    updated['books'][i]['term_freq_in_book'] += 1 
                    quoteFound = False
                    for j, quote2 in enumerate(updated['books'][i]['quotes']):
                        # Term already occured in this particular quote
                        if quote2['_id'] == q['_id']:
                            quoteFound = True
                            updated['books'][i]['quotes'][j]['pos'].append(pos)
                            break
                    # Term appeared in a new quote in this book
                    if (quoteFound == False):
                        updated['books'][i]['quotes'].append({'_id' : q['_id'], 'len' : len(terms), 'pos' : [pos]})
                    break
            # First time term occurs in this book
            if (bookFound == False):
                updated['books'].append({
                        '_id' : q['book_id'], 
                        'term_freq_in_book': 1, 
                        'quotes' : [
                            {'_id' : q['_id'], 'len' : len(terms), 'pos' : [pos]}
                        ]
                    }
                )
            inverted_index.update_one({'term' : term}, {"$set" : updated})

inverted_index.create_index([("term", pymongo.ASCENDING)])
inverted_index.create_index([("books._id", pymongo.ASCENDING)])    
inverted_index.create_index([("books.quotes._id", pymongo.ASCENDING)])       
client.close()