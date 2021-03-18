import React, {useState,useEffect} from 'react';
import Grid from '@material-ui/core/Grid';
import BookCard from "../components/BookCard.js"



//  props will be a list of book objects
export default function ResultPage({results}) {
        console.log("Print cards")

        return (
         <Grid 
         container 
        //  direction="column" 
         justify="center"   
         alignItems="center" 
         spacing={4} 
         xs={12}
         >
        {results.filter((book) => {
            return book.title != null;
        }).map((book,idx) =>
             <BookCard  item key={idx} resultObj={book} />
        )}
           
          </Grid> 
        )
};


