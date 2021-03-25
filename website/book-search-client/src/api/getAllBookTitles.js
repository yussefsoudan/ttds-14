const axios = require('axios');
// const findQuoteURL = 'http://localhost:9000/findQuote';
const getBookTitlesURL = 'https://188.166.173.191:5000/get_all_book_titles';

const getAllBookTitles = async() => {
    return axios.post(getBookTitlesURL,{
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

export default getAllBookTitles;


