const fetch = require("node-fetch");
const fs = require('fs');
const badChars = new Set(['#','<','>','*','_',':','\n','@']);
const badWords = new Set(['copyright','.com','www','copyediting','of fiction','e-book','all rights reserved','published by','publisher','manuscript','editor','coincidental','reproduce','special thank']);
const MongoClient = require('mongodb').MongoClient;
const url = "mongodb://localhost";

let buildCollections = () => {
    let bookID = 0;
    let quoteID = 0;
    let directory = "../books";
    let folders = ['0_Other', '0'] // '1', '2']  ,'3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    let booksDeleted = 0;

    MongoClient.connect(url, { useUnifiedTopology : true }, function(err, client) {

        try {
            let booksCollec = client.db("TTDS").collection("books");
            let quotesCollec = client.db("TTDS").collection("quotes");

            for (i in folders) {
                let subdir = directory + '/' + folders[i];
                console.log(subdir)
                fs.readdir(subdir, function (err, files) {
                    if (err) console.error("Could not list the directory.", err, "In folder: ", folders[i]);
                    console.log("Files size: ", files.length)
                    files.forEach(function (filename, index) {
                        let filePath = subdir + '/' + filename; 
                        let authorIncluded = (filename.indexOf("-") > -1) ? true : false;
                        let title = (!authorIncluded) ? filename : filename.split("-")[0].trim();
                        let author = (!authorIncluded) ? false : filename.split("-")[1].split(".")[0].trim();
                        
                        fs.readFile(filePath, 'utf8', async function(err, text)  {
                            console.log("Reading file: ", filename)
                            if (err) console.error(err, " in book ", filename);
                            
                            let ISBN = findISBN(text); // Books without ISBN have already been removed
                            let bookMetadata = await getBookMetadata(ISBN, title, author, 3);
                            if (bookMetadata == undefined) {
                                console.log("API limit reached on book ", filename, " with ISBN: ", ISBN);
                            }

                            if (bookMetadata != false && bookMetadata != undefined) {
                                // Insert book
                                bookMetadata["_id"] = bookID;
                                bookID += 1;
                                booksCollec.insertOne(bookMetadata, function(err, res) {
                                    if (err) console.log("Error inserting book: ", err, " in book ", filename);
                                })

                                // Insert quotes 
                                let quotes = getQuotes(text);
                                for (q in quotes) {
                                    let quote = quotes[q];
                                    quoteDoc = {"book_id" : (bookID), "quote" : quote};
                                    quoteDoc["_id"] = quoteID;
                                    quoteID += 1;
                                    quotesCollec.insertOne(quoteDoc, function(err, res) {
                                        if (err) console.log("Error inserting quote: ", err, " in book ", filename);
                                    });
                                }
                                
                            } else {
                                // The ISBN does NOT match the Google ISBNs or chosen categories, remove book.
                                fs.unlink(filePath, (err) => {
                                    if (err) {
                                      console.error(err, " in book ", filename)
                                      return
                                    }
                                    // file removed
                                    booksDeleted += 1;
                                });
                            }
                        }); 
                    });
                }); 
            }
        } catch(err) {
            console.log(err);
        }
        finally {
            console.log("Done building the collections. Books deleted: ", booksDeleted);
        }
        
    });

};

