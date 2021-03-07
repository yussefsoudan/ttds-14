const axios = require('axios');
const findQuoteURL = 'http://localhost:9000/findQuote';




const findQuote = async(quoteId) => {
    return axios.post(findQuoteURL,{
        _id:quoteId
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


