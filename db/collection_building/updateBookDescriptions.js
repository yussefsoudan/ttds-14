const fetch = require("node-fetch");
const MongoClient = require('mongodb').MongoClient;
const DB_PASS='thenittygrittyofELnitty'
const DB_USER='readerTTDS'
const DB_NAME='TTDS' 
const DB_HOST='188.166.173.191'
const PORT = '27017'
const url = `mongodb://${DB_USER}:${DB_PASS}@${DB_HOST}:${PORT}`;

let updateBooksWithDescriptions = async () => {
    let client = await MongoClient.connect(url, { useUnifiedTopology : true });
    let booksCollec = client.db("TTDS").collection("books");
    let numOfBooks = await booksCollec.countDocuments();

    for (let i = 0; i < numOfBooks; i += 1000) {
        let lowerLimit = i;
        let upperLimit = i + 1000;
        let books = await booksCollec.find({"_id" : {"$lt" : upperLimit, "$gte" : lowerLimit}}).toArray();

        for (j in books) {
            let book = books[j];
            if (book["description"] == null || book["description"] == undefined || book["description"] == "") {
                let ISBN = book['isbn-13'];
                if (ISBN == '') {
                    ISBN = book['isbn-10'];
                } 
                
                let description = await getBookDescription(ISBN, 5);
                if (description == null) {
                    description = "";
                }
                booksCollec.updateOne({"_id" : book['_id']}, {"$set" : {"description" : description}});
            }
            
        }

        console.log("Finished ", upperLimit);
    }

}

let getBookDescription = async (ISBN, max_tries) => {
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
                ratingsCount = data['items'][item_idx]['volumeInfo']['description'] || '';
            } catch(err) {
                ratingsCount = '';
            }

            if (description != '' && description != null) {
                return ratingsCount;
            } else {
                if (max_tries > 0) {
                    return getBookDescription(ISBN, max_tries - 1);
                } else {
                    return '';
                }
            }
    
        } else {
            return '';
        }
    
    }).catch((err) => {
        console.log("here for ", ISBN);
        if (max_tries > 0) {
            return getBookDescription(ISBN, max_tries - 1);
        } else {
            return '';
        }
    });
}

let run = async () => {
    let start = new Date().getTime();
    try {
        await updateBooksWithDescriptions();
    } catch(err) {
        console.log("Error in updateBooksWithDescriptions(): ", err);
    }
    
    let end = new Date().getTime();
    console.log("Finished updating books in ", (end - start) / 1000, " seconds");
}

run();