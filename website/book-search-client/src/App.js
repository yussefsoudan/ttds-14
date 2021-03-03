import './App.css';
import SearchPage from "./views/SearchPage.js";
import React from "react";

class App extends React.Component {
  constructor(props) {
      super(props);
      this.state = { apiResponse: "" , quoteId: ""};
      this.getQuoteId = this.getQuoteId.bind(this);
      this.findQuote = this.findQuote.bind(this);
      this.setApiResponse = this.setApiResponse.bind(this);
  }

  async callAPI(route, options) {
    let quote = await fetch(`http://localhost:9000/${route}`, options);
    let res = await quote.json();
    console.log("res in callAPI is: " + JSON.stringify(res));
    return res;
  }

  getQuoteId(event) {
    this.setState({quoteId: event.target.value});
  }

  setApiResponse(res) {
    // alert("res: " + res);
    console.log("res in setAPIResponse: " + JSON.stringify(res));
    this.setState({apiResponse: JSON.stringify(res.quote)});
  }

  async findQuote(event) {
    event.preventDefault();
    const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({_id: this.state.quoteId})
    };
    let res = await this.callAPI("findQuote", requestOptions);
    console.log("res in findQuote: " + JSON.stringify(res));
    this.setApiResponse(res);
  }

  async componentDidMount() {
    let res = await this.callAPI("setUp", {});
    console.log(res);
  }

  render() {
      return (
          <div>
              <SearchPage/>
              <input type="text" value={this.state.quoteId} onChange={this.getQuoteId}></input>
              <button onClick={this.findQuote}>Click me</button>
              <p>{this.state.apiResponse}</p>
          </div>
      );
  }
}

export default App;
