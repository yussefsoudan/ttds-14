const axios = require('axios');
const testURL = 'http://127.0.0.1:5000/quote-list';

axios.create({
    responseType: 'json'
  })

const test = async(quoteId) => {
    return axios.post(testURL,{ 
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

export default test;
