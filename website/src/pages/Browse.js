import React, { Component, useState, useEffect} from 'react';
import Footer from './components/Footer';

import Filters from './components/Filters';
import Labels from './components/Labels';
import MovieList from './components/MovieList';
import Options from './components/Options';
import Indexer from './components/Indexer';

import {ReactComponent as Filter} from '../static/icons/filter.svg'

const SORT = {
  "Most Popular": ["NUM_RATING", -1],
  "Least Popular": ["NUM_RATING", 1],
  "Highest Rating": ["AVG_RATING", -1],
  "Lowest Rating": ["AVG_RATING", 1],
  "Most Recent Release": ["YEAR", -1],
  "Least Recent Release": ["YEAR", 1],
}

function Browse(){

  const [filterActive, setFilterActive] = useState(false);
  const [movies, setMovies] = useState(null);
  const [sort, setSort] = useState(SORT['Most Recent Release']);
  const [index, setIndex] = useState(1);
  const [criteria, setCriteria] = useState({});
  const [nIndexes, setNIndexes] = useState(null);
  const [nMatches, setNMatches] = useState(null);
  const [labelsLoaded, setLabelsLoaded] = useState(false);


  function get_movies(){
    if(criteria !== null){
      fetch('/api/movies', {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'cache-control': 'no-store',
        },
        body: JSON.stringify({
          "criteria": criteria,
          "sort": sort,
          "index": index
        })//this.state.filterCriteria
      }).then(res => res.json()).then(data => {
        setMovies(data["data"]);
        setNIndexes(data["n_indexes"]);
        setNMatches(data["n_matches"]);
      })
    }
  }

  useEffect(() => {
    console.log('Setting sort', sort)
    if(movies != null){
      setMovies(null);
      if(index != 1){
        setIndex(1);
      }else{
        get_movies();
      }
    }
  }, [sort])

  useEffect(() => {
    console.log('Setting criteria', criteria)
    setMovies(null);
    setNIndexes(null);
    setNMatches(null);
    if(index != 1){
      setIndex(1);
    }else{
      get_movies();
    }
  }, [criteria])

  // Data Fetching Called at criteria updates
  useEffect(() => {
    console.log('Setting index ', index)
    if(movies != null){
      setMovies(null);
      // Loading is true while movies are null
      get_movies();
    }
  }, [index]);



  function updateCriteria(update){

    let newCriteria = criteria === null? {...update} : {...criteria, ...update}

    // Cancelled criteria are removed
    for(let key in newCriteria){
      if(newCriteria[key] === null){
        delete newCriteria[key];
      }
    }
    setCriteria(
      newCriteria
    )
  }

  return (
    <div id="Browse" className="page">
      {filterActive && <div className="cover" onClick={()=>{setFilterActive(false)}} />}

      <Filters active={filterActive} nMatches={nMatches} updateFilters={updateCriteria} filters={criteria} />

      <div id="ControlPanel">
        <Options name='Sort' updateOption={setSort} option={sort} options={SORT} />
        <Labels labelType="GENRES" updateLabel={updateCriteria} setLoaded={setLabelsLoaded}/>
        
        <div id="FiltersToggle" onClick={()=>{setFilterActive(!filterActive)}} className={filterActive? 'active': ''} ><Filter/>Filters</div>
      </div>
      <div id="MovieList">
        <MovieList movies={movies} />
        <Indexer nIndexes={nIndexes} updateIndex={setIndex} index={index} />
      </div>
      <Footer />
    </div>
  )
}
export default Browse

//<!--<div className="spacer"/>-->
{/* <div id="BrowseResults">
<Loader isLoading={movies.length > 0} />
{movies.filter(movie=>(
    !genre || movie['GENRES'].map(g=> g.ID).indexOf(genre) != -1
  )).length===0 && <div id="alert">
    We are sorry we could find no titles matching your search criteria.
    To learn more about the state of lesbian cinema, click here.
    Otherwise, similar searches with results are:  
  </div>
}

{
  sortMovies(movies, sort).filter(movie=>(
    !genre || movie.GENRES.map(g => g.ID).indexOf(genre) != -1
  )).map(movie => (
    <MovieTile movie={movie} />
  ))
}
</div> */}


