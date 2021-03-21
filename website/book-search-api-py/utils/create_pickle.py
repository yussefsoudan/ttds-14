import pickle
import sys, os
import sys
sys.path.append('../')
from MongoDB import MongoDB
from collections import defaultdict
import pprint
import nltk 
import re
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.stem.porter import *
import time

mongo = MongoDB()
quotes = mongo.quotes

book_term_counts = defaultdict(lambda: 0)

stopSet = set(stopwords.words('english'))
stemmer = PorterStemmer()

start_time = time.time()
all_quotes = quotes.find({}, {"quote": 1, "book_id": 1, "_id": 0})
if all_quotes is not None:
    previous_book_id = 1
    book_term_count = 0

    for quote in all_quotes:
        # if current book id is not what was previously processed, store what has been counted for previous book id
        if quote['book_id'] != previous_book_id:
            # add / update the term counts of the previous book id to the dictionary
            if previous_book_id in book_term_counts:
                print("adding to book with id {} count {}".format(previous_book_id, book_term_count))
                book_term_counts[previous_book_id] += book_term_count
            else:
                print("setting book with id {} as count {}".format(previous_book_id, book_term_count))
                book_term_counts[previous_book_id] = book_term_count
            previous_book_id = quote['book_id']
            book_term_count = 0
        
        # get preprocessed terms of the quote and add it to the current book's count
        terms = [stemmer.stem(token.lower()) for token in re.findall(r'\w+', quote['quote']) if not token.lower() in stopSet]
        book_term_count += len(terms)

    book_term_counts[previous_book_id] = book_term_count

print("final book term counts: {}".format(dict(book_term_counts)))
pickle.dump(dict(book_term_counts), open(f'book_term_counts.p', 'wb'))
print("Finished.")
print("--- {} seconds ---".format(time.time() - start_time))