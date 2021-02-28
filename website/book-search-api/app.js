// Express configuration
var express = require("express"),
    testAPI = require("./routes/testAPI");

// Constants
const bodyParser = require('body-parser');
const cors = require('cors');
// const path = require('path');
// const config = require('./local/config');

// Configure routes
var app = express();
app.use(cors());
app.use(bodyParser.urlencoded({extended: false}));
app.use(bodyParser.json());
app.use(express.static(__dirname + '/public'));
// app.use(express.static(__dirname + '/public/scripts'));
app.use("/testAPI", testAPI);


app.options("/*", function (req, res, next) {
    res.header('Access-Control-Allow-Origin', 'http://localhost:5000');
    res.header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS');
    res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization, Content-Length, X-Requested-With', 'application/json');
    req.header('mode', 'no-cors');
    res.sendStatus(200);
});


app.get('/', function (req, res) {
    res.render('index', { title: 'Express' });
});


app.listen(9000, () => {
    console.log("Server running on port 9000");
});