// class Browse extends Component {
//   constructor(props){
//     super(props)
//     this.state = {
//       genre: null,
//       // categories: ["All", "Romance", "Drama", "Comedy", "Sci-Fi", "Period-Piece", "Horror", "Cult Classic"],
//       genres: [],
//       filterMenuActive: false,
//       movies: [],
//       sort: Object.keys(SORT)[0],
//       filterCriteria: {}
//     }
//     this.all_movies = [];
//     //this.genres = [];
//   }

// function sortMovies(movies, sort){
//   /* Sort Movies by properties.*/
//   let prop = SORT[sort][0]
//   let order = SORT[sort][1]
  
//   return movies.sort((m1, m2) => (m1[prop] > m2[prop] ? order: -1 * order))
// }

//   getMovies(){
//     fetch('/api/movies', {
//       method: 'POST',
//       headers: {
//         'Accept': 'application/json, text/plain, */*',
//         'Content-Type': 'application/json'
//       },
//       body: JSON.stringify({})//this.state.filterCriteria
//     }).then(res => res.json()).then(data => { //
//       console.log(data)
//       this.all_movies = data.data;
//       this.setState({movies: data.data});
//     })
//   }
//   getGenres(){
//     fetch('/api/movie/labels').then(res => res.json()).then(data => {
//       this.setState({genres: data["GENRES"]});
//     });
//   }

//   componentDidMount(){
//     this.getGenres();
//     this.getMovies();
//   }

//   sortMovies(movies){
//     /* Sort Movies by properties.*/
//     let prop = SORT[this.state.sort][0]
//     let order = SORT[this.state.sort][1]
    
//     return movies.sort((m1, m2) => (m1[prop] > m2[prop] ? order: -1 * order))
//   }

//   render () {
//     return (
//         <div id="Browse" className="page">
//           {
//             this.state.filterMenuActive && 
//               <div className="cover" onClick={()=>{this.setState({filterMenuActive: false})}} />
//           }
//           <Filters active={this.state.filterMenuActive? "active": "inactive"} config={filterConfig} list={this.all_movies} action={(mvs)=> {this.setState({movies: mvs})}} />
//           <div id="ControlPanel">
//             <div id="Sort">
//               <div>Sort <Caret/></div>
//               <ul id="SortOptions">
//                 {Object.keys(SORT).map(key => (
//                   <li key={key} className={this.state.sort === key ? 'active' : ''} onClick={()=>{this.setState({'sort': key})}}>{key}</li>
//                 ))}
//               </ul>
//             </div>
//             <div id="Categories">
//               <div className={!this.state.genre? 'active': ''} onClick={()=>{this.setState({genre: null})}}>All</div>
//               {this.state.genres.map(genre => (
//                 <div className={this.state.genre==genre["ID"]? 'active' : ''} onClick={()=>{this.setState({genre:genre['ID'] })}} >{genre['LABEL']}</div>
//               ))}
//             </div>
//             <div id="FiltersToggle" onClick={()=>{this.setState({"filterMenuActive": !this.state.filterMenuActive})}} className={this.state.filterMenuActive? 'active': ''} ><Filter/>Filters</div>
//           </div>
//           <div id="BrowseResults">
//             {this.state.movies.filter(movie=>(
//                 !this.state.genre || movie['GENRE'].indexOf(this.state.genre) != -1
//               )).length==0 && <div id="alert">
//                 We are sorry we could find no titles matching your search criteria.
//                 To learn more about the state of lesbian cinema, click here.
//                 Otherwise, similar searches with results are:  
//               </div>}

