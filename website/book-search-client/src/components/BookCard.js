import React from 'react';


import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import CardMedia from '@material-ui/core/CardMedia';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';


const useStyles = makeStyles((theme) => ({
    cardGrid: {
      paddingTop: theme.spacing(2),
      paddingBottom: theme.spacing(2),
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

  }));
  

export default function BookCard({resultObj}) {
    // console.log("Book card",resultObj)
    const classes = useStyles();
    let book  = resultObj;
    let quote = resultObj.quote ?  resultObj.quote : "" //resultObj.quote.quoteStr;
    // console.log(book)
    // console.log(quote)

    return (
    <Grid 
    item key={book._id}  
    xs={12} 
    sm={6} 
    className={classes.cardGrid}
    
    // md={4}
    >
        <Card raised className={classes.card}>
        <CardMedia
            className={classes.cardMedia}
            // image="https://source.unsplash.com/random"
            image = {book.thumbnail}
            title={book.title}
        />
        <CardContent className={classes.cardContent}>
            <Typography gutterBottom variant="h5" component="h2">
            {book.title}
            </Typography>
            {book.authors.map((author)=>
            <Typography component="h3">
             {author}
            </Typography>)}
            
            <Typography component="h4">
            {quote}
            </Typography>
        </CardContent>
        <CardActions>
            <Button size="small" color="primary" href={book.previewLink}>
            View
            </Button>
            <Button size="small" color="primary">
            Edit
            </Button>
        </CardActions>
        </Card>
      </Grid>
    )              
  }