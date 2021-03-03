const fs = require('fs').promises;
const MongoClient = require('mongodb').MongoClient;
const url = "mongodb://localhost";
const subdir = "/root/index";

let writeIndex = async () => {
    let client = await MongoClient.connect(url, { useUnifiedTopology : true});
    let invertedIndex = client.db("TTDS").collection("invertedIndex");
    let files = await fs.readdir(subdir);

    try {
        // Read each file and write it to Mongo
        for (let idx = 0; idx < files.length; idx++) { 
            let filename = files[idx];
            let filePath = subdir + '/' + filename; 

            let dictText = await fs.readFile(filePath, 'utf-8');
            
            if (dictText.length > 3) {
                
                let dict = await JSON.parse(dictText);
                if (dict.length == 0) {
                    console.log(dictText);
                    return;
                }
                invertedIndex.insertMany(dict, (err, res) => {
                    if (err) {
                        console.log(`Error occured whilse inserting ${filePath}: `, err);
                    }
                });
            }
        }
    } finally {

        // Create Indices
        await invertedIndex.createIndex({"term" : 1});
        await invertedIndex.createIndex({"books._id" : 1});
        await invertedIndex.createIndex({"books.quotes._id" : 1});
    }
}

let run = async () => {
    let start = new Date().getTime();
    try {
        await writeIndex();
    } catch(err) {
        console.log("Error in writeIndex(): ", err);
    }
    
    let end = new Date().getTime();
    let seconds = (end - start) / 1000;
    let minutes = seconds / 60;
    console.log("Finished writing index in ", seconds , " seconds or ", minutes, " minutes.");
}

run();