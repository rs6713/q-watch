import React, { useState, useEffect } from 'react';
import {Link, useNavigate} from 'react-router-dom';
import Footer from './components/Footer';
import Gallery from './components/Gallery';
import Loader from './components/Loader';
import Rating, {getIcon, RatingDisplay} from './components/Rating';
import Quote from './components/Quote';
import Opinion from './components/Opinion';
import {formatRuntime} from '../utils.js';
import Bubbles from './components/Bubbles';
import Button from './components/Button';
import ExpandableBubbles from './components/ExpandableBubbles'

import Source from './components/Source';
import styles from '../scss/defaults.scss';
import {Icon} from './components/Image'
import HTMLString from 'react-html-string';
import MainMenu from './components/MainMenu';
import Sources from './components/Sources';
import {formatLanguage} from '../utils';

import {ReactComponent as ReturnMovie} from '../static/icons/return.svg';
import {ReactComponent as ShuffleMovie} from '../static/icons/shuffle.svg';

function getWindowDimensions() {
  const { innerWidth: pageWidth, innerHeight: pageHeight } = window;
  return {
    pageWidth, pageHeight
  };
}

function useWindowDimensions() {
  const [windowDimensions, setWindowDimensions] = useState(getWindowDimensions());

  useEffect(() => {
    function handleResize() {
      setWindowDimensions(getWindowDimensions());
    }

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return windowDimensions;
}



function Movie(props){
 
  var path = window.location.href.split("/")

  const navigate = useNavigate();

  const [id, setId] = useState(path[path.length-1])

  const [movie, setMovie] = useState(null);
  const { pageHeight, pageWidth } = useWindowDimensions();
  const [showTrailer, setShowTrailer] = useState(false);
  //const [randomMovieId, setRandomMovieId] = useState(3)

  function pickRandomMovie(){
    setMovie(null);
    fetch(`/api/movie/random`, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'cache-control': 'no-store',
      },
      body: JSON.stringify({
        "properties":['ID']
      })//this.state.filterCriteria
    }).then(res => res.json()).then(data => {
      setId(parseInt(data['ID']));
      window.location.href = ('/movies/'+ data['ID'])
    })
  }


  // Data Fetching Called once at mount/dismount
  useEffect(() => {
    fetch(`/api/movie/${id}`, {
      method: 'GET',
      headers: {
        'cache-control': 'no-store',
      }
    }).then(res => res.json()).then(data => {
      setMovie(data);
    })
  }, [id]);

  var content = <div id="MovieContainer">
    <Loader isLoading={movie===null} />
  </div>;
    function gIcon(typ){
      let Ic = getIcon([typ])
      return <Ic />
    }

  var largeScreenWidth = parseInt(styles.WIDTH_LARGE_SCREEN)

  if(movie !== null){
    content = (<div id="MovieContainer">
      {pageWidth >= largeScreenWidth && 
      <div className='GalleryContainer'>
        <Gallery images={movie.IMAGES} />
        <Quote quote={movie.quote}/>
      </div>}
      <div id="MovieContents">
        
        <div id="MovieTitle">
          <div id='MovieDetails'>
          <RatingDisplay 
            rating={movie.AVG_RATING}
            numRating={movie.NUM_RATING}
            id={movie.ID}
            movieTypes={movie.TYPES}
            votable={true}/>
          
          <div id="aside">
            
            <div id="MovieControls">
              <ShuffleMovie aria-label="Choose Random Movie" title="Choose random movie." className="ShuffleMovie" onClick={pickRandomMovie}/>
              
              <ReturnMovie aria-label="Return to Browse" title="Return to Browse" onClick={() => navigate(-1)} />
            </div>
            <div>{movie.YEAR}</div>
            <div>
              {movie.IMDB_ID && <a target='_blank' href={'https://www.imdb.com/title/tt'+movie.IMDB_ID}><Button onClick={()=>{}} text='IMDB' /></a>}
              {movie.TRAILER && <Button onClick={()=>{setShowTrailer(!showTrailer)}} text='Trailer' />}
            </div>
          </div>
          </div>
          
          <h1>{movie.TITLE}</h1>
          <Bubbles items={movie.TAGS} />
          <h2>
            {formatRuntime(movie.RUNTIME)}&nbsp;&#9679;&nbsp;
            {movie.AGE["LABEL"]}&nbsp;&#9679;&nbsp;
            {formatLanguage(movie.LANGUAGE)}&nbsp;&#9679;&nbsp;
            {movie.COUNTRY}&nbsp;&#9679;&nbsp;
            {movie.GENRES.map((genre, idx) => <Icon label={genre.LABEL} name={'genres/'+genre.ICON} key={idx}/>)}&nbsp;&#9679;&nbsp;
            {movie.TYPES.map((typ) => gIcon(typ))}
          </h2>
        
        </div>
        <div id="MovieParts">
          <HTMLString html={'<p>'+movie.SUMMARY + '</p>'}/>
          {pageWidth < largeScreenWidth && <Gallery images={movie.IMAGES} />}
          {/* <Bubbles items={movie.GENRES} /> */}
          {movie.SOURCES && movie.SOURCES.length > 0 &&
            <Sources sources={movie.SOURCES} />
          }
          <ExpandableBubbles items={movie.TROPE_TRIGGERS} aside="(Potential for upsetting content/spoilers)" title="Trope/Trigger Warnings" expandable={true}/>
          <ExpandableBubbles items={movie.REPRESENTATIONS} title="Representation Matters" expandable={false} />
          <Opinion opinion={movie.OPINION}/>
        {pageWidth < largeScreenWidth && <Quote quote={movie.quote}/> }

          
        </div>
        
      </div>
      

    </div>)
  }


  return (
      <div id="Movie" className="page">
        <MainMenu/>

        {
          showTrailer && 
            <div className="cover" onClick={()=>{setShowTrailer(false)}} />
        }
        {
          showTrailer && movie.TRAILER && 
          <iframe className="trailer" src={movie.TRAILER.replace('/watch?v=', '/embed/')} frameBorder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          autoPlay={true} allowFullScreen></iframe>
        }
        {content}
        <Footer />
      </div>
  )
}

export default Movie