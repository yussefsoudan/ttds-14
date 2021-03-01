const express = require('express');
const router = express.Router();

const mongoDB = require('../MongoDB');
// let mongo = new mongoDB();

// find a quote using a number (quote ID)
router.post('/', async function (req, res) {
    console.log(`req.body._id: ${req.body._id}`)
    let quoteID = {_id: req.body._id};
    let quoteRes = await mongoDB.findInCollection("quotes", quoteID);
    let param = {"quote": quoteRes.quote};
    console.log("final param to be sent back is: " + JSON.stringify(param));
    res.json(param);
});

module.exports = router;