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
import clsx from 'clsx';
import Collapse from '@material-ui/core/Collapse';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import Highlighter from "react-highlight-words";
import ShowMoreText from 'react-show-more-text';
import Stars from 'react-stars-display';

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
    marginTop: '5%',
    marginBottom: '5%',
    border: '0.2em solid lightgrey'
  },
  cover: {
    maxWidth: 120,
    minWidth: 120,
    padding: 7,
    objectFit: 'cover',
  },
  details: {
    display: 'flex',
    flexDirection: 'column',
    minWidth: '75%'
  },
  content: {
  },
  expand: {
    transform: 'rotate(0deg)',
    marginLeft: 'auto',
    transition: theme.transitions.create('transform', {
      duration: theme.transitions.duration.shortest,
    }),
  },
  expandOpen: {
    transform: 'rotate(180deg)',
  }
}));

export default function BookCard({resultObj, searchTerms, searchQuote}) {
    const classes = useStyles();
    const [expanded, setExpanded] = React.useState(false);

    let book  = resultObj;
    let quote = resultObj.quote ?  resultObj.quote : "";
    let quoteArr = quote.split(" ");
    let authors = ""
    for (let i = 0; i < book.authors.length; i++) {
      if (i == book.authors.length - 1) {
        authors += book.authors[i]
      } else {
        authors += book.authors[i] + ", "
      }
    }
    let bookDetails = <div style={{"fontStyle" : "italic"}}>
                        <Typography gutterBottom variant="h6" component="h2"  >
                        Book description
                        </Typography>
                        <Typography gutterBottom variant="h7" component="h5"  >
                        {(book.description == undefined ||  book.description == null || book.description == '') ? 
                        'No book description available.' : <ShowMoreText
                        /* Default options */
                        lines={1}
                        more='Show more'
                        less='Show less'
                        className='content-css'
                        anchorClass='my-anchor-css-class'
                        expanded={false}
                        width={0}
                        > {book.description}</ShowMoreText>}
                        </Typography>
                        <Typography gutterBottom variant="h6" component="h2"   >
                        Average rating
                        </Typography>
                        <Typography gutterBottom variant="h7" component="h5"   >
                          {book.averageRating != "" ?
                        <Stars
                        stars={book.averageRating}
                        size={20} //optional
                        spacing={2} //optional
                        fill='#ea9c46' //optional
                        /> : "No ratings were given to this book."}
                        </Typography>
                        <Typography gutterBottom variant="h6" component="h2"   >
                        Number of ratings
                        </Typography>
                        <Typography gutterBottom variant="h7" component="h5"    >
                        {book.ratingsCount != "" ? book.ratingsCount : "No ratings were given to this book."}
                        </Typography>
                        <Typography gutterBottom variant="h6" component="h2"  >
                        Book categories
                        </Typography>
                        <Typography gutterBottom variant="h7" component="h5"  >
                         {book.categories}
                        </Typography>
                        <Typography gutterBottom variant="h6" component="h2"  >
                        Number of pages 
                        </Typography>
                        <Typography gutterBottom variant="h7" component="h5" >
                        {book.pageCount != "" ? book.pageCount : "No page count is available."}
                        </Typography>
                        <Typography gutterBottom variant="h6" component="h2"   >
                        Published date
                        </Typography>
                        <Typography gutterBottom variant="h7" component="h5"    >
                        {book.publishedDate != "" ? book.publishedDate : "No publication date is available."}
                        </Typography>
                        <Typography gutterBottom variant="h6" component="h2"   >
                        ISBN
                        </Typography>
                        <Typography gutterBottom variant="h7" component="h5"   >
                        {book['isbn-13']}
                        </Typography>
                        
                      </div>
      let displayedQuote = bookDetails 
      if (quote.length > 300) {
        displayedQuote = <ShowMoreText
                          /* Default options */
                          lines={3}
                          more='Show more'
                          less='Show less'
                          className='content-css'
                          anchorClass='my-anchor-css-class'
                          expanded={false}
                          width={0}
                          >
                            <q cite="https://www.mozilla.org/en-US/about/history/details/">{
                          <Highlighter
                          highlightClassName="YourHighlightClass"
                          searchWords={searchQuote.includes("\"") ? [searchQuote.replaceAll("\"", "").replaceAll(",", "").replaceAll(";", "")] : searchTerms}
                          autoEscape={true}
                          textToHighlight={quote}
                        >
                          
                          </Highlighter>}</q>
                          </ShowMoreText>
      } else if (quote.length <= 300 && quote.length > 0) {
        displayedQuote = <q cite="https://www.mozilla.org/en-US/about/history/details/">{
                          <Highlighter
                          highlightClassName="YourHighlightClass"
                          searchWords={searchQuote.includes("\"") ? [searchQuote.replaceAll("\"", "").replaceAll(",", "").replaceAll(";", "")] : searchTerms}
                          autoEscape={true}
                          textToHighlight={quote}
                        >
                          
                          </Highlighter>}</q>
      }

    const handleExpandClick = () => {
      setExpanded(!expanded);
    };

  


    return (

      <Card className={classes.root} >
        <CardMedia
          className={classes.cover}
        >
          <img src={book.thumbnail} style={{"max-height" : "100%", "max-width" : "100%", 
          "border" : "0.2em solid black", "border-radius" : "0.1em"}}/>
        </CardMedia>
        <div className={classes.details}>
        
          <CardContent className={classes.content} >
            <Typography variant="h5" component="h2">
              {book.title}
            </Typography>
            <Typography gutterBottom component="h3" >
              {authors}
            </Typography>
            <Typography gutterBottom component="h3" >
              {displayedQuote == bookDetails ? displayedQuote : ""}
            </Typography>
              
            <Typography gutterBottom component="h4" variant="h6" style={{"color" : "darkblue", "font-style": "italic"}} >
              
            {displayedQuote == bookDetails ? "" : displayedQuote}
              
            </Typography>
            <Button disableRipple size="small" color="primary" href={book.previewLink}  target="_blank" style={{'cursor' : 'pointer',  
              'textTransform': "none", 'backgroundColor': 'transparent'  }}>
              View on Google Books
            </Button>
            <hr  style={{
              color: 'lightblue',
              align: 'left',
              width: '100%'
            }}/>
          </CardContent>
          {(quote.length > 0) ? <IconButton
              className={clsx(classes.expand, {
                [classes.expandOpen]: expanded,
              })}
              onClick={handleExpandClick}
              aria-expanded={expanded}
              aria-label="show more"
            >
              <ExpandMoreIcon />
          </IconButton> : ""}
          
          {(quote.length > 0) ? 
            
            
            <Collapse in={expanded} timeout="auto" unmountOnExit>
              {(quote.length > 0) ? <CardContent>{bookDetails}</CardContent> : ""}
            </Collapse>
             :
            ""
          }
          
        </div>
      </Card>

    )              
}

