import React from 'react';
import {Link} from 'react-router-dom';
import Loader from './Loader';
import MovieTile from './MovieTile';
import Alert from './Alert';

function MovieList({movies}){

  var content;

  if (movies === undefined){
    content = <div/>;
  }else if(movies === null){
    content = <div>
      <Alert header='Whoops!' subtitle='We were unable to fetch this movie list at the moment'/>
    </div>
  }else if(movies.length === 0){
    content = <div className="Alert">
      We are sorry we could find no titles matching your search criteria.<br/>
      To learn more about the state of queer cinema, click <Link to={'/data/overview'}>here</Link>.
      
    </div>
  }else{
    content = movies.map((movie, idx) => (
      <MovieTile movie={movie} key={idx}/>
    ))
  }

  return (
    <div id="BrowseResults" style={!movies || movies.length===0 ?{'flex': '1 1'}: {}}>
      <Loader isLoading={movies === undefined} />
      {content}
    </div>
  )
}

export default MovieList;
