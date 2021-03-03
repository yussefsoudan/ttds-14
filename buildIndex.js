const fs = require('fs').promises;
const MongoClient = require('mongodb').MongoClient;
const url = "mongodb://localhost";
const stemmer = require('porter-stemmer').stemmer;

let buildIndex = async () => {
    let text = await fs.readFile('./nltk_stop_words.txt', 'utf8'); 
    let stopWords = new Set(text.split("\n"));
    let client = await MongoClient.connect(url, { useUnifiedTopology : true});
    let dict = {}

    try {
        let quotesCollec = client.db("TTDS").collection("quotes");
        let numOfQuotes = await client.db("TTDS").collection("quotes").countDocuments();
        let loadSize = 100000

        // Split ~57 million quotes into 570 groups
        for (let r = 0; r < 570; r++) {
            let lowerLimit = r * loadSize;
            let upperLimit = lowerLimit + loadSize;
            let quotes = await quotesCollec.find({"_id" : {"$lt" : upperLimit, "$gte" : lowerLimit}}).toArray();
            
            for (i in quotes) {
                let quote = quotes[i];
                let q_id = quote['_id'];
                let b_id = quote['book_id'];
                let terms = await preprocess(quote['quote'], stopWords);
                let uniqueTerms = Array.from(new Set(terms));

                for (j in uniqueTerms) {
                    let term = uniqueTerms[j];
                    let pos = getPositionsOfTerm(term, terms);
                    dict[term] = dict[term] || {'term' : term, 'term_freq' : 0, 'books' : {}};
                    dict[term]['term_freq'] += 1;
                    dict[term]['books'][b_id] = dict[term]['books'][b_id] || {'_id': b_id, 'term_freq_in_book': 0, 'quotes': []};
                    dict[term]['books'][b_id]['term_freq_in_book'] += 1;
                    dict[term]['books'][b_id]['quotes'].push({'_id' : q_id, 'len' : terms.length, 'pos': pos})
                }
            }

            if (r != 0 && r % 9 == 0) {
                // Turn movies objects into array
                let keys = Object.keys(dict);
                for (k in keys) {
                    let term = keys[k];
                    dict[term]['books'] = Object.values(dict[term]['books']);
                }

                let file = await fs.writeFile(`/root/index/load-${r-9}.json`, JSON.stringify(Object.values(dict)), 'utf-8');
                dict = {};
            }
        
            console.log("Processed ", upperLimit, "quotes out of ", numOfQuotes);
        }   

        // Turn movies objects into array
        let keys = Object.keys(dict);
        for (k in keys) {
            let term = keys[k];
            dict[term]['books'] = Object.values(dict[term]['books']);
        }

        let file = await fs.writeFile(`/root/index/final-load.json`, JSON.stringify(Object.values(dict)), 'utf-8');
        dict = {};

    } finally {
        console.log("Done. Press Ctrl + C to exit program.")
    }
};


let getPositionsOfTerm = (term, terms) => {
    let result = [];
    for (let i = 0; i < terms.length; i++) {
        if (term == terms[i]) {
            result.push(i);
        }
    }
    return result;
}

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
