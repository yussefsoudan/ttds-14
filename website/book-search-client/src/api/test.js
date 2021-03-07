const axios = require('axios');
const testURL = 'http://127.0.0.1:5000/';

const test = async() => {
    return axios.get(testURL,{
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
