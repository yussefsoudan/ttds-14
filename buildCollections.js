const fetch = require("node-fetch");
const fs = require('fs');
const badChars = new Set(['#','<','>','*','_',':','\n','@']);
const badWords = new Set(['copyright','.com','www','copyediting','of fiction','e-book','all rights reserved','published by','publisher','manuscript','editor','coincidental','reproduce','special thank', 'inc.']);
const introductoryWords = new Set([/^(^|[^a-z0-9]*)introduction($|[^a-z0-9]*)$/gm, /(^|[^a-z0-9]*)preface($|[^a-z0-9]*)$/gm, /(^|[^a-z0-9]*)prologue($|[^a-z0-9]*)$/gm, /(chapter|part|^)[^a-z0-9]*1([^a-z0-9]*|$)$/gm, /(chapter|part|^)[^a-z0-9]*one([^a-z0-9]*|$)$/gm, /(chapter|part|^)([^a-z0-9]*|^)i([^a-z0-9]*|$)$/, /^([^a-z0-9]*)(1\.( )?)[a-z]*([^0-9]*|$)$/gm]);
const MongoClient = require('mongodb').MongoClient;
// const url = "mongodb://localhost";
const url = "mongodb://localhost:27017";

let buildCollections = () => {
    let bookID = 0;
    let quoteID = 0;
    let directory = "/Users/humuyao/Downloads/Book3";
    let folders = ['7'];
    let booksDeleted = 0;

    MongoClient.connect(url, function(err, client) {
        if (err) console.error("connection error. ", err);
        let booksCollec = client.db("TTDS").collection("books");
        let quotesCollec = client.db("TTDS").collection("quotes");

        for (i in folders) {
            let subdir = directory + '/' + folders[i] + '/';
            fs.readdir(subdir, function (err, files) {
                if (err) console.error("Could not list the directory.", err);

                files.forEach(function (filename, index) { 
                    console.log("book: " + filename)
                    let filePath = subdir + '/' + filename; 
                    let authorIncluded = (filename.indexOf("-") > -1) ? true : false;
                    let title = (!authorIncluded) ? filename : filename.split("-")[0].trim();
                    let author = (!authorIncluded) ? false : filename.split("-")[1].split(".")[0].trim();
                    
                    fs.readFile(filePath, 'utf8' , async function(err, text)  {
                        if (err) console.error(err);
                        
                        let ISBN = findISBN(text); // Books without ISBN have already been removed
                        let bookMetadata = await getBookMetadata(ISBN, title, author, 3);
                        if (bookMetadata == undefined) {
                            console.log("API limit reached", ISBN);
                        }

                        if (bookMetadata != false && bookMetadata != undefined) {
                            // Insert book
                            bookMetadata["_id"] = "b" + bookID;
                            console.log("bookMetadata (inserted into book collection): " + JSON.stringify(bookMetadata))
                            bookID += 1;
                            booksCollec.insertOne(bookMetadata, function(err, res) {
                                if (err) console.log("Error inserting book: ", err);
                            })

                            // Insert quotes 
                            let quotes = getQuotes(text);
                            for (q in quotes) {
                                let quote = quotes[q];
                                quoteDoc = {"book_id" : ("b" + bookID), "quote" : quote};
                                quoteDoc["_id"] = "q" + quoteID;
                                // console.log("quoteDoc (inserted into quote collection): " + JSON.stringify(quoteDoc))
                                quoteID += 1;
                                quotesCollec.insertOne(quoteDoc, function(err, res) {
                                    if (err) console.log("Error inserting quote: ", err);
                                });
                            }
                            
                        } else {
                            // The ISBN does NOT match the Google ISBNs or chosen categories, remove book.
                            // fs.unlink(filePath, (err) => {
                            //     if (err) {
                            //       console.error(err)
                            //       return
                            //     }
                            
                            //     // file removed
                            // });
                            booksDeleted += 1;
                            console.log("books deleted: " + booksDeleted)
                        }
                    }); 
                    console.log()
                });
            });
        }
    });

};

