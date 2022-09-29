import Loader from './Loader';
import MovieTile from './MovieTile';


function MovieList({movies}){

  var content;

  if (movies === null){
    content = <div/>;
  }else if(movies.length === 0){
    content = <div id="alert">
      We are sorry we could find no titles matching your search criteria.
      To learn more about the state of lesbian cinema, click here.
      Otherwise, similar searches with results are:  
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
