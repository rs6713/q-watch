import React from 'react';
import { useEffect, useState } from 'react';
import Image from './components/Image';
import {Link} from 'react-router-dom';
import Search from '../pages/components/Search';
import Options from './components/Options'
import Footer from './components/Footer'
import PieChart from './Graphs/PieChart'
import '../App.scss'
import Lgbt from '../static/images/group-lgbt.png'
import HTMLString from 'react-html-string';

import {ReactComponent as Query} from '../static/icons/query.svg'
import {ReactComponent as Graph} from '../static/icons/graph.svg'
import {ReactComponent as Movie} from '../static/icons/movie.svg'
import {Icon} from './components/Image'
import Rating from './components/Rating';
import {formatRuntime} from '../utils.js';
import Bubbles from './components/Bubbles';
import Counter from './components/Counter';

const PHRASES = [
  "**I will go down with this ship.... (screams in Dido)**",
  "Come for the lesbians. Stay for the lesbians.",
]
const COUNT_CATEGORIES = {
  'LGBTQIA+ Categories': 'LGBTQIA+ Categories',
  'Genres': 'Genres',
  'Tropes / Triggers': 'Tropes / Triggers',
  'Representations': 'Representations',
  'Age': 'Age',
  'Intensity': 'Intensity',
  'Country': 'Country',
  'Tag': 'Tag'

}

function Main(){
  const [movieGif, setMovieGif] = useState(null);
  const [movieFeatured, setMovieFeatured] = useState(null);
  const [movieCounts, setMovieCounts] = useState(null);
  const [countCategory, setCountCategory] = useState('LGBTQIA+ Categories')
  const [scrollActive, setScrollActive] = useState(true);

  // Data Fetching Called once at mount/dismount
  useEffect(() => {
    fetch(`/api/movie/featured`, {
      method: 'GET',
      headers: {
        'cache-control': 'no-store',
      }
    }).then(res => res.json()).then(data => {
      setMovieFeatured(data);
    })
  }, []);

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
          'Representations': ['REPRESENTATIONS'],
          'Age': ['AGE'],
          'Intensity': ['INTENSITY'],
          'Country': ['COUNTRY'],
          'Tag': ['TAGS']
        }
      })//this.state.filterCriteria
    }).then(res => res.json()).then(data => {
      setMovieCounts(data)
    })
    
  }, []);

  var backgroundDiv = <div className="background"></div>
  if(movieGif !== null){
    backgroundDiv = <div className="background image">
      {Image(movieGif.FILENAME, movieGif.CAPTION)}
    </div>
  }

  function scroll(){
    document.getElementById("Welcome").scrollIntoView({behavior:"smooth", block: "start"});
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
        <div className="arrow" onClick={scroll}>
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
      <div id='Welcome' className='block'>
        <div>
          <h2 className='bubbletext'>Find Yourself</h2>
          <p><b>Q-Watch was created with the goal of helping LGBTQIA+ persons, find the movies that not only fit their preferred genre, but has characters that look, live and love like them. </b><br/><br/>As always, we stand on the shoulders of giants; there is a plethora of hidden gems in our history, we hope to help you find stories new <b>and old</b> that satisfy your <span className='explainer'><b><i>quavings</i></b><span>queer cravings</span> </span>. </p>
        </div>
        <div>
          <img src={Lgbt} alt="LGBT Group of people watching LGBT Movies" />
        </div>
      </div>
      {movieFeatured && 
      <div id='Featured'>
        <Link to={"/movies/"+movieFeatured.ID}>
        <div className='block'>
          <h2 className='bubbletext'>Movie Of The Week</h2>
          <div>
            {Image(movieFeatured.FILENAME, movieFeatured.CAPTION)}
            <Rating rating={movieFeatured.AVG_RATING} rotated={true} id={movieFeatured.ID} movieTypes={movieFeatured.TYPES} votable={false}/>
          </div>
          <div className='info'>
            
            <h2>{movieFeatured.TITLE}</h2>
            <h3>
              {formatRuntime(movieFeatured.RUNTIME)}&nbsp;&#9679;&nbsp;
              {movieFeatured.AGE["LABEL"]}&nbsp;&#9679;&nbsp;
              {movieFeatured.LANGUAGE}&nbsp;&#9679;&nbsp;
              {movieFeatured.COUNTRY}&nbsp;&#9679;&nbsp;
              {movieFeatured.GENRES.map((genre) => <Icon label={genre.LABEL} name={'genres/'+genre.ICON} />)}
            </h3>
            <Bubbles items={movieFeatured.REPRESENTATIONS} />
            
            <HTMLString html={'<p>'+movieFeatured.DESCRIP + '</p>'}/>
          </div>
        </div>
        </Link>
      </div>
      
      }
      <div className='leftblock' id='ControlPanelContainer'>
        <div id="ControlPanel">
          <Options name='Category' updateOption={setCountCategory} option={countCategory} options={COUNT_CATEGORIES} />
        </div>
      </div>
      <div id='Understand' className='block'>
        <div>
          
          <PieChart dataset={movieCounts} dataChoice={countCategory}/>
        </div>
        <div>
          {movieCounts !== null && <h2 className='bubbletext'>
            <span><span className='bg'></span><Counter total={movieCounts['TOTAL']}/></span> MOVIES AND COUNTING</h2>}
        </div>
      </div>


      
      
      <div className='centerblock' id='Analytics'>
        <div>
          <Query/>
          <h2>The Opportunity</h2>
          <p>
          Creating a searchable archive of Queer media, presented us with the unique opportunity to evaluate the state of Queer Cinema. <br/><br/>It is a myth that progress is linear, and guaranteed.
          </p>
        </div>
        <div>
          <Graph/>
          <h2>Our Goals</h2>
          <p>
          As more money is injected into LGBT entertainment than ever before, we want to understand our changing landscape. <br/><br/>Who exactly is benefiting the most from these investments, and what parts of LGBT representation are still being neglected?
          </p>
        </div>
        <div>
          <Movie/>
          <h2>What's Next?</h2>
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