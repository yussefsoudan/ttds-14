import React ,{useState,useEffect} from 'react';
import Switch from '@material-ui/core/Switch';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import MenuItem from '@material-ui/core/MenuItem';
import Select from '@material-ui/core/Select';
import InputLabel from '@material-ui/core/InputLabel';
import FormControl from '@material-ui/core/FormControl';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';
import { makeStyles } from '@material-ui/core/styles';



const useStyles = makeStyles((theme) => ({
    formControl: {
        margin: theme.spacing(1),
        minWidth: 120,
      },
  }));
  
  
let years = []
for(var i = 1990; i< 2022; i++){
  years.push(i)
}

export default function SearchFeatures(props) {
    const classes = useStyles();

    const [state, setState] = useState({
          bookSearch : false,
          author : "",
          bookTitle: "",
          genre: "",
          yearFrom:1990,
          yearTo : 2021
      });
    

    
    const handleChange = (field,value) => {
        console.log("Field",field)
        console.log("Value",value)

        // TODO 
        // Year has to be checked and error message displayed
        setState({...state,[field]:value})
        
        /* Pass state to parent component  */
        props.handleChange({[field]:value})
    };


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
             <TextField 
             id="standard-basic" label="Book Title" 
             value={state.bookTitle}
             onChange={e => handleChange('bookTitle', e.target.value)} /> 
            </Grid>
           <Grid container item xs={4} >
             <TextField 
             id="standard-basic" label="Author" 
             value={state.author}
             onChange={e => handleChange('author', e.target.value)} />  
            </Grid>
           <Grid container item xs={4} >
             <TextField 
             id="standard-basic" label="Genre" 
             value={state.genre}
             onChange={e => handleChange('genre', e.target.value)} />  
            </Grid>            
         </Grid>
         
         {/* Second row of advance Search */}
         <Grid container item xs={12} spacing={3}>

         
           <Grid container item xs={4}>
             <FormControl className={classes.formControl}>
                 <InputLabel id="year-from">Year From</InputLabel>
                 <Select
                   labelId="year-from-select"
                   id="year-from-select"
                   // open={open}
                   // onClose={handleClose}
                   // onOpen={handleOpen}
                   value={state.yearFrom}
                   onChange={e => handleChange('yearFrom', e.target.value)}
                 >
                   {years.map((name) => (
                               <MenuItem key={name} value={name} >
                                 {name}
                               </MenuItem>
                             ))}
                 </Select>
             </FormControl>
           </Grid>

           <Grid container item xs={4}>
             <FormControl className={classes.formControl}>
                 <InputLabel id="year-to">Year To</InputLabel>
                 <Select
                   labelId="year-to-select"
                   id="year-to-select"
                   // open={open}
                   // onClose={handleClose}
                   // onOpen={handleOpen}
                   value={state.yearTo}
                   onChange={e => handleChange('yearTo', e.target.value)}
                 >
                   {years.map((name) => (
                               <MenuItem key={name} value={name} >
                                 {name}
                               </MenuItem>
                             ))}
                 </Select>
             </FormControl>
           </Grid>
         </Grid>
       </Grid>
    </>
    )

}
