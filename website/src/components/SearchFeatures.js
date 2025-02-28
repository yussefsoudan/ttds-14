import React, { useState, forwardRef, useImperativeHandle } from "react";

import Switch from '@material-ui/core/Switch';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import MenuItem from '@material-ui/core/MenuItem';
import Select from '@material-ui/core/Select';
import InputLabel from '@material-ui/core/InputLabel';
import FormControl from '@material-ui/core/FormControl';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';
import { makeStyles } from '@material-ui/core/styles';
import Autocomplete from '@material-ui/lab/Autocomplete';


const useStyles = makeStyles((theme) => ({
    formControl: {
        // margin: theme.spacing(1),
        minWidth: 120,
      },
  }));
  
  
let years = []
for(var i = 1990; i< 2022; i++){
  years.push(i)
}


let genres = ['All','Fiction','Biography & Autobiography','Juvenile Fiction','Poetry','Young Adult Fiction',
'Philosophy','Young Adult Nonfiction','True Crime','Indic fiction (English)']

const SearchFeatures = forwardRef((props,ref) => {
    const classes = useStyles();

    const authors = props.authors;
    const book_titles = props.book_titles;

    const [state, setState] = useState({
          bookSearch : false,
          author : "",
          bookTitle: "",
          genre: "",
          yearFrom:1990,
          yearTo : 2021,
          minRating: 1
      });
    

    
    const handleChange = (field,value) => {
        console.log("Field",field)
        console.log("Value",value)

        // TODO 
        // Year has to be checked and error message displayed
        setState({...state,[field]:value})
        
        /* Pass state to parent component  */
        props.handleChange(field,value)
    };

    
    const handleClear=()=> {
      setState({...state, author:"",bookTitle:"",genre:"",yearFrom:1990,yearTo : 2021})
    }


    useImperativeHandle(ref, () => {
      return {
        handleClear: handleClear
      };
    });


    return(
    <>
      {/* Extra search features */}
      <Grid container>  
         <FormControlLabel
           control={<Switch checked={state.bookSearch} onChange={e => handleChange('bookSearch', e.target.checked)} name="bookSearch" color="primary"/>}
           label="Book Search"
         />
      </Grid>

      <Grid container spacing={1}>

         {/* First row of advance Search */}
         <Grid container item xs={12} spacing={3}>
            <Grid container item xs={4} >
              <Autocomplete
                id="book-title-select"
                options={book_titles}
                getOptionLabel={(book_title) => book_title.book_title}
                style={{ width: 300 }}
                renderInput={(params) => <TextField {...params} label="Book Title" />}
                onChange={(event, newValue) => handleChange('bookTitle', newValue ? newValue.book_title : newValue )}
              />
            </Grid>
            <Grid container item xs={4} >
              <Autocomplete
                id="author-select"
                options={authors}
                getOptionLabel={(author) => author.name}
                style={{ width: 300 }}
                renderInput={(params) => <TextField {...params} label="Author" />}
                onChange={(event, newValue) => handleChange('author', newValue ? newValue.name : newValue)}  

              />
            </Grid>

           <Grid container item xs={4}>
             <FormControl className={classes.formControl}>
                 <InputLabel id="genre">Genre</InputLabel>
                 <Select
                   labelId="genre-selcet"
                   id="genre-select"

                   value={state.genre}
                   onChange={e =>handleChange('genre', e.target.value)}
                 >
                   {genres.map((genre) => (
                               <MenuItem key={genre} value={genre} >
                                 {genre}
                               </MenuItem>
                             ))}
                 </Select>
             </FormControl>
           </Grid>        
         </Grid>
         
         {/* Second row of advance Search */}
        <Grid container item xs={12} spacing={3}>

           <Grid container item xs={4} >
              <TextField 
                className={classes.formControl} 
                label="Year From"
                labelId="year-from-select"
                id="year-from-select"
                rowsMax={1}
                value={state.yearFrom}
                onChange={e => handleChange('yearFrom', e.target.value != '' ? parseInt(e.target.value) : '')}
              ></TextField>
            </Grid>

           <Grid container item xs={4} >
              <TextField 
                className={classes.formControl} 
                label="Year To"
                labelId="year-to-select"
                id="year-to-select"
                rowsMax={1}
                value={state.yearTo}
                onChange={e => handleChange('yearTo', e.target.value != '' ? parseInt(e.target.value) : '')}
              ></TextField>
            </Grid>

           <Grid container item xs={4}>
             <FormControl className={classes.formControl}>
                 <InputLabel id="rating">Min. Rating</InputLabel>
                 <Select
                   labelId="rating-selcet"
                   id="rating-select"

                   value={state.minRating}
                   onChange={e =>handleChange('minRating', e.target.value)}
                 >
                   {[1,2,3,4,5].map((rating) => (
                               <MenuItem key={rating} value={rating} >
                                 {rating}
                               </MenuItem>
                             ))}
                 </Select>
             </FormControl>
           </Grid>    

        </Grid>
      </Grid>
    </>
    )

});
export default SearchFeatures;
