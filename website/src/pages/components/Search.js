import React from 'react';
import {useState, useEffect} from 'react';
import {ReactComponent as SearchIcon} from '../../static/icons/search.svg'
import {Link} from 'react-router-dom';
import {ReactComponent as Scissor} from '../../static/icons/scissor.svg'
import {getIcon} from './Rating';

function Search({placeholder}){
  const [movies, setMovies] = useState(null);
  const [active, setActive] = useState(false);
  const [query, setQuery] = useState("");
  const [resultsActive, setResultsActive] = useState(false);

  function onFocus(){
    setActive(true);
  }

  function onFocusOut(){
    if (!resultsActive){
      setActive(false);
    }
  }

  // Data Fetching Called once at mount/dismount
  useEffect(() => {
    fetch('/api/movies', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'cache-control': 'no-store',
      },
      body: JSON.stringify({
        "properties": ["ID", "TITLE", "YEAR", "AVG_RATING", "TYPES"]
      })//this.state.filterCriteria
    }).then(res => res.json()).then(data => {
      setMovies(data["data"]);
    })
  }, [])


  return (
    <div className="searchbar" >
        <SearchIcon />
        {!query && <span>{placeholder}</span>}

        <input onFocus={onFocus}  onChange={event => setQuery(event.target.value)} onBlur={onFocusOut}>
          
        </input>
        <span className='bg'></span>
        <Link to={"/browse"}><span>Advanced Search</span></Link>
        
        <div className="searchresults" style={{display: active ? 'block': 'none'}} 
        onMouseEnter={()=>{setResultsActive(true)}}
        onMouseLeave={()=>{setResultsActive(false)}}
        >
          { movies &&
            movies.filter(movie => {
              if(query === ""){
                return false;
              }
              if (movie.TITLE.toLowerCase().startsWith(query.toLowerCase())) {
                return true;
              }
              return false;
            }).map((movie) => {
              let Icon = getIcon(movie.TYPES);
              let rating = movie.AVG_RATING > 0? movie.AVG_RATING : "-";
              return <Link to={"/movies/" + movie.ID} key={movie.ID}>
                <div className="searchresult">
                  <span>{movie.TITLE}</span>
                  <div>{movie.YEAR} 
                  &nbsp;&#9679;&nbsp; {rating}&nbsp;<Icon /></div>
                </div>
              </Link>
            })
          }
        </div>
      </div>
  )


}

// class Search extends Component {
//   constructor(props){
//     super(props)
//     this.state = {
//       query: "",
//       movies: [],
//       active: false,
//       resultsactive: false,
//     }
//   }
//   componentDidMount() {
//     this.getMovies();

//   }


//   getMovies = () => {
//     this.setState({
//       movies: movies
//     })
//   }

//   onFocus = () =>{
//     this.setState({active: true})
//     //this.refs.nameInput.getInputDOMNode().focus();
//   }

//   onFocusOut = () =>{
//     if (!this.state.resultsactive){
//       this.setState({active: false})
//     }
//   }

//   render(){
//     return (
//       <div className="searchbar" >
//         <SearchIcon />
//         <input onFocus={this.onFocus} placeholder={this.props.placeholder} onChange={event => this.setState({query: event.target.value})} onBlur={this.onFocusOut} />
//         <Link to={"/browse"}><span>Advanced Search</span></Link>
        
//         <div className="searchresults" style={{display: this.state.active ? 'block': 'none'}} 
//         onMouseEnter={()=>{this.setState({resultsactive:true})}}
//         onMouseLeave={()=>{this.setState({resultsactive:false})}}
//         >
//           {
//             this.state.movies.filter(movie => {
//               if(this.state.query === ""){
//                 return false;
//               }
//               if (movie.title.toLowerCase().includes(this.state.query.toLowerCase())) {
//                 return true;
//               }
//               return false;
//             }).map((movie) => (
//               <Link to={"/movies/" + movie.id} key={movie.id}>
//                 <div className="searchresult">
//                   <span>{movie.title}</span>
//                   <div>{movie.year} &nbsp;&#9679;&nbsp; {movie.rating}&nbsp;<Scissor /></div>
//                 </div>
//               </Link>
//             ))
//           }
//         </div>
//       </div>
//     )
//   }
// }

export default Search