let getBookMetadata = async (ISBN, title, author, max_tries) => {
    let URL = "https://www.googleapis.com/books/v1/volumes?q=isbn";
    let APIKey = "&key=AIzaSyDxE-bNMbTHHWaxU9bW78hV3qGPFFW-qZM";
    ISBN = ISBN.replace(/\s|:|-/gi, '');
    let metadata = {'title' : title, 
    'authors' : [author], 
    'isbn-10' : '', 
    'isbn-13' : '',
    'categories' : [], 
    'thumbnail' : '', 
    'publishedDate' : '',
    'previewLink' : '',
    'pageCount' : '',
    'averageRating' : ''}; 
    let endpoint = URL + ISBN + APIKey;
    let accepted_cats = new Set(['fiction','biography & autobiography','juvenile fiction','poetry','young adult fiction',
                     'philosophy','young adult nonfiction','true crime','indic fiction (english)']);
    
    
    return fetch(endpoint)
    .then(response => response.json())
    .then(data => {
        let items = data['totalItems'];
        if (items > 0) {
            let item_idx = 0;
            for (let i = 0; i < items; i++) {
                let isbn10 = '';
                let isbn13 = '';
                try {
                    isbn10 = data['items'][i]['volumeInfo']['industryIdentifiers'][0]['identifier'];
                } catch(err) {}
                try {
                    isbn13 = data['items'][i]['volumeInfo']['industryIdentifiers'][1]['identifier'];
                } catch(err) {}
                
                if (ISBN == isbn10 || ISBN == isbn13) {
                    item_idx = i;
                    metadata['isbn-10'] = isbn10;
                    metadata['isbn-13'] = isbn13;
                    break;
                }
            }
            
            try {
                metadata['title'] = data['items'][item_idx]['volumeInfo']['title'] || title;
            } catch(err) {
                metadata['title'] = title;
            }
            
            try {
                metadata['authors'] = data['items'][item_idx]['volumeInfo']['authors'] || [author];
            } catch(err) {
                metadata['authors'] = [author]
            }
            
            try {
                metadata['categories'] = data['items'][item_idx]['volumeInfo']['categories'] || [];
            } catch(err) {
                metadata['categories'] = [];
            }

            try {
                metadata['publishedDate'] = data['items'][item_idx]['volumeInfo']['publishedDate'] || '';
            } catch(err) {
                metadata['publishedDate'] = '';
            }
            
            try {
                metadata['thumbnail'] = data['items'][item_idx]['volumeInfo']['imageLinks']['thumbnail'] || '';
            } catch(err) {
                metadata['thumbnail'] = '';
            }
            
            try {
                metadata['previewLink'] = data['items'][item_idx]['volumeInfo']['previewLink'] || '';
            } catch(err) {
                metadata['previewLink'] = '';
            }
            
            try {
                metadata['pageCount'] = data['items'][item_idx]['volumeInfo']['pageCount'] || ''; 
            } catch(err) {
                metadata['pageCount'] = '';
            }
            
            try {
                metadata['averageRating'] = data['items'][item_idx]['volumeInfo']['averageRating'] || '';
            } catch(err) {
                metadata['averageRating'] = '';
            }
            
            if (metadata['categories'].length > 0) {
                let book_cat = new Set(metadata['categories'].map(x => x.toLowerCase()));
                let intersection = new Set([...book_cat].filter(x => accepted_cats.has(x)));
                if ((metadata['isbn-10'] == '' && metadata['isbn-13'] == '') || intersection.size == 0) {
                    return false;
                } else {
                    if (metadata == undefined) console.log("undefined is", ISBN);
                    return metadata;
                }
            } else {
                return false;
            }      
        } else {
            return false;
        }
    
    }).catch((err) => {
        console.log("here for ", ISBN);
        if (max_tries > 0) {
            return getBookMetadata(ISBN, title, author, max_tries - 1);
        } else {
            return false;
        }
    });
} 
    

let findISBN = (text) => {
    // Try first with 'ISBN' included
    const regex0 = /(?:ISBN(?:-1[03])?:? ?)(?:978(?:-|\s)?|979(?:-|\s)?)?(?:[0-9]{1,5}(?:-|\s)?)(?:[0-9]{1,7}(?:-|\s)?)(?:[0-9]{1,6}(?:-|\s)?)(?:[0-9X]{1}(?:-|\s)?)/gm;
    // Try without 'ISBN' and hyphen seperated
    const regex1 = /(?:978(?:-)?|979(?:-)?)?(?:[0-9]{1,5}(?:-))(?:[0-9]{1,7}(?:-))(?:[0-9]{1,6}(?:-))(?:[0-9X]{1})/gm;
    // Try without 'ISBN' and not seperated (must be of length 10 or 13; if 13, must start with 978 or 979)
    const regex2 = /(?:978|979)?(?:[0-9]{9})(?:[0-9X]{1})/gm;
    // Try without 'ISBN' and space seperated and ISBN-13 ONLY (sacrifice space seperated 10)
    const regex3 = /(?:978\s|979\s)(?:[0-9]{1,5}\s)(?:[0-9]{1,7}\s)(?:[0-9]{1,6}\s)(?:[0-9X]{1})/gm;

    let search0 = text.match(regex0) || [];
    if (search0.length > 0) {
        let match0 = search0[0];
        if (match0.indexOf(":") > -1) {
            return match0.split(":")[1].trim(); 
        } else {
            return match0.split("ISBN")[1].trim();
        }
    }
    let search1 = text.match(regex1) || [];
    if (search1.length > 0) {
        let match1 = search1[0];
        return match1;
    }
    let search2 = text.match(regex2) || [];
    if (search2.length > 0) {
        let match2 = search2[0];
        return match2;
    }
    let search3 = text.match(regex3) || [];
    if (search3.length > 0) {
        let match3 = search3[0];
        return match3; 
    }

    return false;
};

let getQuotes = (text) => {
    let quotes = [];
    let paragraphs = text.split("\n\n");
    // A quote is a paragraph with at least 10 words that doesnt include bad chars/words or thank you multiple times 
    for (i in paragraphs) {
        let par = paragraphs[i];
        let foundBadChar = false;
        let foundBadWord = false;

        for (j in par) {
            let char = par[j];
            if (badChars.has(char)) {
                foundBadChar = true;
                break;
            }
        }

        let words = par.split().map(x => x.toLowerCase());
        for (w in words) {
            let word = words[w];
            if (badWords.has(word)) {
                foundBadWord = true;
                break;
            }
        }

        let thankYouCount = (par.split().map(x => x.toLowerCase()).join().match(/thank/gm) || []).length;
        let matches = par.match(/\w+/gm) || [];
        if (matches.length >= 10 && !foundBadWord && !foundBadChar && thankYouCount < 3) {
            quotes.push(par);
        }

    }

    return quotes;
}

let run = async () => {
    let start = new Date().getTime();
    try {
        buildCollections();
    } catch(err) {
        console.log("Error in buildCollections(): ", err);
    }
    
    let end = new Date().getTime();
    console.log("Finished building collections in ", (end - start) / 1000, " seconds");
}

run();

