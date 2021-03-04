# Data Gathering and Index Building
The following is a breakdown of the process of gathering the books used in this project as well as a rough overview on the scripts used to build collections and an inverted hierarchical index from such data. 

## Data Gathering
We were quite fortunate to have came across a [public 196,640 .txt books dataset](https://github.com/soskek/bookcorpus/issues/27#issuecomment-716104208) curated by  [shawwn](https://github.com/shawwn) and [the-eye.eu](https://the-eye.eu/).  The books were downloaded on the DigitalOcean droplet, taking 108GB of disk space when unzipped. 

## Data Filtering 
After running the `deleteSomeBooks.py` script, books meeting the following criteria are deleted:

 - Non-English books
 - Books containing no ISBN
 - Empty books

This deletes roughly 20,000 books, leaving roughly 175,000 books.

When running the `buildCollections.js` script (discussed in the following subsection) the following books are also deleted:

 - Books with an ISBN not matching any of the Google Books API ISBNs
 - Books **NOT** in the following genres:
	 - `['fiction','biography & autobiography','juvenile fiction','poetry','young adult fiction','philosophy','young adult nonfiction','true crime','indic fiction (english)']`

This leaves us with only *30,630 books*.

## Collection Building
There are two collections (apart from the index; see the next subsection) that were built directly from the filtered dataset of the 30,630 books using the `buildCollections.js` script.  The following two collections occupy roughly 13GB of disk space. 

### `books`
The `books` collection has 30,630 documents of the following form:
```
{
	"_id":11,
	"title":"Xunzi",
	"authors":["Burton Watson"],
	"isbn-10":"9780231521314",
	"isbn-13":"0231521316",
	"categories": ["Philosophy"],
	"thumbnail":"http://books.google.com/books/content?id=0SE2AAAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
	"publishedDate":"2003-05-21",
	"previewLink":"http://books.google.co.uk/books?id=0SE2AAAAQBAJ&printsec=frontcover&dq=isbn9780231521314&hl=&cd=4&source=gbs_api",
	"pageCount":160,"averageRating":""
}
```
Each `books` document contains metadata about the book obtained from the Google Books API. 

### `quotes`
The `quotes` collection has 50,630,265 documents of the following form:
```
{	
	"_id":14581,
	"book_id":11,
	"quote":"Whereas Cyrus treated the peoples he conquered with deep respect, Alexander sometimes urged his soldiers to put civilian populations to the sword. As his domains widened, Alexander increasingly gave himself over to tyrannical methods and monstrous egotism. Had any of Cyrus' generals acted with a cruelty equal to Alexander's, he would have been relieved of his duties immediately."
}
```
The `buildCollections.js` script builds the `quotes` collection from the .txt files as follows:

 - Each quote is obtained by splitting on `\n\n`, making each quote a paragraph.
 - Those quotes are only added to the `quotes` collection if they meet the following criteria:
	 - It contains at least 10 alphanumeric characters.
	 - It does NOT include any of the following words or characters:
		 - `['#','<','>','*','_',':','\n','@','copyright','.com','www','copyediting','of fiction','e-book','all rights reserved','published by',
'publisher','manuscript','editor','coincidental','reproduce','special thank']`
	 - It does NOT include the word 'thank' more than 2 times (to avoid including thank-you notes). 


## Index Building
The `invertedIndex` collection contains 10,267,545 documents (occuping 23GB of disk space) and it represents an inverted heirarchical index that maps each term to the books it appears in to the quotes that appear in each book to the positions of the term in each such quote. Each document takes the following form: 

```
{	
	"_id": ObjectId("6040b3b44600b73f8ca43cde"),
	"term":"conquer",
	"term_freq": 22,
	"books":[
		{
		  "_id":11,
		  "term_freq_in_book":13,
		  "quotes": [
		    {"_id":14576,"len":45,"pos":[16]},
		    .
		    .
		    ]
		 },
		 .
		 .
		]
}
```

The droplet used to build the index has 160GB of disk space and 8GB of memory.
The following are the challenges presented to us by the limitations of our resources:
 

 1. Creating a document for each term  was not possible due to the MongoDB limit of 16MB per document. 
 2. Iterating through the quotes, creating the `invertedIndex` documents and writing them to MongoDB (or updating already existing MongoDB documents) with them was not possible. This is because performing an insert or update operation multiple times for each of the 50,630,265 quotes would have roughly taken 28 days in the best case. 
 
We have catered for both of those challenges in the process of building the `invertedIndex` collection. The process is two-fold:

### Stage 1: Make the Documents and Write them to Disk
The first stage is executed by the `db/index_building/py/buildIndex.py` script. As we cannot build the index whilst scanning through batches of the quotes, the following approach was adopted:

 1. Load in memory 1000 `quotes` documents at a time.
 2. Use the those quotes to build a temporary index (in a `tempIndex = dict()` variable).
	 - Preprocess each term by case-folding, removing if a stop word or if it is not an alphanumeric and then stem. 
	 - Update the `tempIndex`. 
 3. Every 200,000 quotes, we write the `tempIndex` documents to disk.   
 4. Garbage collect and clear variables, then return to step 1. 

This divides the whole index into 200 disk files or batches. This means that each term can have a maximum of 200 documents. As quotes here are paragraphs, splitting the index into 200 files on disk was the best we can do given the memory limitations. Any lesser split and the script would crash because `tempIndex` was getting too large.

### Stage 2: Load Index Disk Batches; Write them to Mongo
The second stage is executed by the `db/index_building/py/writeIndexToMongo.py` script. 

 1. Load each of the 200 index batch files.
 2. Use the `insert_many` MongoDB operation to write the documents of each file.
 3. Garbage collect and clear variables, then return to step 1. 

### Notes
When querying the index, caution must be exercised in taking all of the documents for each term into account when,  for instance, trying to obtain the overall term frequency since there could be up to 200 documents for each term. 

Notice that you would find the equivalent of the previous two scripts written in Javascript inside `db/index_building/js/`.  These scripts failed to create the index due to always running out of memory due to the lack of any control given to the programmer on the process of garbage collection. The Python scripts would similarily run out of memory if we fail to include `.clear()` or `gc.collect()` for clearing used memory. 





