import React, {useState,useEffect} from 'react';
import Grid from '@material-ui/core/Grid';

import BookCard from "../components/BookCard.js"


const bookstest = [1, 2, 3, 4, 5, 6, 7, 8, 9];


export default function ResultPage([{quote,bookDetails}]) {
    const [status, setStatus] = useState('idle')
    const [error, setError] = useState(null)
    const [books,setBooks] = useState([])


    useEffect(() => {
        if (!quote) {
          return
        }
        setStatus('resolved')
        // fetchBooks(quote).then(
        //   booksData => {
        //     setStatus('resolved')
        //     setBooks(booksData)
        //   },
        //   errorData => {
        //     setStatus('rejected')
        //     setError(errorData)
        //   },
        // )
      }, [quote])
  
      if (status === 'idle') {
        return 'Submit a quote'
      }
  
      if (status === 'rejected') {
        return 'Oh no...'
      }
  
      if (status === 'pending') {
        return '...'
      }
  
      if (status === 'resolved') {
        console.log("Print cards")
        // return (<pre>{JSON.stringify(books, null, 2)}</pre>)
        return (
         <Grid container spacing={4}>
            {bookstest.map((book) => 
                <BookCard  item key={book} book={book} />
            )}
          </Grid> 
        )
      }
};


