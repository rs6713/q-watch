import React, { Component, useState, useEffect} from 'react';
import Footer from './components/Footer';

import Filters from './components/Filters';
import Labels from './components/Labels';
import MovieList from './components/MovieList';
import Sort from './components/Sort';
import Indexer from './components/Indexer';


import {ReactComponent as Filter} from '../static/icons/filter.svg'




const filterConfig = {
  title: "Movie Filters",
  filterSections:[
    {
      title: "By Women for Women",
      subtitle: "Sometimes things are best done yourself.",
      type: "checkbox",
      filters:[
        {
          label: "Female Director",
          id: "female_director",
          descrip: "The movie is directed by a woman"
        },
        {
          label: "Female Writer",
          id:"female_writer",
          descrip: "The movie is written by a woman"
        }
      ]
    },
    {
      title: "Movie Qualities",
      filters: [
        {
          label: "Age Range",
          id: "age_range",
          type: "slider",
          options: ["Coming of Age", "Young Adult", "30-60", "60+"]
        },
        {
          label: "Language",
          id: "language",
          type: "dropdown",
        },
      ]
    },
    {
      title: "Tropes / Trigger Warnings",
      id: "warnings",
      expandable: true,
      warning: "IMPLIED SPOILERS",
      subtitle: "Early mainstream, queer media was messy at best. Select the tropes you wish to avoid.",
      type: "bubble",
      filters:[
        {
          label: "Teacher/Student",
          id:"teacher_student",
          descrip: "Because it's illegal"
        },
        {
          label: "Lesbian Bed death",
          id: "lesbian_bed_death"
        },
        {
          label: "Bury your gays",
          id: "bury_your_gays"
        },
        {
          label: "Sexual Violence",
          id: "sexual_violence"
        },
        {
          label: "Suicide",
          id: "suicide",
          descrip: ""
        },
        {
          label: "Conversion Therapy",
          id: "conversion_therapy",
          descrip: ""
        },
        {
          label: "Hate Crimes",
          id: "hate_crimes",
          descrip: ""
        },
        {
          label: "They don't end up together.",
          id: "lonely_lesbians",
          descrip: ""
        },
        {
          label: "Unaccepting Family/Disowning",
          id: "family_troubles",
          descrip: ""
        },
        {
          label: "Bi Erasure",
          id: "bi_erasure",
          descrip: ""
        },
        {
          label: "It was just a phase",
          id: "it_was_a_phase",
          descrip: ""
        }
      ]
    },
    {
      title: "Representation Matters",
      id: "representation",
      warning: "See yourself on the bigscreen.",
      subtitle: "We have tried our best, but if you feel we are missing filters here, please let us know, email us at q-watch.gmail.com.",
      disclaimers: [
        "Unfortunately some options may be missing or extremely broad, due to a lack of representation in the media itself.",
        "Representation here, guarantees presence, but not good representation: see tropes/trigger warnings."
      ],
      type: "bubble",
      filters: [
        {
          label: "Black Love",
          id: "blackLove",
          descrip: "Black characters loving black characters."
        },
        {
          label: "POC Love",
          id: "pocLove",
          descrip: "POC characters loving POC characters."
        },
        {
          label: "QTIPOC",
          id: "qtipoc",
          descrip: "At least one of the main characters is POC"
        },
        {
          label: "Transgender",
          id: "transgender",
          descrip: "At least one of the main characters is trans"
        },
        {
          label: "Disability",
          id: "disability",
          descrip: "At least one of the main characters is disabled"
        },
        {
          label: "Butch",
          id: "butch",
          descrip: "At least one of the main characters is butch"
        },
        {
          label: "Bisexual",
          id: "bisexual",
          descrip: "At least one of the main characters is bisexual"
        },
        {
          label: "Polyamory",
          id: "polyamory",
          descrip: "The relationship is polyamorous"
        },
        {
          label: "Jewish",
          id: "jewish",
          descrip: "At least one of the main characters is jewish"
        }
      ]
    },
    {
      title: "Can't find what you're looking for?",
      subtitle: "Unfortunately Queer cinema (like most media) can be majority homogeneous. Allowing these options, may help you find more movies for specific demographics/story types",
      type: "checkbox",
      filters:[
        {
          label: "Queer Love can be Side Stories/Characters",
          id: "allowSideCharacters"
        },
        {
          label: "Queerness can be implied (only)",
          id: "allowImplied"
        }
      ]
    }
  ]
}


function Browse(){

  const [filterActive, setFilterActive] = useState(false);
  const [movies, setMovies] = useState(null);
  const [criteria, setCriteria] = useState({});
  const [sort, setSort] = useState(["YEAR", -1]);
  const [index, setIndex] = useState(1);
  const [nIndexes, setNIndexes] = useState(null);


  // Data Fetching Called at criteria updates
  useEffect(() => {
    // Loading is true while movies are null
    setMovies(null);

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
    })
  }, [criteria, sort, index]);

  function updateCriteria(update){

    let newCriteria = {...criteria, ...update}

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

      {/* <Filters active={filterActive? "active": "inactive"} config={filterConfig} list={allMovies} action={(mvs)=> {setMovies(mvs)}} />
       */}
      <div id="ControlPanel">
        <Sort updateSort={setSort} sort={sort} />
        <Labels labelType="GENRES" updateLabel={updateCriteria}/>
        
        <div id="FiltersToggle" onClick={()=>{setFilterActive(!filterActive)}} className={filterActive? 'active': ''} ><Filter/>Filters</div>
      </div>

      <MovieList movies={movies} />
      <Indexer nIndexes={nIndexes} updateIndex={setIndex} index={index} />
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

