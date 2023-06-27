import React, {useMemo} from 'react';
import {Link} from 'react-router-dom';
import Image from './Image';
import Rating, {getIcon} from './Rating';
import {Icon} from './Image'
import {formatRuntime, formatLanguage} from '../../utils.js';

function MovieTile({movie}){

  const RatingIcon = useMemo(() => {
    return getIcon(movie.TYPES)
  }, [])

  function gIcon(typ){
    let Ic = getIcon([typ])
    return <Ic />
  }
  return (
    <Link to={'/movies/' + movie.ID} key={movie.ID}>
      <div className="movietile" key={movie.ID}>
        {/* <div className="screenshot" alt={movie.CAPTION} style={{backgroundImage: 'url(/movie-pictures/' + movie.FILENAME + ')'}} /> */}
        <div className="screenshot">
          {Image(movie.FILENAME, movie.CAPTION)}
          <Rating 
            rating={movie.AVG_RATING}
            Icon={RatingIcon}
            rotated={true}
            noDefault={true}
          />
        </div>
        <div className="description">
          <h3>{movie.TITLE}</h3>
          <h4>
              {formatRuntime(movie.RUNTIME)}&nbsp;&#9679;&nbsp;
              {movie.AGE && movie.AGE["LABEL"]}&nbsp;&#9679;&nbsp;
              {formatLanguage(movie.LANGUAGE)}&nbsp;&#9679;&nbsp;
              {movie.COUNTRY}
            </h4>
            
          <p> {movie.BIO}</p>
          <h4>
              <span>{movie.TYPES.map((typ) => gIcon(typ))}</span>
              <span>{movie.GENRES.map((genre) => <Icon label={genre.LABEL} name={'genres/'+genre.ICON} />)}</span>
          </h4>
        </div>
        <span>{movie.YEAR}</span>
        
        {/* <Rating rating={movie.AVG_RATING} rotated={true} id={movie.ID} movieTypes={movie.TYPES} / > */}
      </div>
    </Link>
  )
}

export default MovieTile;


