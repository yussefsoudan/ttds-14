import React, {useState,useEffect} from 'react';
import Grid from '@material-ui/core/Grid';
import BookCard from "../components/BookCard.js"
import Pagination from '@material-ui/lab/Pagination';

//  props will be a list of book objects
export default function ResultPage({results}) {

      const [state, setState] = useState({
          results : [],
          offset : 1,
          perPageResults: 10,
        });


          
        useEffect(() => {
          setState({...state,results:results})
        }, []);

        console.log("Print cards")
        console.log("Number of results",results.length)
        const r = results.length
        const l = state.perPageResult
        console.log(r/l)
        console.log(Number.isNaN(state.results.length) )
        console.log(Number.isNaN( state.perPageResults ))


        const handlePaginationClick = (offset) => {
          setState({...state,offset:offset})
        }
        var count;
        if (state.results.length  % state.perPageResult == 0)
          count = Math.floor(state.results.length/state.perPageResult) 
        else
          count = Math.floor(state.results.length/state.perPageResult) + 1

        console.log("Count of pages",(state.results.length/state.perPageResult) )
        return (
        
        <Grid container 
        className="book-container" 
        spacing={6}
         //  direction="column" 
         justify="center"   
         alignItems="center" 
         >
          <Grid 
            item 
            className="book-card-result"
            xs={8}
          >


         
             {/* {results.length > state.resultLimit &&
              <Pagination 
              count={count} 
              page={state.offset} 
              onChange={(e, offset) => handlePaginationClick(offset)} />
            }

            {state.results.slice(state.offset, state.offset + state.resultLimit).filter((book) => {
                  return book.title != null;
              }).map((book,idx) =>
                  <BookCard  item key={idx} resultObj={book} />
              )}

            {results.length > state.resultLimit &&
             <Pagination 
             count={count} 
             page={state.offset} 
             onChange={(e, offset) => handlePaginationClick(offset)} />
            } */}

            {state.results.filter((book) => {
                  return book.title != null;
              }).map((book,idx) =>
                  <BookCard  item key={idx} resultObj={book} />
              )}


          </Grid>
        </Grid> 
        )
};


