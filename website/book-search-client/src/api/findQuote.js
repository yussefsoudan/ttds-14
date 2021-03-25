const axios = require('axios');
// const findQuoteURL = 'http://localhost:9000/findQuote';
const findQuoteURL = 'https://188.166.173.191:5000/quote_from_id';

const findQuote = async(quoteId) => {
    return axios.post(findQuoteURL,{
        _id: quoteId,
        responseType: 'json'
    })
    .then(response => {
        console.log("res in callAPI is: " + JSON.stringify(response));
        return response.data;
      })
    .catch(error => {
        throw error;
    });   
}

export default findQuote;


