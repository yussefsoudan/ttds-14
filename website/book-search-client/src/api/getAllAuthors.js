const axios = require('axios');
// const findQuoteURL = 'http://localhost:9000/findQuote';
const getAuthorsURL = 'https://ttds-14.herokuapp.com//get_all_authors';

const getAllAuthors = async() => {
    return axios.post(getAuthorsURL,{
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

export default getAllAuthors;


