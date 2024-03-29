import React from 'react';
import { useEffect, useState, useMemo} from 'react';
import Image from './components/Image';
import {Link} from 'react-router-dom';
import Search from '../pages/components/Search';
import Options from './components/Options'
import Footer from './components/Footer'
import PieChart from './Graphs/PieChart'
import MainMenu from './components/MainMenu'
import ChartLine from './Graphs/ChartLine'
import '../App.scss'
import Lgbt from '../static/images/group-lgbt.png'
import HTMLString from 'react-html-string';
import Alert from './components/Alert';

import {ReactComponent as Query} from '../static/icons/query.svg'
import {ReactComponent as Graph} from '../static/icons/graph.svg'
import {ReactComponent as Movie} from '../static/icons/movie.svg'
import {Icon} from './components/Image'
import Rating, {getIcon} from './components/Rating';
import {formatRuntime} from '../utils.js';
import Bubbles from './components/Bubbles';
import Counter from './components/Counter';
import {PercentDelta} from './components/Delta';
import {groupDataAgg} from './data/utils.js' //, generateCombinations, getMovieValues
import {formatLanguage} from '../utils';

import gif1 from '../static/images/backup_gifs/rafiki.gif';
import gif2 from '../static/images/backup_gifs/ammonite.gif';
import gif3 from '../static/images/backup_gifs/paris_is_burning.gif';
import gif4 from '../static/images/backup_gifs/the_half_of_it.gif';

const backupGifs = [gif1, gif2, gif3, gif4];

