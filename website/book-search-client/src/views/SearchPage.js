import React, {useState,useEffect} from 'react';
import AppBar from '@material-ui/core/AppBar';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import BookIcon from '@material-ui/icons/Book';

import CssBaseline from '@material-ui/core/CssBaseline';
import Grid from '@material-ui/core/Grid';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';
import Container from '@material-ui/core/Container';
import CircularProgress from '@material-ui/core/CircularProgress';

import ResultPage from "./ResultPage.js"
import findQuote from "../api/findQuote.js";
import test from "../api/test.js";


const useStyles = makeStyles((theme) => ({
  icon: {
    marginRight: theme.spacing(2),
  },
  heroContent: {
    backgroundColor: theme.palette.background.paper,
    padding: theme.spacing(8, 0, 6),
  },
  heroButtons: {
    marginTop: theme.spacing(4),
  },
  cardGrid: {
    paddingTop: theme.spacing(8),
    paddingBottom: theme.spacing(8),
  },
  card: {
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
  },
  cardMedia: {
    paddingTop: '56.25%', // 16:9
  },
  cardContent: {
    flexGrow: 1,
  },
  footer: {
    backgroundColor: theme.palette.background.paper,
    padding: theme.spacing(6),
  },
  margin: {
    margin: theme.spacing(1),
  },
}));


export default function SearchPage() {
  const classes = useStyles();

  // const [quote, setQuote] = useState('');
  // const [submitted,setSubmit] = useState(false)

  const [state, setState] = useState({
    apiResponse: {
      quote:{},
      bookDetails:{}
    } , 
    quoteId: "",
    isLoading : false,
    requestError:"",
    success: false
  });

  const handleChange = (event) => {
    setState({...state,quoteId: event.target.value})
  };

  const handleSubmit = () =>{
    // Validate input 
    // If input is correct then make the request otherwise change state
    // and display appropriate component
    // findQuoteRequest();
    test()
  }

  const handleClear=(event)=> {
    event.preventDefault();
    setState({...state, quoteId:"",apiResponse:{},success : false})
    // setQuote("");
    // setSubmit(false)
  }


  const findQuoteRequest = async () => {
    setState({ ...state, isLoading: true, requestError: "", apiResponse: "" });
    console.log(state.isLoading)
    const quoteId = state.quoteId;
    await findQuote(quoteId)
        .then(response => {
            console.log("res in setAPIResponse: " + JSON.stringify(response));
            setState({
                ...state,
                isLoading: false,
                apiResponse: {
                  quote: response.quote, // quote object
                  bookDetails : response.book}, // book object
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
      <AppBar position="relative">
        <Toolbar>
          <BookIcon className={classes.icon} />
          <Typography variant="h6" color="inherit" noWrap>
            Book Search Engine
          </Typography>
        </Toolbar>
      </AppBar>
      <main>
        <div className={classes.heroContent}>
          <Container maxWidth="sm">
            <Typography component="h1" variant="h2" align="center" color="textPrimary" gutterBottom>
              Search a book by a quote
            </Typography>
           
           {/* Search Bar */}
            <TextField 
            fullWidth 
            className={classes.margin} 
            label="Type your quote..."
            multiline
            rowsMax={4}
            value={state.quoteId}
            onChange={handleChange}
            ></TextField>

            <Typography variant="h5" align="center" color="textSecondary" paragraph>
              Try to type something short and leading about the book you are looking for
            </Typography>

            {/* Buttons */}
            <div className={classes.heroButtons}>
              <Grid container spacing={2} justify="center">
                <Grid item>
                  <Button variant="contained" color="primary" onClick={handleSubmit}>
                    Submit
                  </Button>
                </Grid>
                <Grid item>
                  <Button variant="outlined" color="primary" onClick={handleClear}>
                    Clear
                  </Button>
                </Grid>
              </Grid>
            </div>
          </Container>
        </div>
        
        <Container className={classes.cardGrid} maxWidth="md">
          {/* Container to hold the results of the search  */}
          {state.isLoading
          ? ( <div >
            <CircularProgress />
          </div>) 
          :  ( state.success && <ResultPage results={[state.apiResponse]} /> ) // provide list of results
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