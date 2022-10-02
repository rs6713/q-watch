import React, { useState, useEffect } from 'react';
import {Link} from 'react-router-dom';
import Footer from './components/Footer';
import Rating from './components/Rating';
import {formatRuntime} from '../utils.js';
import Bubbles from './components/Bubbles';
import ExpandableBubbles from './components/ExpandableBubbles'
import {sourceDisclaimer} from '../constants'
import Source from './components/Source';
import Image from './components/Image';
import {ReactComponent as ReturnMovie} from '../static/icons/return.svg';
import {ReactComponent as ShuffleMovie} from '../static/icons/shuffle.svg';

function Movie(props){
 
  var path = window.location.href.split("/")
  var id = path[path.length-1]

  const [playTrailer, setPlayTrailer] = useState(false);
  const [movie, setMovie] = useState({
    'SOURCES': [],
    'TROPE_TRIGGERS': [],
    'GENRES': [],
    'REPRESENTATIONS':[],
    'IMAGES': []
  });

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
  }, []);


  return (
      <div id="Movie" className="page">
        <div id="MovieControls">
          
          <ShuffleMovie aria-label="Choose Random Movie" title="Choose random movie." className="ShuffleMovie"/>
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
        <div id="MovieContainer">
          
          <div id="MovieContents">
            <Rating rating={movie.AVG_RATING} rotated={true} id={movie.ID} />
            <h1>{movie.TITLE}</h1>
            <h2>
              {formatRuntime(movie.RUNTIME)}&nbsp;&#9679;&nbsp;
              Rating {movie.AGE}&nbsp;&#9679;&nbsp;
              {movie.LANGUAGE}
            </h2>
            <p>{movie.BIO}</p>
            <div id="aside">{movie.YEAR}</div>
            
            <Bubbles items={movie.GENRES} />
            {movie.SOURCES.length > 0 &&
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
            }
            {
              movie.TROPE_TRIGGERS.length > 0 && <ExpandableBubbles items={movie.TROPE_TRIGGERS} aside="(Potential for upsetting content/spoilers)" title="Trope/Trigger Warnings" />
            }
            {
              movie.REPRESENTATIONS.length > 0 && <ExpandableBubbles items={movie.REPRESENTATIONS} title="Representation Matters" expandable={false} />
            }

            <div id="quote">
              "{movie.quote}"
            </div>

          </div>
          <div id="MovieScreenshots">
            {movie.IMAGES.map((img)=>(
              Image(img.FILENAME, img.CAPTION)
            ))}
          </div>
        </div>
        <Footer />
      </div>
  )
}

export default Movie