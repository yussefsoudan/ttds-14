import React, {useState,useEffect} from 'react';
import Grid from '@material-ui/core/Grid';
import BookCard from "../components/BookCard.js"
import Pagination from '@material-ui/lab/Pagination';

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
          let order = key.split("-")[1]
          let actualKey = key.split("-")[0]
          var arr = state.data
          if (order == "ASC") {
            arr = sortByKeyASC(arr,actualKey)
          } else {
            arr = sortByKeyDSC(arr,actualKey)
          }

          // arr = sortByKey(arr,"averageRating")
          setState({...state,sort:value,data:arr,sorting:false})
          console.log("Sorted results",state.data)
        }

        const sortByKeyASC = (array, key) => {
          return array.sort(function(a, b) {
              var x = a[key]; 
              var y = b[key];
              return ((x < y) ? -1 : ((x > y) ? 1 : 0));
          });
        }

        const sortByKeyDSC = (array, key) => {
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

                <Grid item xs={2} >
                  <FormControl className={classes.formControl} >
                      <InputLabel id="genre">Sort by</InputLabel>
                      <Select
                        labelId="sort-selcet"
                        id="sort-select"
                        onChange={e => handleSort(e.target.value,true)}
                      >
                        <MenuItem value={"title-ASC"}>Book title: A-Z</MenuItem>
                        <MenuItem value={"title-DSC"}>Book title: Z-A</MenuItem>
                        <MenuItem value={"averageRating-DSC"}>Average rating: High-to-Low</MenuItem>
                        <MenuItem value={"averageRating-ASC"}>Average rating: Low-to-High</MenuItem>
                        <MenuItem value={"pageCount-DSC"}>Page count: High-to-Low</MenuItem>
                        <MenuItem value={"pageCount-ASC"}>Page count: Low-to-High</MenuItem>
                        <MenuItem value={"ratingsCount-DSC"}>Number of ratings: High-to-Low</MenuItem>
                        <MenuItem value={"ratingsCount-ASC"}>Number of ratings: Low-to-High</MenuItem>
                      </Select>
                  </FormControl>
                </Grid>
              </Grid>
              )}      

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


