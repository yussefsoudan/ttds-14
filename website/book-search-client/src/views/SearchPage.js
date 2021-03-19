import React, {useState,useEffect} from 'react';
import AppBar from '@material-ui/core/AppBar';
import BookIcon from '@material-ui/icons/Book';
import Grid from '@material-ui/core/Grid';

import CssBaseline from '@material-ui/core/CssBaseline';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';
import Container from '@material-ui/core/Container';
import CircularProgress from '@material-ui/core/CircularProgress';


import ResultPage from "./ResultPage.js"
import getSearchResults from "../api/getSearchResults.js";
import SearchBar from "../components/SearchBar.js";


const useStyles = makeStyles((theme) => ({
  icon: {
    marginRight: theme.spacing(2),
  },
  cardGrid: {
    paddingTop: theme.spacing(8),
    paddingBottom: theme.spacing(8),
  },
  footer: {
    backgroundColor: theme.palette.background.paper,
    padding: theme.spacing(6),
  },
  margin: {
    margin: theme.spacing(1),
  },
  formControl: {
    margin: theme.spacing(1),
    minWidth: 120,
  },

}));


export default function SearchPage() {
  const classes = useStyles();

  const [state, setState] = useState({
    apiResponse: {
      books:[]
    } , 
    isLoading : false,
    requestError:"",
    success: false
  });

  console.log("Search page render")

/* 
Single handleRequest function that will trigger the proper API function based on the
type of search 
 */
  const handleRequest = async (searchInput) => {

    let {
      quote, 
      bookSearch,
      author ,
      bookTitle,
      genre,
      yearFrom,
      yearTo} = searchInput


    setState({ ...state, isLoading: true, requestError: "", apiResponse: "" });
    console.log(state.isLoading)
    
    let terms = quote.split(" ")
    await getSearchResults(
      bookSearch ? "/books_from_terms_list" : "/quotes_from_terms_list",

      {terms, author ,bookTitle, genre, yearFrom, yearTo}
      )
        .then(response => {
            // console.log("res in setAPIResponse: " + JSON.stringify(response));
            setState({
                ...state,
                isLoading: false,
                apiResponse: {
                  books : response.books}, // book object, might contain quote as well 
                requestError: "",
                success:true
            });
        })
        .catch(errorResponse => {
            setState({
                ...state,
                isLoading: false,
                requestError: errorResponse,
                apiResponse: {
                  quote:""
                }
            });
        });        
  }

  return (
    <React.Fragment>
      <CssBaseline />
      {/* <AppBar position="relative">
        <Toolbar>
          <BookIcon className={classes.icon} />
          <Typography variant="h6" color="inherit" noWrap>
            Book Search Engine
          </Typography>
        </Toolbar>
      </AppBar> */}
      <main>
        {/* Search bar including the Advance search options */}
        <SearchBar handleRequest={handleRequest}/>

        {/* Results container */}
        <Container className={classes.cardGrid} maxWidth="md">
          {/* Container to hold the results of the search  */}
          {state.isLoading
          ? ( <Grid container 
            // spacing={6}
             justify="center"   
             alignItems="center" 
             >
            <CircularProgress />
          </Grid>) 
          :  ( state.success && <ResultPage results={state.apiResponse.books} /> ) // provide list of results
          }
        </Container>
      </main>

      {/* Footer */}
      <footer className={classes.footer}>
        <Typography variant="h6" align="center" gutterBottom>
          Footer
        </Typography>
        <Typography variant="subtitle1" align="center" color="textSecondary" component="p">
          Something here to give the footer a purpose!
        </Typography>
      </footer>
      {/* End footer */}
    </React.Fragment>
  );
}