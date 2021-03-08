"""
This script computes the average processed (stop words removed) sentence length based on the sentences collection.
"""
import pickle
from MongoDB import MongoDB
# from pymongo.operations import UpdateMany
from collections import defaultdict
import pprint
import nltk 
import re
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.stem.porter import *
import time
# from ir_eval.preprocessing import preprocess

# START_COUNT = 57600000

mongo = MongoDB()
# sentences = mongo.sentences
quotes = mongo.quotes
# movies = mongo.movies
# books = mongo.books
# LIMIT = 100000

total_counted = 0       # START_COUNT
book_term_counts = defaultdict(lambda: 0)
# movie_term_counts = pickle.load(open('movie_term_counts.p', 'rb'))
# movie_id = list(movie_term_counts.keys())[-1]
# movie_term_count = movie_term_counts[movie_id]

# initialisation
book_id = "b0" 
book_term_count = 0
stopSet = set(stopwords.words('english'))
stemmer = PorterStemmer()

start_time = time.time()
try:
    ss = quotes.find({}, {"quote": 1, "book_id": 1, "_id": 0}) # , skip=total_counted
    if ss is not None:
        for s in ss:
            if s['book_id'] != book_id:
                # Add / Update the term counts of the book_id to the dictionary
                if book_id in book_term_counts:
                    print("adding to book with id {} count {}".format(book_id, book_term_count))
                    book_term_counts[book_id] += book_term_count
                else:
                    print("setting book with id {} as count {}".format(book_id, book_term_count))
                    book_term_counts[book_id] = book_term_count
                book_id = s['book_id']
                book_term_count = 0

            terms = [stemmer.stem(token.lower()) for token in re.findall(r'\w+', s['quote']) if not token.lower() in stopSet]
            book_term_count += len(terms)
            total_counted += 1
        book_term_counts[book_id] = book_term_count
        # if total_counted % LIMIT != 0:
        #     break
except:
    pass

print("final book term counts: {}".format(dict(book_term_counts)))
pickle.dump(dict(book_term_counts), open(f'book_term_counts.p', 'wb'))
print("Finished.")
print("--- {} seconds ---".format(time.time() - start_time))