const axios = require('axios');
const getQuotesURL = 'http://127.0.0.1:5000/quotes_from_terms_list';

const getQuotesFromTerms = async(terms) => {
    return axios.post(getQuotesURL,{
        terms: terms,
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

export default getQuotesFromTerms;


