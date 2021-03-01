var express = require("express");
var router = express.Router();
const mongoDB = require('../MongoDB');
const conf = require('../local/config');

router.get('/', function (req, res, next) {
    mongoDB.connectToServer(conf.mongoConfig);
});

module.exports = router;