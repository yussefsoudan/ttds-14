import React, {useState,useEffect} from 'react';
import Grid from '@material-ui/core/Grid';
import BookCard from "../components/BookCard.js"


const bookstest = [1, 2, 3, 4, 5, 6, 7, 8, 9];

//  props will be a list of objects with quote and bookDetails attributes
export default function ResultPage({results}) {
        console.log("Print cards")
        return (
         <Grid container spacing={4}>
            {results.map((resultObj) =>
                 <BookCard  item key={resultObj.bookDetails._id} resultObj={resultObj} />
            )}
          </Grid> 
        )
};


