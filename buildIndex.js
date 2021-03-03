const fs = require('fs').promises;
const MongoClient = require('mongodb').MongoClient;
const url = "mongodb://localhost";
const stemmer = require('porter-stemmer').stemmer;

let buildIndex = async () => {
    let text = await fs.readFile('./nltk_stop_words.txt', 'utf8'); 
    let stopWords = new Set(text.split("\n"));
    let client = await MongoClient.connect(url);
    try {
        let quotesCollec = client.db("TTDS").collection("quotes");
        let numOfQuotes = await client.db("TTDS").collection("quotes").countDocuments();
        let invertedIndex = client.db("TTDS").collection("invertedIndex");
        let index = 0;

        // Load 5000 quotes in memory at a time
        for (let q_id_count = 5000; q_id_count <= numOfQuotes; q_id_count += 5000) { 
            let lowerLimit = q_id_count-5000;
            let upperLimit = q_id_count;
            let results = await quotesCollec.find({"_id" : {"$lt" : upperLimit, "$gte" : lowerLimit}}).toArray();

            for (i in results) {
                let quote = results[i];
                let q_id = quote['_id'];
                let b_id = quote['book_id'];
                let terms = await preprocess(quote['quote'], stopWords);
                for (pos in terms) {
                    let term = terms[pos];
                    let doc = {};
                    let queryResult = await invertedIndex.find({'term' : term}).toArray();
                    // Insert new docu when it's a unique term or last document containing term has term_freq of > 200.
                    if (queryResult.length == 0 || queryResult[queryResult.length - 1]['term_freq'] > 200) { // 
                        doc['_id'] = index;
                        doc['term'] = term;
                        doc['term_freq'] = 1; // num of times term occurs across all quotes
                        quote_obj = {'_id' : q_id, 'len' : terms.length, 'pos' : [pos] }
                        book_obj = {'_id' : b_id, 'term_freq_in_book': 1, 'quotes' : []}
                        doc['books'] = [];
                        doc['books'].push(book_obj);
                        doc['books'][0]['quotes'] = [];
                        doc['books'][0]['quotes'].push(quote_obj);
    
                        await invertedIndex.insertOne(doc);
                        index += 1;
    
                        if (index == 1) {
                            // Non-unique index!
                            invertedIndex.createIndex({"term" : 1});
                        }
                    } 
                    else { // Term already exists 
                        // Update the last entry
                        doc = queryResult[queryResult.length - 1];
                        let docID = doc['_id']
                        let val = doc['term_freq'] + 1; 
                        invertedIndex.updateOne({'_id' : docID}, {$set : { 'term_freq': val}})
    
                        // Term already occured in this book
                        let b_arr_id = idInArray(doc['books'], b_id);
                        if (b_arr_id > -1) {
                            let obj = {};
                            let key = `books.${b_arr_id}.term_freq_in_book`;
                            let val = doc['books'][b_arr_id]['term_freq_in_book'] + 1;
                            obj[key] = val;
                            invertedIndex.updateOne({'term' : term}, {$set : obj});
    
                            // Term already occured in this particular quote
                            let q_arr_id = idInArray(doc['books'][b_arr_id]['quotes'], q_id)
                            if (q_arr_id > -1) {
                                let obj = {};
                                let key = `books.${b_arr_id}.quotes.${q_arr_id}.pos`;
                                obj[key] = pos;
                                invertedIndex.updateOne({'_id' : docID}, {$push : obj})
                            } // Term appeared in a new quote in this book
                            else {
                                let obj = {}
                                let key = `books.${b_arr_id}.quotes`;
                                let val = {'_id' : q_id, 'len' : terms.length, 'pos' : [pos]};
                                obj[key] = val;
                                invertedIndex.updateOne({'_id' : docID}, {$push : obj});
                            }
                            
                        } // First time term occurs in this book
                        else {
                            let obj =  {};
                            let key = `books`;
                            let val = {
                                '_id' : b_id,
                                'term_freq_in_book': 1, 
                                'quotes' : [
                                    {'_id': q_id, 'len' : terms.length, 'pos' : [pos]}
                                ]
                            };
                            obj[key] = val;
                            invertedIndex.updateOne({'_id' : docID}, {$push : obj});
                        }
                    }
                }
            } 
            console.log("Processed ", q_id_count, "quotes out of ", numOfQuotes);
        }    
    } finally {
        await client.db("TTDS").collection("invertedIndex").createIndex({"books._id" : 1});
        await client.db("TTDS").collection("invertedIndex").createIndex({"books.quotes._id" : 1});
        console.log("Done. Press 'ctrl + c' to stop the program.")
    }
};

let preprocess = async (quote, stopWords) => {
    let final = [];
    let tokens = quote.match(/\w+/gm);
    for (i in tokens) {
        let token = tokens[i].toLowerCase();
        if (!stopWords.has(token)) {
            final.push(stemmer(token));
        }
    }
    return final;
}

let idInArray = (arr, id) => {
    for(let i = 0; i < arr.length; i++) {
        if (arr[i]['_id'] == id) {
            return i;
        }
    }
    return -1;
}

let run = async () => {
    let start = new Date().getTime();
    try {
        await buildIndex();
    } catch(err) {
        console.log("Error in buildIndex(): ", err);
    }
    
    let end = new Date().getTime();
    let seconds = (end - start) / 1000;
    let minutes = seconds / 60;
    console.log("Finished building index in ", seconds , " seconds or ", minutes, " minutes.");
}

run();
