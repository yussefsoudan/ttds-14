const axios = require('axios');
const getBooksURL = 'http://0.0.0.0:5000/books_from_terms_list';

const getBooksFromTerms = async(terms) => {
    return axios.post(getBooksURL,{
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

export default getBooksFromTerms;


