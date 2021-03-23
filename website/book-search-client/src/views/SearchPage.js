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
import getAllAuthors from "../api/getAllAuthors.js"
import getAllBookTitles from "../api/getAllBookTitles";

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

let dummy_authors = [{name:"Janish"}
,{name:"Harry poppins"},
{name:"Anna michin"},
{name:"Mike"},
{name:"Joah noah"},
{name:"Michelin"}]

export default function SearchPage() {
  const classes = useStyles();

  const [state, setState] = useState({
    apiResponse: {
      books:[]
    } , 
    searchTerms : [],
    isLoading : false,
    errorOccur:false,
    errorMsg:"",
    success: false,
    authors : [],
    book_titles : []
  });

  console.log("Search page render")


  // Use effect hook that will be triggered once, on render, to fetch the Author names
  useEffect(() => {
    console.log("Hook to get author names")
      const getAuthorsandBookNames = async () => {
        let authors = []
        let book_titles = []
        await getAllAuthors()
          .then(response => {
            // console.log("repsonse within author hook",response);
            authors = response.authors
          })
          .catch(errorResponse => {
            console.log("Error response",errorResponse)
          });

          await getAllBookTitles()
          .then(response => {
            // console.log("repsonse within book hook",response);
            book_titles = response.book_titles
          })
          .catch(errorResponse => {
            console.log("Error response",errorResponse)
          });

          setState({
              ...state,
              book_titles: book_titles,
              authors:authors
          })
      };

    

      getAuthorsandBookNames();

    }, []); // empty list of dependencies ensures the hooks is only called upon rendering of the component


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
    
    
    await getSearchResults(
      bookSearch ? "/books_search" : "/quotes_search",

      {quote, author ,bookTitle, genre, yearFrom, yearTo}
      )
        .then(response => {
            // console.log("res in setAPIResponse: " + JSON.stringify(response));
            setState({
                ...state,
                isLoading: false,
                apiResponse: {
                  books : response.books}, // book object, might contain quote as well 
                requestError: "",
                success:true,
                searchTerms:response.searchTerms
            });
        })
        .catch(errorResponse => {
            setState({
                ...state,
                isLoading: false,
                success : false,
                errorOccur: true,
                errorMsg: errorResponse,
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
        <SearchBar handleRequest={handleRequest}  authors={state.authors} book_titles={state.book_titles} />

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
          :  ( state.success && <ResultPage results={state.apiResponse.books} searchTerms={state.searchTerms} /> ) // provide list of results
          }
          {state.errorOccur && <Typography variant="h6" align='center' color='error' className="error-message">{`Your request has timed out. The error message is: ${state.errorMsg}`}</Typography> }
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