##################################################################
# AFTER deleting the books that require deletion
# RUN this script to make the books and quotes collections
##################################################################
import time
import pymongo 
import os 
import re
import gc
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.stem.porter import *
from helperFunctions import findISBN 
from nltk import sent_tokenize
from helperFunctions import getBookMetadata
from tqdm import tqdm # progress bar 

# Possible addition: author name + book name? During Author section, those might be mentioned
bad_chars = set(['#','<','>','*','_',':','\n','@'])
bad_words = set(['copy right','copyright','.com','www','copyediting','of fiction','e-book','all rights reserved','published by',
            'publisher','manuscript','editor','coincidental','reproduce','special thank'])
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
    folders = ['0_Other','0','1','2','3','4','5','6','7','8','9','A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    directory = "/root/books"

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
                if bookMetadata == False or bookMetadata == None:
                    booksWithFaultyISBNOrCateg += 1
                    os.remove(filepath)
                    continue 

                # Insert book
                bookMetadata["_id"] =  bookID
                bookID += 1
                b = booksCollec.insert_one(bookMetadata)
                terms_count = 0
                
                # Insert quotes
                quotes = getQuotes(text)
                quotes_objects = []
                counter = 1000
                for quote in quotes:
                    quoteDoc = {"book_id" : b.inserted_id, "quote" : quote}
                    quoteDoc["_id"] = quoteID
                    quoteID += 1
                    quotes_objects.append(quoteDoc)
                    terms_count += len([stemmer.stem(token.lower()) for token in re.findall(r'\w+', quote) if not token.lower() in stopSet])
                    counter -= 1
                    if counter == 0:
                        quotesCollec.insert_many(quotes_objects)
                        counter = 1000
                        quotes_objects.clear()
                        quotes_objects = []
                        gc.collect()

                booksCollec.update_one({"_id" : bookID}, {"$set" : {"terms_count" : terms_count}})
                print("Finished book: ", bookID)

    print("Books removed for having a faulty ISBN or category: " + str(booksWithFaultyISBNOrCateg))
    client.close()

def getQuotes(text):
    quotes = []
    paragraphs = text.split("\n\n") 

    # A quote is a paragraph with at least 10 words that doesnt include bad chars/words or thank you multiple times 
    for par in paragraphs:
        found_bad_chars = False 
        found_bad_words = False
        
        for char in par:
            if char in bad_chars:
                found_bad_chars = True
                break 
        for word in par.lower():
            if word in bad_words:
                found_bad_words = True 
                break
        
        # Usually if thank you/thanks appears more than 2-3 times, itis an Acknowledgement section
        thank_you_count = par.lower().count('thank') 
        
        if len(re.findall('\w+', par)) >=10 and not found_bad_chars and not found_bad_words and thank_you_count<3:
            quotes.append(par)
    return quotes


buildCollections()