const PHRASES = [
  "I will go down with this ship...(screams in Dido)",
  "Come for the lesbians. Stay for the lesbians.",
  "Theyyyy do not give out Oscars for playing trans like they used to",
  "It's liked she reached up and put a string of lights around my heart",
  "The lily means I dare you to love me.",
  "I wish I knew how to quit you.",
  "We're here. We're queer.",
  "I like the wine, and not the label.",
  "I don't know what I am. I think I might be nothing.",
  "Swim the warm waters of sins of the flesh",
  "Yes, I live with a man. Yes, I’m a middle-aged fag.",
  "You can be gay, but you don't have to let nobody call you a faggot",
  "Yeah, it's always heartwarming to see a prejudice defeated by a deeper prejudice.",
  "If a bullet should enter my brain, let that bullet destroy every closet door.",
  "What happened to you? You happened to me.",
  "I have infinite tenderness for you.",
  "I want to show the world. How much I love you.",
  "My angel, flung out of space.",
  "I could tell the answer was yes. And that it was now.",
  "You make me feel something I absolutely cannot feel.",
  "Kiss me. Now. Infront of all these people.",
  "How you could live in an ocean of her thoughts.",
  "It is to you I devote a dreaming space.",
  "This is my Josh. And he is a homosexual.",
  "We are everywhere.",
  "Fuck the senator, I don’t give a damn what he thinks.",
  "No. But God knows we keep trying.",
  "Would you?",
  "But to be in love when you’re sad, that’s something else.",
  "You were my first everything.",
  "We accept the love we think we deserve.",
  "The only way to get through this is together.",
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
  const [movieGif, setMovieGif] = useState(undefined);
  const [movieFeatured, setMovieFeatured] = useState(undefined);
  const [movieCounts, setMovieCounts] = useState(undefined);
  const [countCategory, setCountCategory] = useState('LGBTQIA+ Categories')
  const [scrollActive, setScrollActive] = useState(true);
  const [ratingIcon, setRatingIcon] = useState(undefined);

  const backupGif = useMemo(() => {
    return backupGifs[parseInt(Math.random() * backupGifs.length)]
  })

  const welcomePhrase = useMemo(() => {
    var now = new Date();
    var start = new Date(now.getFullYear(), 0, 0);
    var diff = now - start;
    var oneDay = 1000 * 60 * 60 * 24;
    var day = Math.floor(diff / oneDay);
    return PHRASES[day % PHRASES.length]
  }, [])

  // const [movies, setMovies] = useState(null);
  // useEffect(() => {
  //     fetch('/api/movies', {
  //       method: 'POST',
  //       headers: {
  //         'Accept': 'application/json',
  //         'Content-Type': 'application/json',
  //         'cache-control': 'no-store',
  //       },
  //       body: JSON.stringify({
  //         "criteria": {},
  //         'properties': [
  //           'YEAR', 'RUNTIME', 'AGE', 'COUNTRY', 'LANGUAGE',
  //           'BOX_OFFICE_USD', 'BUDGET_USD',
  //           'TYPES', 'REPRESENTATIONS', 'TROPE_TRIGGERS', 'TAGS', 'INTENSITY',
  //           'AVG_RATING'
  //         ]
  //       })//this.state.filterCriteria
  //     }).then(res => res.json()).then(data => {
  //       setMovies(data["data"]);
  //     })
  // }, []);

  // Data Fetching Called once at mount/dismount
  useEffect(() => {
    fetch(`/api/movie/featured`, {
      method: 'GET',
      headers: {
        'cache-control': 'no-store',
      }
    }).then(res => res.json()).then(data => {
      if(Object.keys(data).length > 0){
        setRatingIcon(getIcon(data.TYPES))
        setMovieFeatured(data);
      }
    }).catch(err => {
      setMovieFeatured(null);
      setRatingIcon(null);
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
    }).catch(err => {
      // From provided backup list
      setMovieGif(null);
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
          'Tag': ['TAGS'],
          'Year': ['YEAR'],
          'Representation_Year': ['REPRESENTATIONS', 'YEAR'],
          'Type_Year': ['TYPES', 'YEAR']
        }
      })//this.state.filterCriteria
    }).then(res => res.json()).then(data => {
      setMovieCounts(data)
    }).catch(err => {
      setMovieCounts(null);
    })
  }, []);

  var backgroundDiv = <div className="background"></div>
  if(movieGif !== undefined){
    backgroundDiv = <div className="background image">
      {movieGif !== null && Image(movieGif.FILENAME, movieGif.CAPTION)}
      {movieGif === null && <img src={backupGif} />}
    </div>
  }


  let marqueeContent =  <div>
  <PercentDelta 
    dataset={movieCounts}
    dataChoice='Year'
    value2={[2022, 2021, 2020, 2019, 2018]}
    value1={[2017, 2016, 2015, 2014, 2013]}
    statement='5 Year LGBTQIA+'
    substatement='How many movies were released in 2018-22 compared to 2013-17?'
  />
  <PercentDelta 
    dataset={movieCounts}
    dataChoice='Year'
    value2={2022}
    value1={2021}
    statement='2022 LGBTQIA+'
    substatement='How many movies were released in 2022 compared to 2021?'
  />
   <PercentDelta 
    dataset={movieCounts}
    dataChoice='Representation_Year'
    value2={['QTIPOC, 2022', 'QTIPOC, 2021', 'QTIPOC, 2020']}
    value1={['QTIPOC, 2019', 'QTIPOC, 2018', 'QTIPOC, 2017']}
    statement='3 Year QTIPOC'
    substatement='How many movies had 1+ QTIPOC Characters in 2020-22 compared to 2017-19?'
  />
  <PercentDelta 
    dataset={movieCounts}
    dataChoice='Representation_Year'
    value2={['Black Love, 2022', 'Black Love, 2021', 'Black Love, 2020', 'Black Love, 2019', 'Black Love, 2018']}
    value1={['Black Love, 2017', 'Black Love, 2016', 'Black Love, 2015', 'Black Love, 2014', 'Black Love, 2013']}
    statement='5 Year Black Love'
    substatement='How many movies centered Black Love in 2018-22 compared to 2013-17?'
  />
  <PercentDelta 
    dataset={movieCounts}
    dataChoice='Representation_Year'
    value2={['Disability, 2022', 'Disability, 2021', 'Disability, 2020', 'Disability, 2019', 'Disability, 2018']}
    value1={['Disability, 2017', 'Disability, 2016', 'Disability, 2015', 'Disability, 2014', 'Disability, 2013']}
    statement='5 Year Disability'
    substatement='How many movies had characters with disabilities in 2018-22 compared to 2013-17?'
  />
  <PercentDelta 
    dataset={movieCounts}
    dataChoice='Type_Year'
    value2={['Transgender, 2022', 'Transgender, 2021', 'Transgender, 2020']}
    value1={['Transgender, 2019', 'Transgender, 2018', 'Transgender, 2017']}
    statement='3 Year Transgender'
    substatement='How many movies had transgender characters in 2020-22 compared to 2017-19?'
  />
  </div>// : <></>

  let featuredTitle = movieFeatured ? <div className='featuredTitle'>
  <h2>{movieFeatured.TITLE}</h2>
  <h3>
    {formatRuntime(movieFeatured.RUNTIME)}&nbsp;&#9679;&nbsp;
    {movieFeatured.AGE["LABEL"]}&nbsp;&#9679;&nbsp;
    {formatLanguage(movieFeatured.LANGUAGE)}&nbsp;&#9679;&nbsp;
    {movieFeatured.COUNTRY}&nbsp;&#9679;&nbsp;
    {movieFeatured.GENRES.map((genre) => <Icon label={genre.LABEL} name={'genres/'+genre.ICON} key={genre.LABEL} />)}&#9679;&nbsp;
    {movieFeatured.TYPES.map((typ) => getIcon([typ]))}
  </h3>
  <Bubbles items={movieFeatured.REPRESENTATIONS} />
  </div> : <></>;

  return (
    <div id="Main" className="page">
      <div id="TitlePage">
        {backgroundDiv}
        <h3 id='beta'>Beta</h3>
        <div id="Title" >
          
          <h1>Q-WATCH</h1>

          <Search placeholder={welcomePhrase} />
        </div>
        {movieGif && Object.keys(movieGif).indexOf('MOVIE_ID') !== -1 &&
          <div id="MovieInfo">
            <Link to={"/movies/" + movieGif.MOVIE_ID} >
              <h3>{movieGif.TITLE}</h3>
              <h3>{movieGif.YEAR}</h3>
            </Link>
          </div>
        }
        {/* <div className="arrow" onClick={scroll}>
          <span></span>
          <span></span>
          <span></span>
        </div> */}
      </div>
      <MainMenu/>
      <div className='contentContainer'>
      
      <div id='Welcome' className='block'>
        <div style={movieCounts === null? {'border-radius': 0} : {}}>
          <h2 className='bubbletext'>Find Yourself</h2>
          <p><b>Q-Watch was created with the goal of helping LGBTQIA+ persons, find the movies that not only fit their preferred genre, but has characters that look, live and love like them. </b><br/><br/>As always, we stand on the shoulders of giants; there is a plethora of hidden gems in our history, we hope to help you find stories new <b>and old</b> that satisfy your <span className='explainer'><b><i>quavings</i></b><span>queer cravings</span> </span>. </p>
        </div>
        <div>
          <img src={Lgbt} alt="LGBT Group of people watching LGBT Movies" />
        </div>
      </div>
      {  <div id='statsContainer'> 
        <div>
          {/* aria-hidden="true" for screenreaders second time */}
        {marqueeContent}{marqueeContent}
        </div>
      </div>}
      {movieFeatured && <h2 className='bubbletext'>Movie Of The Week</h2>}
      {movieFeatured && 
      <Link to={"/movies/"+movieFeatured.ID}>
      <div id='Featured'>
        <div>
        {featuredTitle}
        <div className='block'>
          
          <div>
            {Image(movieFeatured.FILENAME, movieFeatured.CAPTION)}
            <Rating 
              rating={movieFeatured.AVG_RATING}
              Icon={ratingIcon}
              noDefault={true}
              rotated={true}
            />
          </div>
          <div className='info'>
            <HTMLString html={'<p>'+ (movieFeatured.DESCRIP || movieFeatured.SUMMARY) + '</p>'}/>
          </div>
          </div>
          </div>
        </div>
        <div id='bg'/>
      </Link>
      
      }
      {movieCounts !== null &&
        <div className='leftblock' id='ControlPanelContainer'>
          <div id="ControlPanel">
            <Options name='Category' updateOption={setCountCategory} option={countCategory} options={COUNT_CATEGORIES} />
          </div>
        </div>
      }
      {
        movieCounts === null && <div id='Understand' className='block'>
          <Alert header='Whoops!' subtitle="It appears we can't access our data right now, but please feel free to explore our `Disclaimers` and `FAQ` sections." />
        </div>
      }
      {movieCounts && 
        <div id='Understand' className='block'>
          <div>
            <PieChart dataset={movieCounts} dataChoice={countCategory}/>
          </div>
          <div>
            <h2 className='bubbletext'>
              <span>
                <span className='bg'></span>
                <Counter total={movieCounts['TOTAL']}/>
              </span>
              <br/>
              MOVIES AND COUNTING
            </h2>
          </div>
        </div>
      }

      <div className='centerblock' id='Analytics'>
        <div>
          <div>
            <Query/>
            <span className='left'><span/></span>
            <span className='right'><span/></span>
          </div>
          <h2>The Opportunity</h2>
          <p>
          Creating a searchable archive of Queer media, presented us with the unique opportunity to evaluate the state of Queer Cinema. <br/><br/>It is a myth that progress is linear, and guaranteed.
          </p>
          
        </div>
  
        <div>
          <div>
            <Graph/>
            <span className='left'><span/></span>
            <span className='right'><span/></span>
          </div>
          <h2>Our Goals</h2>
          <p>
          As more money is injected into LGBT entertainment than ever before, we want to understand our changing landscape. <br/><br/>Who exactly is benefiting the most from these investments, and what parts of LGBT representation are still being neglected?
          </p>
        </div>
        <div>
          <div>
            <Movie/>
            <span className='left'><span/></span>
            <span className='right'><span/></span>
          </div>
          <h2>What's Next?</h2>
          <p>We are constantly adding new movies to expand our archive, to make our data analysis more representative of the true state of global Queer Cinema.</p>
        </div>
      </div>

        <Footer />
        </div>
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