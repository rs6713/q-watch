import React, { useState, useEffect } from 'react';
import {Link} from 'react-router-dom';
import Footer from './components/Footer';
import Gallery from './components/Gallery';
import Loader from './components/Loader';
import Rating from './components/Rating';
import Quote from './components/Quote';
import {formatRuntime} from '../utils.js';
import Bubbles from './components/Bubbles';
import ExpandableBubbles from './components/ExpandableBubbles'
import {sourceDisclaimer} from '../constants'
import Source from './components/Source';
import styles from '../scss/defaults.scss';

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

  const [id, setId] = useState(path[path.length-1])
  const [playTrailer, setPlayTrailer] = useState(false);
  const [movie, setMovie] = useState(null);
  const { pageHeight, pageWidth } = useWindowDimensions();
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
      console.log(data)
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

  var largeScreenWidth = parseInt(styles.WIDTH_LARGE_SCREEN)

  if(movie !== null){
    content = (<div id="MovieContainer">
      <div id="MovieContents">
        <div id="MovieTitle">
          <Rating rating={movie.AVG_RATING} rotated={true} id={movie.ID} movieTypes={movie.TYPES} />
          <h1>{movie.TITLE}</h1>
          <h2>
            {formatRuntime(movie.RUNTIME)}&nbsp;&#9679;&nbsp;
            {movie.AGE["LABEL"]}&nbsp;&#9679;&nbsp;
            {movie.LANGUAGE}&nbsp;&#9679;&nbsp;
            {movie.COUNTRY}
          </h2>
          <div id="aside">{movie.YEAR}</div>
        </div>
        <div id="MovieParts">
          <p>{movie.SUMMARY}</p>
          <Bubbles items={movie.GENRES} />
          {/* {movie.SOURCES.length > 0 &&
            <div id="findMe">
              <h2>
                Find Me On
                {movie.TRAILER && <span id="watchTrailer" onClick={()=>{setPlayTrailer(true)}}>
                  Watch Trailer
                </span>
                }
              </h2>
              <span className="disclaimer">({sourceDisclaimer})</span>
              <div>
                {movie.SOURCES.map((source, i) => <Source key={i} id={source.ID} />)}
              </div>
            </div>
          } */}
          <ExpandableBubbles items={movie.TROPE_TRIGGERS} aside="(Potential for upsetting content/spoilers)" title="Trope/Trigger Warnings" expandable={true}/>
          <ExpandableBubbles items={movie.REPRESENTATIONS} title="Representation Matters" expandable={false} />
          <Quote quote={movie.quote}/>
          {pageWidth < largeScreenWidth && <Gallery images={movie.IMAGES} />}
        </div>
        
      </div>
      {pageWidth >= largeScreenWidth && <Gallery images={movie.IMAGES} />}

    </div>)
  }


  return (
      <div id="Movie" className="page">
        <div id="MovieControls">
          
          <ShuffleMovie aria-label="Choose Random Movie" title="Choose random movie." className="ShuffleMovie" onClick={pickRandomMovie}/>
          <Link to="/browse">
            <ReturnMovie aria-label="Return to Browse" title="Return to Browse" className="ReturnMovie" />
          </Link>
        </div>

        {
          playTrailer && 
            <div className="cover" onClick={()=>{setPlayTrailer(false)}} />
        }
        {
          playTrailer && movie.trailer && 
          <iframe className="trailer" src={movie.TRAILER} frameBorder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          autoPlay={true} allowFullScreen></iframe>
        }
        {content}
        <Footer />
      </div>
  )
}

export default Movie