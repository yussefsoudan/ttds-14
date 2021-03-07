const mongodb = require('mongodb');
const MongoClient = mongodb.MongoClient;

var _db;

module.exports = {

  connectToServer: function(conn) {
    MongoClient.connect(conn.url, { useNewUrlParser: true, useUnifiedTopology: true }, function(err, client) {
      _db  = client.db(conn.dbName);
      console.log("Connection Successful");
      if (err) console.log(err);
    });
  },

  findInCollection: async function(col, query) {
    console.log("query: " + JSON.stringify(query))
    return _db.collection(col).findOne(query)
  },

};

// class MongoDB {
//     Database = {db: ''};

//     async connect(conn) {
//         try {
//           MongoClient.connect(conn.url, { useNewUrlParser: true }, (err, database) => {
//                 if (err) console.log(err);
//                 this.Database.db = database.db(conn.dbName);
//                 console.log("conn.dbName: " + conn.dbName);
//                 console.log("Mongo Connection successful.");
//             });
//         }
//         catch(err) {
//           console.log("Error caught: ", err);
//         }
//     }

//     // given a collection, find the query object
//     async findOne(col, query) {
//         return this.Database.db.collection(col).findOne(query) || {};
//     }

//     // findItem = function (item) {
//     //     console.log('finding');
//     //     MongoClient.connect(url, {useNewUrlParser: true, useUnifiedTopology: true}, (err, db) => {
//     //         if (err) throw err;

//     //         const dbo = db.db("shelf");
//     //         dbo.collection('compartment').findOne({item: item}).then((docs) => {
//     //             if (docs) {
//     //                 const location = docs.location;
//     //                 console.log("found this in MONGODB: " + JSON.stringify(location));
//     //                 this.Database.current_location = JSON.parse(JSON.stringify(location));
//     //             } else {
//     //                 this.Database.current_location = '';
//     //             }
//     //         }).catch((err) => {
//     //             console.log(err);
//     //         }).finally(() => {
//     //             db.close();
//     //         })
//     //     })
//     // };
// }

// module.exports = MongoDB;



