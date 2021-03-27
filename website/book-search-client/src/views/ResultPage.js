import React, {useState,useEffect} from 'react';
import Grid from '@material-ui/core/Grid';
import BookCard from "../components/BookCard.js"
import Pagination from '@material-ui/lab/Pagination';

import Switch from '@material-ui/core/Switch';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';
import MenuItem from '@material-ui/core/MenuItem';
import Select from '@material-ui/core/Select';
import InputLabel from '@material-ui/core/InputLabel';
import FormControl from '@material-ui/core/FormControl';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
  formControl: {
      // margin: theme.spacing(1),
      minWidth: 120,
    },
}));


//  props will be a list of book objects
export default function ResultPage({results, searchTerms, searchQuote}) {
      const classes = useStyles();

      const [state, setState] = useState({
          data : [],
          searchTerms : [],
          offset : 1,
          perPageResults: 10,
          sort: false,
          searchQuote : ""

        });

        console.log("Result page rendered")

        
        useEffect(() => {
          const onRender = async () => {
            console.log("Use effect hook")
            setState({...state, data:results, searchTerms : searchTerms, searchQuote : searchQuote}) 
            }
          onRender()
        },[]);


        const handlePaginationClick = (offset) => {
          setState({...state,offset:offset})
        }

        const handleSort = (key,value) => {
          console.log("Sort")
          var arr = state.data
          arr = sortByKey(arr,key)

          // arr = sortByKey(arr,"averageRating")
          setState({...state,sort:value,data:arr,sorting:false})
          console.log("Sorted results",state.data)
        }

        const sortByKey = (array, key) => {
          return array.sort(function(a, b) {
              var x = a[key]; 
              var y = b[key];
              return ((x < y) ? 1 : ((x > y) ? -1 : 0));
          });
      }

        // Calculate how many pagination page we will have 
        var length = Object.keys(state.data).length;
        var count;
        if (length % Number(state.perPageResults) == 0)
          count = Math.floor(length/Number(state.perPageResults)) 
        else
          count = Math.floor(length/Number(state.perPageResults)) + 1
        console.log("Page count",count)


        return (
        <Grid container 
        className="book-container" 
        spacing={6}
         justify="center"   
         alignItems="center" 
         >
           
          <Grid 
            item 
            className="book-card-result"
            xs={8}
          >

            {length> 0 && ( 
            <Grid container spacing={3}>  
            {length> state.perPageResults &&
              <Grid item xs={8} >
                  <Pagination 
                  count={count} 
                  page={state.offset} 
                  onChange={(e, offset) => handlePaginationClick(offset)} />
              </Grid>
              }

              {/* <Grid item xs={2} >
                <FormControlLabel
                control={<Switch checked={state.sort} onChange={e => handleSort("averageRating",e.target.checked)} name="sort" color="primary"/>}
                label="Average Rating"
                labelPlacement="End"
                />
              </Grid>
            </Grid>          */}

            <Grid item xs={2} >
            <FormControl className={classes.formControl} >
                <InputLabel id="genre">Sort by</InputLabel>
                <Select
                  labelId="sort-selcet"
                  id="sort-select"

                  value={state.genre}
                  onChange={e => handleSort(e.target.value,true)}
                >
                  <MenuItem value={"title"}>Book title</MenuItem>
                  <MenuItem value={"averageRating"}>Average Rating</MenuItem>
                  <MenuItem value={"pageCount"}>Page count</MenuItem>

                  {/* <MenuItem value={30}>Thirty</MenuItem> */}
                </Select>
            </FormControl>
            </Grid>
            </Grid>
            )        
            
            
            
            }



            { state.data.slice(
             (state.offset -1 )*state.perPageResults, 
              (state.offset-1)*state.perPageResults + Number(state.perPageResults)).filter((book) => {
                  return book.title != null;
              }).map((book,idx) =>
                  <BookCard  item key={idx} resultObj={book} searchTerms={state.searchTerms} searchQuote={state.searchQuote}/>
              )
            }

            {length> state.perPageResults &&
             <Pagination 
             count={count} 
             page={state.offset} 
             onChange={(e, offset) => handlePaginationClick(offset)} />
            }

          </Grid>
        </Grid> 
        
        )
};


