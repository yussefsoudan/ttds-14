import pymongo 
import os 
import re
import nltk
nltk.download('punkt')
from nltk import sent_tokenize

def makeBooksAndQuotesCollections():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["TTDS"]
    booksCollec = db["books"]
    quotesCollec = db["quotes"]

    directory = r"/Users/yussefsoudan/Studies/Uni/year-4-cs/TTDS/CW3"
    folders = ['7', 'X', 'Y', 'Z']
    for folder in folders:
        subdir = directory + '/' + folder
        for filename in os.listdir(subdir):
            if filename.endswith(".txt"):
                filepath = subdir + '/' + filename
                text = open(filepath, "r").read()

                authorIncluded = True if "-" in filename else False
                title = filename if not authorIncluded else filename.split("-")[0].strip()
                author = False if not authorIncluded else filename.split("-")[1].split(".")[0].strip()
                ISBN = findISBN(filepath)
                quotes = getQuotes(text)

                # Insert book
                bookDoc = {"title" : title, "author" : author, "ISBN": ISBN}
                x = booksCollec.insert_one(bookDoc)

                # Insert paragraph
                for quote in quotes:
                    quoteDoc = {"book_id" : x.inserted_id, "quote" : quote}
                    quotesCollec.insert_one(quoteDoc)
                 
    client.close()

def getQuotes(text):
    quotes = text.split("\n\n") # quote is a paragraph
    return quotes


def findISBN(text):

    # Try first with 'ISBN' included
    regex0 = re.compile("(?:ISBN(?:-1[03])?:? ?)(?:978(?:-|\s)?|979(?:-|\s)?)?(?:[0-9]{1,5}(?:-|\s)?)(?:[0-9]{1,7}(?:-|\s)?)(?:[0-9]{1,6}(?:-|\s)?)(?:[0-9X]{1}(?:-|\s)?)")    
    # Try without 'ISBN' and hyphen seperated
    regex1 = re.compile("(?:978(?:-)?|979(?:-)?)?(?:[0-9]{1,5}(?:-))(?:[0-9]{1,7}(?:-))(?:[0-9]{1,6}(?:-))(?:[0-9X]{1})")
    # Try without 'ISBN' and not seperated (must be of length 10 or 13; if 13, must start with 978 or 979)
    regex2 = re.compile("(?:978|979)?(?:[0-9]{9})(?:[0-9X]{1})")
    # Try without 'ISBN' and space seperated and ISBN-13 ONLY (sacrifice space seperated 10)
    regex3 = re.compile("(?:978\s|979\s)(?:[0-9]{1,5}\s)(?:[0-9]{1,7}\s)(?:[0-9]{1,6}\s)(?:[0-9X]{1})")

    if regex0.search(text):
        match = regex0.search(text).group(0)
        if ":" in match:
            return match.split(":")[1].strip()
        else:
            return match.split("ISBN")[1].strip()
    elif regex1.search(text):
        match = regex1.search(text).group(0)
        return match
    elif regex2.search(text):
        match = regex2.search(text).group(0)
        return match 
    elif regex3.search(text):
        match = regex3.search(text).group(0)
        return match
    return False


makeBooksAndQuotesCollections()


