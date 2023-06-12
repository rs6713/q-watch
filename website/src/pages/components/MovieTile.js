import React from 'react';
import {Link} from 'react-router-dom';
import Image from './Image';
import Rating, {getIcon} from './Rating';
import {Icon} from './Image'
import {formatRuntime} from '../../utils.js';

function MovieTile({movie}){

  function gIcon(typ){
    let Ic = getIcon([typ])
    return <Ic />
  }
  console.log(movie)
  return (
    <Link to={'/movies/' + movie.ID} key={movie.ID}>
      <div className="movietile" key={movie.ID}>
        {/* <div className="screenshot" alt={movie.CAPTION} style={{backgroundImage: 'url(/movie-pictures/' + movie.FILENAME + ')'}} /> */}
        <div className="screenshot">
          {Image(movie.FILENAME, movie.CAPTION)}
        </div>
        <div className="description">
          <h3>{movie.TITLE}</h3>
          <h4>
              {formatRuntime(movie.RUNTIME)}&nbsp;&#9679;&nbsp;
              {movie.AGE && movie.AGE["LABEL"]}&nbsp;&#9679;&nbsp;
              {movie.LANGUAGE}&nbsp;&#9679;&nbsp;
              {movie.COUNTRY}
            </h4>
            <h4>
              {movie.TYPES.map((typ) => gIcon(typ))}
              &nbsp;&#9679;&nbsp;
              {movie.GENRES.map((genre) => <Icon label={genre.LABEL} name={'genres/'+genre.ICON} />)}
            </h4>
          <p> {movie.BIO}</p>
        </div>
        <span>{movie.YEAR}</span>
        <Rating rating={movie.AVG_RATING} rotated={true} id={movie.ID} movieTypes={movie.TYPES} / >
      </div>
    </Link>
  )
}

export default MovieTile;

