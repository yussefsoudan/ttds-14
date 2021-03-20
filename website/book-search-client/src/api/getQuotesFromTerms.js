const axios = require('axios');
const getQuotesURL = 'https://ttds-14.herokuapp.com/quotes_from_terms_list';

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


