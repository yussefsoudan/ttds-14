import os 
from langdetect import detect

directory = r"/Users/yussefsoudan/Studies/Uni/year-4-cs/TTDS/CW3"
folders = ['7', 'X', 'Y', 'Z']
nonEnglishBooks = 0
emptyBooks = 0
booksDeleted = open("booksDeleted.txt", "w")

for folder in folders:
    subdir = directory + '/' + folder
    for filename in os.listdir(subdir):
        if filename.endswith(".txt"):
            filepath = subdir + '/' + filename
            f = open(filepath)
            try:
                # Read first 3000 chars only (to save memory)
                text = f.read(3000)
                # Remove if book is empty or not English
                if len(text) == 0 or detect(text) != "en":
                    bookIsNotEnglish = True if len(text) != 0 else False 
                    nonEnglishBooks = (nonEnglishBooks + 1) if bookIsNotEnglish else nonEnglishBooks
                    emptyBooks = (emptyBooks + 1) if not bookIsNotEnglish else emptyBooks
                    reason = "NotEnglish" if bookIsNotEnglish else "Empty"
                    booksDeleted.write(filepath + "---" + reason + "\n")
                    os.remove(filepath)
                f.close()
            except Exception as ex: 
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print(message)
                print(filepath)
        else:
            continue

booksDeleted.close()
print("Files deleted: " + str(nonEnglishBooks)  + " non English books, and " + str(emptyBooks) + " empty books.")