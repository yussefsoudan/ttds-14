import React from 'react';
import { makeStyles, useTheme } from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import Button from '@material-ui/core/Button';
import CardContent from '@material-ui/core/CardContent';
import CardMedia from '@material-ui/core/CardMedia';
import IconButton from '@material-ui/core/IconButton';
import Typography from '@material-ui/core/Typography';
import SkipPreviousIcon from '@material-ui/icons/SkipPrevious';
import PlayArrowIcon from '@material-ui/icons/PlayArrow';
import SkipNextIcon from '@material-ui/icons/SkipNext';

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
    marginTop: '5%',
    marginBottom: '5%',
  },
  cover: {
    maxWidth: '100%',
    padding: '0.7em'
  },
  details: {
    display: 'flex',
    flexDirection: 'column',
  },
  content: {
  },
}));

export default function BookCard({resultObj}) {
    const classes = useStyles();
    let book  = resultObj;
    let quote = resultObj.quote ?  resultObj.quote : "";
    let authors = ""
    for (let i = 0; i < book.authors.length; i++) {
      if (i == book.authors.length - 1) {
        authors += book.authors[i]
      } else {
        authors += book.authors[i] + ", "
      }
    }

    return (

      <Card className={classes.root} >
        <CardMedia
          className={classes.cover}
        >
          <img src={book.thumbnail} style={{"max-height" : "100%", "max-width" : "100%", 
          "border" : "0.2em solid black", "border-radius" : "0.1em"}}/>
        </CardMedia>
        <div className={classes.details}>
          <CardContent className={classes.content}>
            <Typography variant="h5" component="h2">
              {book.title}
              </Typography>
              <Typography gutterBottom component="h3"   >
              {authors}
              </Typography>
              
              <Typography gutterBottom component="h4" variant="h6" style={{"color" : "darkblue", "font-style": "italic"}} >
              <q cite="https://www.mozilla.org/en-US/about/history/details/">{quote}</q>
              </Typography>
                <Typography size="small" color="primary" href={book.previewLink}  target="_blank" style={{'textTransform': 'none'}}>
                View on Google Books
                </Typography>
          </CardContent>
        </div>
      </Card>
    )              
}

