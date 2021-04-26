# Books & Book Quotes Search Engine
This is a group project for the 2020-2021 iteration of the Text Technologies for Data Science course.

The search engine is a system that finds books, book quotes and book details for a particular set of books. The book dataset consists of 24,985 books, from which there are 40,999,867 quotes. The search engine uses two inverted index structures to provide quote search, strict phrase search and booksearch functionalities. For a quote query, the system returns the most relevant quotes,  their contexts and theirbook details; the relevant quotes will be ranked with respect to their BM-25 score.  For a book query, the system returns the most relevant books using terms appearing in the book title; the relevant quotes will be ranked with respect to their TF-IDF score. We implement the search engine in the form of a web application, with the frontend providing the user interface and the backend responsible for querying the database and ranking the results. 

A demo of the webapp can be found [here](https://drive.google.com/file/d/1w3cD81nfz_1SGpfA0O4bskncNYek-JAM/view?usp=sharing)
