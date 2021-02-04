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

def buildCollections():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["TTDS"]
    booksCollec = db["books"]
    quotesCollec = db["quotes"]
    booksWithFaultyISBN = 0

    directory = r"/Users/yussefsoudan/Studies/Uni/year-4-cs/TTDS/CW3"
    folders = ['7', 'X', 'Y', 'Z']
    for folder in folders:
        subdir = directory + '/' + folder
        for filename in os.listdir(subdir):
            if filename.endswith(".txt"):
                filepath = subdir + '/' + filename
                text = open(filepath).read()

                authorIncluded = True if "-" in filename else False
                title = filename if not authorIncluded else filename.split("-")[0].strip()
                author = False if not authorIncluded else filename.split("-")[1].split(".")[0].strip()
                ISBN = findISBN(text) # Books without ISBN have already been removed
                bookMetadata = getBookMetadata(ISBN, title, author)

                # The ISBN does NOT match the Google ISBNs, remove book.
                if bookMetadata == False:
                    booksWithFaultyISBN += 1
                    os.remove(filepath)
                    continue 

                quotes = getQuotes(text)

                # Insert book
                x = booksCollec.insert_one(bookMetadata)

                # Insert paragraph
                for quote in quotes:
                    quoteDoc = {"book_id" : x.inserted_id, "quote" : quote}
                    quotesCollec.insert_one(quoteDoc)

    print("Books removed for having a faulty ISBN: " + str(booksWithFaultyISBN))
    client.close()

def getQuotes(text):
    quotes = []
    paragraphs = text.split("\n\n") 
    bad_chars = ['#','<','>','*','_',':','\n']

    # A quote is a paragraph with at least 10 chars and no 'bad' characters. 
    for par in paragraphs:
        if len(re.findall('\w+', par)) >=10 and not any (char in par for char in bad_chars):
            quotes.append(par)
    return quotes




buildCollections()


