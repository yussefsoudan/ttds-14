const axios = require('axios');
const setUpURL = 'http://localhost:5000/SetUp';

const setUp = async() => {
    return axios.get(setUpURL,{})
    .then(response => {
        console.log("res in callAPI is: " + JSON.stringify(response));
        return response.data;
      })
    .catch(error => {
        throw error;
    });   
}

export default setUp;


