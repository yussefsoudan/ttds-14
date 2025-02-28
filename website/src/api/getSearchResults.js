const axios = require('axios');
const baseURL = 'http://188.166.173.191:5000';

const getSearchResults = async(endpoint, params) => {
    console.log("request endpoint",baseURL + endpoint)
    return axios.post(baseURL + endpoint,{
        quote: params.quote,
        author: params.author ,
        bookTitle: params.bookTitle, 
        genre: params.genre, 
        yearTo: params.yearTo, 
        yearFrom: params.yearFrom,
        minRating: params.minRating,
        responseType: 'json'
    })
    .then(response => {
        console.log("res in callAPI is: " + JSON.stringify(response));
        return response.data;
        // throw Error("This is an error message")
      })
    .catch(error => {
        throw error;
    });   
}

export default getSearchResults;


