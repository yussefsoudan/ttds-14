import './App.css';
import SearchPage from "./views/SearchPage.js";
import React, { useState,useEffect } from "react";
import findQuote from "./api/findQuote.js";
import setUp from "./api/setUp.js"

function App(){
    const [state, setState] = useState({
        connectDB:{
            isLoading:false,
            error:""
        }
    });


    // useEffect(() => {
    //     const setUpRequest = async () => {
    //       setState({ ...state, connectDB: { ...state.connectDB, isLoading: true } });
    //       await setUp()
    //         .then(response => {
    //           console.log(response);
    //           setState({
    //             ...state,
    //             connectDB: {
    //               isLoading: false,
    //             }
    //           });
    //         })
    //         .catch(errorResponse => {
    //           setState({
    //             ...state,
    //             connectDB: { isLoading: false, error: errorResponse }
    //           });
    //         });
    //     };
    
    //     setUpRequest();
        
    //   }, []); // empty list of dependencies ensures the hooks is only called upon rendering of the component

    return(
        //TODO: Display different component in case of a db connection error 
        <div>
        <SearchPage/>
        </div>
    )
}
export default App;













// class App extends React.Component {
//   constructor(props) {
//       super(props);
//       this.state = { apiResponse: "" , quoteId: ""};
//       this.getQuoteId = this.getQuoteId.bind(this);
//       this.findQuote = this.findQuote.bind(this);
//       this.setApiResponse = this.setApiResponse.bind(this);
//   }

//   async callAPI(route, options) {
//     let quote = await fetch(`http://localhost:9000/${route}`, options);
//     let res = await quote.json();
//     console.log("res in callAPI is: " + JSON.stringify(res));
//     return res;
//   }

//   getQuoteId(event) {
//     this.setState({quoteId: event.target.value});
//   }

//   setApiResponse(res) {
//     // alert("res: " + res);
//     console.log("res in setAPIResponse: " + JSON.stringify(res));
//     this.setState({apiResponse: JSON.stringify(res.quote)});
//   }

//   async findQuote(event) {
//     event.preventDefault();
//     const requestOptions = {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({_id: this.state.quoteId})
//     };
//     let res = await this.callAPI("findQuote", requestOptions);
//     console.log("res in findQuote: " + JSON.stringify(res));
//     this.setApiResponse(res);
//   }

//   async componentDidMount() {
//     let res = await this.callAPI("setUp", {});
//     console.log(res);
//   }

//   render() {
//       return (
//           <div>
//               <SearchPage/>
//               <input type="text" value={this.state.quoteId} onChange={this.getQuoteId}></input>
//               <button onClick={this.findQuote}>Click me</button>
//               <p>{this.state.apiResponse}</p>
//           </div>
//       );
//   }
// }

