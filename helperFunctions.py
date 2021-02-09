import re
import requests

def getBookMetadata(ISBN, title, author):

    URL = "https://www.googleapis.com/books/v1/volumes?q=isbn"
    
    # Remove space, dashes or colons from isbn
    ISBN = ISBN.translate({ord(i): None for i in ' -:'}) 
    metadata = {'title' : title, 
        'authors' : [author], 
        'isbn-10' : '', 
        'isbn-13' : '',
        'categories' : [], 
        'thumbnail' : '', 
        'publishedDate' : '',
        'previewLink' : '',
        'pageCount' : '',
        'averageRating' : ''}

    endpoint = URL + ISBN
    accepted_cats = set(['fiction','biography & autobiography','juvenile fiction','poetry','young adult fiction',
                     'philosophy','young adult nonfiction','true crime','indic fiction (english)', 'poetry'])
    
    # Account for occasional failure of get request even though the book might exist
    for i in range(3):

        # Sending GET request and saving the response as response object 
        r = requests.get(url = endpoint) 

        # Extract data in JSON format 
        data = r.json()
        items = 0
        
        # Sometimes due to server error, the totalItems tag cannot be accessed
        # However, the normal case is that even if a book is not registered in the API, the
        # totalItems tag will be 0
        try:
            items = data['totalItems']
        except:
            print("No totalItems tag found, probably due to server error")
        
        if items > 0:
            # Sometimes, the first item returned from the API is not the book with the given isbn
            # Search through the items list provided to find which item is the correct one 
            item_idx = 0
            for j in range(items):
                # industryIdentifiers tag might not exist
                isbn10 = ''
                isbn13 = ''
                try:
                    isbn10 = data['items'][j]['volumeInfo']['industryIdentifiers'][0]['identifier']
                except:
                    # print("No registered ISBN-10 found!")
                    pass
                try:
                    isbn13 = data['items'][j]['volumeInfo']['industryIdentifiers'][1]['identifier']    
                except:
                    #print("No registered ISBN-13 found!")  
                    pass

                if (ISBN == isbn10 or ISBN == isbn13):
                    item_idx = j
                    metadata['isbn-10'] = isbn10 
                    metadata['isbn-13'] = isbn13
                    break
            
            title = data['items'][item_idx]['volumeInfo']['title']
            metadata['title'] = title
            
            # Author tag might not exist
            try:
                authors = data['items'][item_idx]['volumeInfo']['authors']
                metadata['authors'] = authors
            except:
                #print("No authors found!") 
                pass
               
            # Categories tag might not exist
            try:
                categories = data['items'][item_idx]['volumeInfo']['categories']
                metadata['categories'] = categories
            except:
                #print("No categories found!")
                pass
            
            # Published date might not exist
            try:
                publishedDate = data['items'][item_idx]['volumeInfo']['publishedDate']
                metadata['publishedDate'] = publishedDate
            except:
                #print("No published date found!")
                pass

            # Thumbnail might not exist
            try:
                thumbnail = data['items'][item_idx]['volumeInfo']['imageLinks']['thumbnail']
                metadata['thumbnail'] = thumbnail
            except:
                #print("No thumbnail found!")
                pass

            # Preview link might not exist
            try: 
                previewLink = data['items'][item_idx]['volumeInfo']['previewLink']
                metadata['previewLink'] = previewLink
            except:
                #print("No preview link found!")
                pass

            # Pagecount might not exist 
            try: 
                pageCount = data['items'][item_idx]['volumeInfo']['pageCount']
                metadata['pageCount'] = pageCount
            except:
                #print("No pageCount found")
                pass

            # Rating might not exist
            try:
                averageRating = data['items'][item_idx]['volumeInfo']['averageRating']
                metadata['averageRating'] = averageRating
            except:
                #print("No rating found")
                pass

            break
        else:
            # print("No match for given ISBN!")
            pass
    

    # lowercase the categories to match the accepted_cat set
    book_cat = set([cat.lower() for cat in metadata['categories'] ])
    
    # If no matching isbn or no common elements between the 2 category sets, then the book is rejected
    if metadata['isbn-10'] == '' and metadata['isbn-13'] == '' or not (book_cat & accepted_cats):
        return False
    else:
        return metadata

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



#print(getBookMetadata('978-1-84749-308-8', '', ''))
# text = open('text.txt').read()
# print(findISBN(text))
