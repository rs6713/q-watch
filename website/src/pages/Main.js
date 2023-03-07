import React from 'react';
import { useEffect, useState } from 'react';
import Image from './components/Image';
import {Link} from 'react-router-dom';
import Search from '../pages/components/Search';
import Options from './components/Options'
import Footer from './components/Footer'
import PieChart from './Graphs/PieChart'
import '../App.scss'
import Bisexual from '../static/images/person-bisexual.png'

import {ReactComponent as Query} from '../static/icons/query.svg'
import {ReactComponent as Graph} from '../static/icons/graph.svg'
import {ReactComponent as Movie} from '../static/icons/movie.svg'


const PHRASES = [
  "**I will go down with this ship.... (screams in Dido)**",
  "Come for the lesbians. Stay for the lesbians.",
]
const COUNT_CATEGORIES = {
  'LGBTQIA+ Categories': 'LGBTQIA+ Categories',
  'Genres': 'Genres',
  'Tropes / Triggers': 'Tropes / Triggers',
  'Representations': 'Representations'
}

function Main(){
  const [movieGif, setMovieGif] = useState(null);
  const [movieCounts, setMovieCounts] = useState(null);
  const [countCategory, setCountCategory] = useState('LGBTQIA+ Categories')

  //Data Fetching Called once at mount/dismount
  useEffect(() => {
    fetch(`/api/gif/random`, {
      method: 'GET',
      headers: {
        'cache-control': 'no-store',
      }
    }).then(res => res.json()).then(data => {
      setMovieGif(data);
    })
  }, []);

  useEffect(() => {
    fetch('/api/movies/count', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'cache-control': 'no-store',
      },
      body: JSON.stringify({
        "groups": {
          'LGBTQIA+ Categories': ['TYPES'],
          'Genres': ['GENRES'],
          'Tropes / Triggers': ["TROPE_TRIGGERS"],
          'Representations': ['REPRESENTATIONS']
        }
      })//this.state.filterCriteria
    }).then(res => res.json()).then(data => {
      console.log(data)
      setMovieCounts(data)
    })
  }, []);



  var backgroundDiv = <div className="background"></div>
  if(movieGif !== null){
    backgroundDiv = <div className="background image">
      {Image(movieGif.FILENAME, movieGif.CAPTION)}
    </div>
  }
  

  return (
    <div id="Main" className="page">
      <div id="TitlePage">
        {backgroundDiv}
        <div id="Title" >
          <h1>Q-WATCH</h1>
          <Search placeholder="Query Queer Watches" />
        </div>
        {movieGif !== null && 
          <div id="MovieInfo">
            <Link to={"/movies/" + movieGif.MOVIE_ID} >
              <h3>{movieGif.TITLE}</h3>
              <h3>{movieGif.YEAR}</h3>
            </Link>
          </div>
        }
      </div>
      <div id='Welcome' className='block'>
        <div>
          <h2>Find<br></br>Yourself</h2>
          <p><b>Q-Watch was created with the goal of helping LGBTQIA+ persons, find the movies that not only fit their preferred genre, but has characters that look, live and love like them. </b><br/><br/>As always, we stand on the shoulders of giants; there is a plethora of hidden gems in our history, we hope to help you find stories new <b>and old</b> that satisfy your <span className='explainer'><b><i>quavings</i></b><span>queer cravings</span> </span>. </p>
        </div>
        <div>
          <img src={Bisexual} alt="Bisexual Person watching Bisexual Movies" />;
        </div>
      </div>
      <div className='leftblock'>
        <div id="ControlPanel">
          <Options name='Category' updateOption={setCountCategory} option={countCategory} options={COUNT_CATEGORIES} />
        </div>
      </div>
      <div id='Understand' className='block'>
        <div>
          
          <PieChart dataset={movieCounts} dataChoice={countCategory}/>
        </div>
        <div>
          {movieCounts !== null && <h2>{movieCounts['TOTAL']} MOVIES AND COUNTING</h2>}
        </div>
      </div>
      <div className='centerblock' id='Analytics'>
        <div>
          <Query/>
          <p>
          Creating a searchable archive of Queer media, presented us with the unique opportunity to evaluate the state of Queer Cinema. <br/><br/>It is a myth that progress is linear, and guaranteed.
          </p>
        </div>
        <div>
          <Graph/>
          <p>
          As more money is injected into LGBT entertainment than ever before, we want to understand our changing landscape. <br/><br/>Who exactly is benefiting the most from these investments, and what parts of LGBT representation are still being neglected?
          </p>
        </div>
        <div>
          <Movie/>
          <p>We are constantly adding new movies to expand our archive, to make our data analysis more representative of the true state of global Queer Cinema.</p>
        </div>
      </div>

        <Footer />

    </div>
  )
}

// class Main extends Component {
//   constructor(props){
//     super(props)
//     this.state={

//     }
//   }

//   loadBackground(){
//     //TODO: Get images from server side
//     var movies = [
//       {
//         "gif": 'debs-000.gif',
//         "year": 2004,
//         "title": "D.E.B.S",
//         "id": 5
//       },
//       {
//         "gif": 'desert-hearts-000.gif',
//         "year": 1986,
//         "title": "Desert Hearts",
//         "id": 5
//       },
//       {
//         "gif": 'i-cant-think-straight-000.webp',
//         "year": 2009,
//         "title": "I can't think straight",
//         "id": 5
//       },
//       {
//         "gif": 'rafiki-000.gif',
//         "year": 2018,
//         "title": "Rafiki",
//         "id": 5
//       },
//       {
//         "gif": 'ammonite-000.gif',
//         "year": 2021,
//         "title": "Ammonite",
//         "id": 8
//       },
//     ]
//     var randIndex = Math.floor(Math.random()*movies.length);
//     this.setState({
//       movie: movies[randIndex]
//     })
//   }

//   componentWillMount(){
//     this.loadBackground()
//   }
  
//   render () {
//     //'url(../static/' + this.state.backgroundgif + ')'
//     return (

//     )
//   }
// }

export default Main