let getBookMetadata = async (ISBN, title, author, max_tries) => {
    let URL = "https://www.googleapis.com/books/v1/volumes?q=isbn";
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
    let endpoint = URL + ISBN
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

let removeUntilIntroduction = (text) => {
    let textByLines = text.split("\n");
    let lineCount = 0;
    let beginWordsDict = {};

    for (i in textByLines) {
        line = textByLines[i];
        if (line) {
            lineCount += 1;
            // line = line.map(x => toLowerCase(x));
            // console.log("line considered is: " + line);
        } else {
            continue;
        }

        if (lineCount >= 200) {
            break;
        }

        for (let word of introductoryWords) {
            // console.log("finding word: " + word);

            let search = line.match(word) || [];
            // console.log("search is: " + search);
            if (search.length > 0) {
                let rawMatch = search[0];
                
                // [^\w\s] is anything that's not a digit, letter, whitespace, or underscore.
                // [^\w\s]|_ is the same as ^ except including underscores.
                let match = rawMatch.replace(/[^\w\s]|_/g,"").toLowerCase().trim();

                // console.log("matching introductory word is: " + match);

                if (match in beginWordsDict) {
                    beginWordsDict[match].push(parseInt(i));
                } else {
                    beginWordsDict[match] = [parseInt(i)];
                }
                
                break;
            }
        }
    }

    console.log("beginWordsDict: " + JSON.stringify(beginWordsDict));

    // find a line number to read from
    let readFrom = 0;

    // if only one introductory word has appeared, start reading from that line
    if (Object.keys(beginWordsDict).length == 1) {
        let key = Object.keys(beginWordsDict)[0];
        // console.log("key is: " + key)
        // console.log("list being fed: " + beginWordsDict[key])
        readFrom = Math.max(...beginWordsDict[key]);
    } 
    // more than one introductory word has appeared
    else if (Object.keys(beginWordsDict).length > 1) {
        // all values (of key-value pairs) of the dictionary are single elem lists
        // i.e. multiple introductory words have appeared, but they all appear only once
        let allSingle = true;
        
        // all values (of key-value pairs) of the dictionary are multiple elem lists
        // i.e. multiple introductory words have appeared, but they all appear multiple times (usually twice)
        let allMulti = true;

        for (key in beginWordsDict) {
            if (beginWordsDict[key].length == 1) {
                allMulti = false;
            }  
            if (beginWordsDict[key].length > 1) {
                allSingle = false;
            }   
        }

        // this means there are keys with single elem lists AND ALSO keys with multiple elem lists
        // i.e. some introductory words appear once, some appeared more than once
        if (!allSingle && !allMulti) {
            for (key in beginWordsDict) {
                // only considering lists with 2 elements

                if (beginWordsDict[key].length == 2) {
                    // idea: start reading from the latest appearance of the earlier introductory word
                    // e.g. 
                    
                    // Contents Page
                    // -------------
                    // INTRODUCTION
                    // Chapter 1
                    // _____________
                    
                    // - actual book
                    // INTRODUCTION (start reading from here)

                    if (readFrom == 0) {
                        readFrom = Math.max(...beginWordsDict[key]);
                    } else {
                        readFrom = Math.min(...[Math.max(...beginWordsDict[key]), readFrom]);
                    }
                }

            }
        } 

        // all keys in dictionary have one elem lists
        else if (allSingle) {
            // idea: read the latest appearing introductory word
            // e.g.
                
            // Preface
            // Introduction
            // Chapter 1 (start reading from here)

            console.log("all keys in dictionary have one elem lists!");
            helper = []
            for (key in beginWordsDict) {
                helper.push(beginWordsDict[key]);
            }
            console.log("helper: " + helper);
            readFrom = Math.max(...helper);
        } 

        // all keys in dictionary have multiple elem lists
        else if (allMulti) {
            // idea: start reading from the latest appearance of the earlier introductory word
            // e.g. 
            
            // Contents Page
            // -------------
            //  INTRODUCTION
            //  Chapter 1
            //  _____________

            //  - actual book
            //  INTRODUCTION (start reading from here)
            //  Chapter 1

            helper = [];
            for (key in beginWordsDict) {
                helper.push(Math.max(...beginWordsDict[key]));
            }
            readFrom = Math.min(...helper);
        }  
    }   

    console.log("readFrom: " + readFrom);
    let newTextArray = textByLines.slice(readFrom);
    let newText = newTextArray.join("\n");
    return newText;
}

let getQuotes = (text) => {
    let quotes = [];
    let newText = removeUntilIntroduction(text)
    let paragraphs = newText.split("\n\n");
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
        
        // let words = par.split().map(x => x.toLowerCase());
        // for (w in words) {
        //     let word = words[w];
        //     if (badWords.has(word)) {
        //         foundBadWord = true;
        //         break;
        //     }
        // }

        for (let badWord of badWords) {
            // let badWord = badWords[w];
            if (par.toLowerCase().includes(badWord)) {
                // console.log("par which has badWord is: " + par)
                // console.log("badWord is: " + badWord)
                console.log()
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



buildCollections()
