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
        let invertedIndex = client.db("TTDS").collection("invertedIndex");

        let results = await quotesCollec.find({}).toArray();
        for (i in results) {
            let quote = results[i];
            let q_id = quote['_id'];
            let b_id = quote['book_id'];
            let terms = await preprocess(quote['quote'], stopWords);
            for (pos in terms) {
                let term = terms[pos];
                let doc = {};
                let queryResult = await invertedIndex.find({'_id' : term}).toArray();
                // Unique term
                if (queryResult.length == 0) {
                    doc['_id'] = term;
                    doc['term_freq'] = 1; // num of times term occurs across all quotes
                    quote_obj = {'len' : terms.length, 'pos' : [pos] }
                    book_obj = { 'term_freq_in_book': 1}
                    doc['books'] = {};
                    doc['books'][b_id] = book_obj;
                    doc['books'][b_id]['quotes'] = {};
                    doc['books'][b_id]['quotes'][q_id] = quote_obj;

                    invertedIndex.insertOne(doc, async function(err, res) {
                        if (err) console.log("Error inserting inverted index unique entry: ", err);
                    });
                } 
                else { // Term already exists 
                    // Each term should have one entry (for now)
                    doc = queryResult[0];
                    let val = doc['term_freq'] + 1;
                    invertedIndex.updateOne({'_id' : term}, {$set : { 'term_freq': val}});

                    // Term already occured in this book
                    if (Object.keys(doc['books']).indexOf(b_id) > -1) {
                        let obj = {};
                        let key =  `books.${b_id}.term_freq_in_book`;
                        let val = doc['books'][b_id]['term_freq_in_book'] + 1;
                        obj[key] = val;
                        invertedIndex.updateOne({'_id' : term}, {$set : obj});

                        // Term already occured in this particular quote
                        if (Object.keys(doc['books'][b_id]['quotes']).indexOf(q_id) > -1) {
                            let obj = {};
                            let key = `books.${b_id}.quotes.${q_id}.pos`;
                            obj[key] = pos;
                            invertedIndex.updateOne({'_id' : term}, {$push : obj})
                        } // Term appeared in a new quote in this book
                        else {
                            let obj = {}
                            let key = `books.${b_id}.quotes.${q_id}`;
                            let val = {'len' : terms.length, 'pos' : [pos]};
                            obj[key] = val;
                            invertedIndex.updateOne({'_id' : term}, {$set : obj});
                        }
                        
                    } // First time term occurs in this book
                    else {
                        let obj =  {};
                        let key = `books.${b_id}`;
                        let val = {
                            'term_freq_in_book': 1, 
                            'quotes' : {
                                q_id : {'len' : terms.length, 'pos' : [pos]}
                            }
                        };
                        obj[key] = val;
                        invertedIndex.updateOne({'_id' : term}, {$set : obj});
                    }
                }
            }
        } 
    } finally {
        client.close();
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

let run = async () => {
    let start = new Date().getTime();
    await buildIndex();
    let end = new Date().getTime();
    console.log(end - start);
}

run();