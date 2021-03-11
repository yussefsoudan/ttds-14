const fetch = require("node-fetch");
const MongoClient = require('mongodb').MongoClient;
const url = "mongodb://localhost";

let updateBooksWithRatingsCount = async () => {
    let client = await MongoClient.connect(url, { useUnifiedTopology : true });
    let booksCollec = client.db("TTDS").collection("books");
    let numOfBooks = await booksCollec.countDocuments();

    for (let i = 0; i < numOfBooks; i += 1000) {
        let lowerLimit = i;
        let upperLimit = i + 1000;
        let books = await booksCollec.find({"_id" : {"$lt" : upperLimit, "$gte" : lowerLimit}}).toArray();

        for (j in books) {
            let book = books[j];
            let ISBN = book['isbn-13'];
            if (ISBN == '') {
                ISBN = book['isbn-10'];
            } 
            
            let ratingsCount = await getRatingsCount(ISBN, 3);
            if (ratingsCount == null) {
                ratingsCount = "";
            }
            booksCollec.updateOne({"_id" : book['_id']}, {"$set" : {"ratingsCount" : ratingsCount}});
        }

        console.log("Finished ", upperLimit);
    }

}

let getRatingsCount = async (ISBN, max_tries) => {
    let ratingsCount = "";
    let URL = "https://www.googleapis.com/books/v1/volumes?q=isbn";
    let endpoint = URL + ISBN;

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
                    break;
                }
            }
             
            try {
                ratingsCount = data['items'][item_idx]['volumeInfo']['ratingsCount'] || '';
            } catch(err) {
                ratingsCount = '';
            }

            if (ratingsCount != '' && ratingsCount != null) {
                return ratingsCount;
            }
    
        } else {
            return '';
        }
    
    }).catch((err) => {
        console.log("here for ", ISBN);
        if (max_tries > 0) {
            return getRatingsCount(ISBN, max_tries - 1);
        } else {
            return '';
        }
    });
}

let run = async () => {
    let start = new Date().getTime();
    try {
        await updateBooksWithRatingsCount();
    } catch(err) {
        console.log("Error in updateBooksWithRatingsCount(): ", err);
    }
    
    let end = new Date().getTime();
    console.log("Finished updating books in ", (end - start) / 1000, " seconds");
}

run();