// Express configuration
let express = require("express"),
    setUp = require("./routes/setUp");
    findQuote = require("./routes/findQuote");
    
// Constants
const bodyParser = require('body-parser');
const cors = require('cors');

// Configure routes
let app = express();
app.use(cors());
app.use(bodyParser.urlencoded({extended: false}));
app.use(bodyParser.json());
app.use("/setUp", setUp);
app.use("/findQuote", findQuote);


app.options("/*", function (req, res, next) {
    res.header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS');
    res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization, Content-Length, X-Requested-With', 'application/json');
    req.header('mode', 'no-cors');
    res.sendStatus(200);
});


app.listen(9000, () => {
    console.log("Server running on port 9000");
});




