import React ,{useState,useRef} from 'react';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';
import { makeStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Container from '@material-ui/core/Container';
import Button from '@material-ui/core/Button';
import SearchFeatures from "./SearchFeatures.js";
const axios = require('axios');

const useStyles = makeStyles((theme) => ({

      heroContent: {
        backgroundColor: theme.palette.background.paper,
        padding: theme.spacing(8, 0, 6),
      },
      heroButtons: {
        marginTop: theme.spacing(4),
      },
      margin: {
        margin: theme.spacing(1),
      },
  }));
  


export default function SearchBar(props) {
    const classes = useStyles();

    const [state, setState] = useState({
        quote:"",
        bookSearch : false,
        author : "",
        bookTitle: "",
        genre: "",
        yearTo : 2021,
        yearFrom: 1990,
        minRating:1,
        correction: "",
    });


    const ref = useRef(null);


    const handleChange = (event) => {
      setState({...state,quote: event.target.value})
      // Spellcheck
      axios.post('http://188.166.173.191:5000' + '/spellcheck',{
        search_text: event.target.value
      }).then(res => {
      if (res['data']['correction_exists']) {
        setState({...state,correction: res['data']['corrected_text'], quote: event.target.value})
      } else {
        setState({...state,correction: "", quote: event.target.value})
      }
      }).catch(err => {
      console.log("ERROR RETRIEVINGG CORRECTION: " + err)
      });
        
    };
    
    const handleSearchFeaturesChange = (param,value) =>{
        setState({...state, [param]:value});
        console.log("Search features input:",param,value);
    }
    
    const handleClear=(event)=> {
        event.preventDefault();
        setState({...state, quote:"",apiResponse:{},success : false})
        ref.current.handleClear();

    }

    const handleSpellCorrect= () => {
      setState({...state, quote: state.correction, correction: ""})
    }

    
    const handleSubmit = () =>{
        // Potential to validate input here if needed
        props.handleRequest(state)
    }

    
    return(
    <>
        <div className={classes.heroContent}>
          <Container maxWidth="sm">
            <Typography component="h4" variant="h4" align="center" color="textPrimary" gutterBottom>
              Search for a book by its title, by a quote or even by a phrase!
            </Typography>
           
           {/* Search Bar */}
            <TextField 
            fullWidth 
            className={classes.margin} 
            label={state.bookSearch ? "Type your book title terms..." :"Type your quote terms..."}
            multiline
            rowsMax={4}
            value={state.quote}
            onChange={handleChange}
            ></TextField>

            <Typography variant="h7" align="center" color="textSecondary" paragraph style={{"fontStyle" : "italic", "cursor" : "pointer"}} onClick={handleSpellCorrect}>
              {state.correction.length != 0 ? "Did you mean '" + state.correction + "'?": ""}
            </Typography>

            <Typography variant="caption" align="center" color="textSecondary" paragraph value={"hi"} style={{"fontStyle" : "italic"}}>
            Tip: For phrase search, the less common your terms the faster your phrase will be retrieved!

            </Typography>

            {/* Search features component  */}
            <SearchFeatures ref= {ref} handleChange={handleSearchFeaturesChange}  authors={props.authors} book_titles={props.book_titles} />

            {/* Buttons */}
            <div className={classes.heroButtons}>
              <Grid container spacing={2} justify="center">
                <Grid item>
                  <Button variant="contained" color="primary" onClick={handleSubmit}>
                    Search
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
        
    </>
    )

}

