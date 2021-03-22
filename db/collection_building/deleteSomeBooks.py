##################################################################
# Run this script to delete non-ISBN, non-English and empty books
##################################################################

import os 
from helperFunctions import findISBN 
from langdetect import detect

directory = r"/root/books"
folders = ['0_Other', '0', '1', '2','3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

nonEnglishBooks = 0
nonISBNBooks = 0
emptyBooks = 0

for folder in folders:
    subdir = directory + '/' + folder
    for filename in os.listdir(subdir):
        if filename.endswith(".txt"):
            filepath = subdir + '/' + filename
            f = open(filepath)
            try:
                text = f.read()
                reason = ""

                # Remove if book meets deletion criteria
                if len(text) == 0:
                    emptyBooks += 1
                    os.remove(filepath)
                    reason = "Empty"
                elif detect(text) != "en": 
                    nonEnglishBooks += 1
                    os.remove(filepath)
                    reason = "Non-English"
                elif findISBN(text) == False:
                    nonISBNBooks += 1
                    os.remove(filepath)
                    reason = "No-ISBN"
                f.close()
                
            except Exception as ex: 
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print(message)
                print(filepath)
        else:
            continue

booksDeleted.close()
print("Files deleted: " + str(nonEnglishBooks)  + " non English books, " + str(nonISBNBooks) + " non-ISBN books, and " + str(emptyBooks) + " empty books.")
