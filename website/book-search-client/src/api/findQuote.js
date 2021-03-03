const axios = require('axios');
const findQuoteURL = 'http://localhost:9000/findQuote';

const findQuote = async(quoteId) => {
    return axios.post(findQuoteURL,{
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

export default findQuote;



//   const findQuote =async (event) => {
//     event.preventDefault();
//     const requestOptions = {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({_id: state.quoteId})
//     };
//     let res = await callAPI("findQuote", requestOptions);
//     console.log("res in findQuote: " + JSON.stringify(res));
//     setApiResponse(res);
// }


// const callAPI = async (route, options) => {
//     let quote = await fetch(`http://localhost:9000/${route}`, options);
//     let res = await quote.json();
//     console.log("res in callAPI is: " + JSON.stringify(res));
//     return res;
// }