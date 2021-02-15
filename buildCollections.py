##################################################################
# AFTER deleting the books that require deletion
# RUN this script to make the books and quotes collections
##################################################################

import pymongo 
import os 
import re
import nltk
from helperFunctions import findISBN 
from nltk import sent_tokenize
from helperFunctions import getBookMetadata
from tqdm import tqdm # progress bar 
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.stem import *
from nltk.stem.porter import *
stopSet = set(stopwords.words('english'))
stemmer = PorterStemmer()

def buildCollections():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["TTDS"]
    booksCollec = db["books"]
    quotesCollec = db["quotes"]
    inverted_index = db["inverted_index"]
    booksWithFaultyISBNOrCateg = 0
    index = 0
    bookID = 0
    quoteID = 0

    directory = r"/Users/yussefsoudan/Studies/Uni/year-4-cs/TTDS/CW3"
    #directory = r"C:/Users/Erodotos/Desktop/Year 4/TTDS/group-project/Book3"
    folders = ['7', 'X', 'Y', 'Z']

    for folder in folders:
        subdir = directory + '/' + folder
        for filename in tqdm(os.listdir(subdir)):
            if filename.endswith(".txt"):
                filepath = subdir + '/' + filename
                text = open(filepath, "r", encoding='utf-8').read()

                authorIncluded = True if "-" in filename else False
                title = filename if not authorIncluded else filename.split("-")[0].strip()
                author = False if not authorIncluded else filename.split("-")[1].split(".")[0].strip()
                ISBN = findISBN(text) # Books without ISBN have already been removed
                bookMetadata = getBookMetadata(ISBN, title, author)

                # The ISBN does NOT match the Google ISBNs or chosen categories, remove book.
                if bookMetadata == False:
                    booksWithFaultyISBNOrCateg += 1
                    os.remove(filepath)
                    continue 

                quotes = getQuotes(text)

                # Insert book
                bookMetadata["_id"] = "b" + str(bookID)
                bookID += 1
                b = booksCollec.insert_one(bookMetadata)

                # Insert paragraph
                for quote in quotes:
                    indexDoc = {}
                    quoteDoc = {"book_id" : b.inserted_id, "quote" : quote}
                    quoteDoc["_id"] = "q" + str(quoteID)
                    quoteID += 1
                    q = quotesCollec.insert_one(quoteDoc)
                    
                    # Insert inverted index entry 
                    terms = [stemmer.stem(token.lower()) for token in re.findall(r'\w+', quote) if not token.lower() in stopSet]
                    for pos, term in enumerate(terms):
                        query = inverted_index.find({'term' : term})
                        # Unique term
                        if inverted_index.count_documents({'term' : term}) == 0: 
                            indexDoc['_id'] = index
                            index += 1
                            indexDoc['term'] = term 
                            indexDoc['term_freq'] = 1 # num of times term occurs across all quotes
                            indexDoc['books'] = {
                                b.inserted_id : {
                                    'term_freq_in_book': 1, 
                                    'quotes' : {
                                            q.inserted_id : {'len' : len(terms), 'pos' : [pos]}
                                        }
                                }
                            }
                            inverted_index.insert_one(indexDoc)

                            # Make the multi-layer indices on the inverted_index collection
                            if index == 1:
                                inverted_index.create_index([("term", pymongo.ASCENDING)])
                        # Term already exists
                        else:
                            # Each term should have one entry (for now)
                            updated = query[0]
                            updated['term_freq'] += 1
                            bookFound = True if b.inserted_id in updated['books'].keys() else False
                            # Term already occured in this book
                            if bookFound == True:
                                updated['books'][b.inserted_id]['term_freq_in_book'] += 1 
                                quoteFound = True if q.inserted_id in updated['books'][b.inserted_id]['quotes'].keys() else False
                                # Term already occured in this particular quote
                                if quoteFound == True:
                                    updated['books'][b.inserted_id]['quotes'][q.inserted_id]['pos'].append(pos)
                                # Term appeared in a new quote in this book
                                else:
                                    updated['books'][b.inserted_id]['quotes'][q.inserted_id] = {'len' : len(terms), 'pos' : [pos]}
                                    
                            # First time term occurs in this book
                            else:
                                updated['books'][b.inserted_id] = {
                                        'term_freq_in_book': 1, 
                                        'quotes' : {
                                            q.inserted_id : {'len' : len(terms), 'pos' : [pos]}
                                        }
                                    }
                                
                            inverted_index.update_one({'term' : term}, {"$set" : updated})


    print("Books removed for having a faulty ISBN or category: " + str(booksWithFaultyISBNOrCateg))
    client.close()

def getQuotes(text):
    quotes = []
    paragraphs = text.split("\n\n") 
    bad_chars = ['#','<','>','*','_',':','\n','@']
    bad_words = ['copyright','.com','www','copyediting','of fiction','e-book','all rights reserved','published by',
                'publisher','manuscript','editor','coincidental','reproduce','special thank'] 
    
    #Possible addition: author name + book name? During Author section, those might be mentioned

    # A quote is a paragraph with at least 10 words that doesnt include bad chars/words or thank you multiple times 
    for par in paragraphs:
        found_bad_chars = any (char in par for char in bad_chars)
        found_bad_words = any (word in par.lower() for word in bad_words)
        
        # Usually if thank you/thanks appears more than 2-3 times, itis an Acknowledgement section
        thank_you_count = par.lower().count('thank') 
        
        if len(re.findall('\w+', par)) >=10 and not found_bad_chars and not found_bad_words and thank_you_count<3:
            quotes.append(par)
    return quotes



buildCollections()


