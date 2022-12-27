import React from 'react';
import {Link} from 'react-router-dom';
import Loader from './Loader';
import MovieTile from './MovieTile';


function MovieList({movies}){

  var content;

  if (movies === null){
    content = <div/>;
  }else if(movies.length === 0){
    content = <div className="Alert">
      We are sorry we could find no titles matching your search criteria.<br/>
      To learn more about the state of queer cinema, click <Link to={'/data/explore'}>here</Link>.
      
    </div>
  }else{
    content = movies.map(movie => (
      <MovieTile movie={movie} />
    ))
  }

  return (
    <div id="BrowseResults">
      <Loader isLoading={movies === null} />
      {content}
    </div>
  )
}

export default MovieList;