//             {
//               this.sortMovies(this.state.movies).filter(movie=>(
//                 !this.state.genre || movie.GENRE.indexOf(this.state.genre) != -1
//               )).map(movie => (
//                 <Link to={'/movies/' + movie.ID}>
//                   <div className="movietile">
//                     <div className="screenshot" alt={movie.CAPTION} style={{backgroundImage: 'url(/movie-pictures/' + movie.FILENAME + ')'}} />
//                     <div className="description">
//                       <h3>{movie.TITLE}</h3>
//                       <p> {movie.BIO}</p>
//                     </div>
//                     <span>{movie.YEAR}</span>
//                     <Rating score={movie.AVG_RATING} rotated={true}/ >
//                   </div>
//                 </Link>
//               ))
//             }
//           </div>
//           <div className="spacer"/>
//           <Footer />
//         </div>
//     )
//   }
// }

// var movies = [
//   {
//     id: 1,
//     title: "But I'm a Cheerleader",
//     year: "1999",
//     rating: 4.5,
//     bio: "A popart, lesbian classic, an all-american cheerleader must attend conversion therapy.",
//     screenshot: 'movie-pictures/but-im-a-cheerleader-001.webp',
//     category: ["Comedy", "Cult Classic", "Romance"]
//   },
//   {
//     id: 2,
//     title: "Blue is the warmest color",
//     year: "2013",
//     rating: 3.5,
//     bio: "If the male gaze were a love scene.",
//     screenshot: '/movie-pictures/blue-is-the-warmest-color-000.jpg',
//     category: ["Drama", "Romance"]
//   },
//   {
//     id: 3,
//     title: "Desert Hearts",
//     year: "1985",
//     rating: 4.7,
//     bio: "Who knew it could be so wet in the desert.",
//     screenshot: '/movie-pictures/desert-hearts-000.jpg',
//     category: ["Drama", "Romance", "Cult Classic"]
//   },
//   {
//     id: 4,
//     title: "Imagine me and you",
//     year: "2007",
//     rating: 4.5,
//     bio: "A woman meets the gaze of a florist, there's just one problem, she's already walking down the aisle.",
//     screenshot: 'movie-pictures/imagine-me-and-you-000.jpg',
//     category: ["Comedy", "Romance", "Cult Classic"]
//   },
//   {
//     id: 5,
//     title: "Rafiki",
//     year: "2018",
//     rating: 4.8,
//     bio: "Against the backdrop and LGBT rights in Kenya, two girls love.",
//     screenshot: 'movie-pictures/rafiki-000.jpg',
//     category: ["Drama", "Romance"]
//   },
//   {
//     id: 6,
//     title: "D.E.B.S",
//     year: "2004",
//     rating: 4.8,
//     bio: "The one who is best at lying, lies best to themselves.",
//     screenshot: "movie-pictures/debs-000.png",
//     category: ["Cult Classic", "Comedy", "Romance"]
//   },
//   {
//     id: 7,
//     title: "Lost and Delirious",
//     year: "2001",
//     rating: 2.7,
//     bio: "The girls boarding school dream.",
//     screenshot: "/movie-pictures/lost-and-delirious-000.jpg",
//     category: ["Drama"]
//   },
//   {
//     id: 8,
//     title: "Ammonite",
//     year: "2021",
//     rating: 4.7,
//     bio: "An overlooked Geologist discovers there is more to life than fossils. (pussy)",
//     screenshot: "/movie-pictures/ammonite-000.jpg",
//     category: ["Drama", "Period-Piece", "Romance"],
//   }
// ]
// const SORT = {
//   "Most Popular": ("NUM_RATING", -1),
//   "Least Popular": ("NUM_RATING", 1),
//   "Highest Rating": ["AVG_RATING", -1],
//   "Lowest Rating": ["AVG_RATING", 1],
//   "Most Recent Release": ["YEAR", -1],
//   "Least Recent Release": ["YEAR", 1],
// }

