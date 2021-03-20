const axios = require('axios');
const baseURL = 'https://ttds-14.herokuapp.com';

const getSearchResults = async(endpoint, params) => {
    console.log("request endpoint",baseURL + endpoint)
    return axios.post(baseURL + endpoint,{
        terms: params.terms,
        author: params.author ,
        bookTitle: params.bookTitle, 
        genre: params.genre, 
        yearTo: params.yearTo, 
        yearFrom: params.yearFrom,
        responseType: 'json'
    })
    .then(response => {
        // console.log("res in callAPI is: " + JSON.stringify(response));
        return response.data;
      })
    .catch(error => {
        throw error;
    });   
}

export default getSearchResults;


