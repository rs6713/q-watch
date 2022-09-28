import {SORT} from './defaults';
import Loader from './Loader';
import MovieTile from './MovieTile';

function sortMovies(movies, sort){
  /* Sort Movies by properties.*/
  let prop = SORT[sort][0]
  let order = SORT[sort][1]
  
  return movies.sort((m1, m2) => (m1[prop] > m2[prop] ? order: -1 * order))
}

function filterMovies(movies, filters){

  if (movies === null) return null

  function filterMovie(movie){

    for(let property of Object.keys(filters)){
      if (filters[property] === null){
        continue;
      }
      if(movie[property].map(p => p.ID).indexOf(filters[property]) == -1){
        console.log(property, filters[property], movie[property])
        return false;
      }
    }
    return true;
  }

  return movies.filter(filterMovie)
}

function MovieList({movies, filters, sort}){

  let filteredMovies = filterMovies(movies, filters)
  var content;

  if (filteredMovies === null){
    content = <div/>;
  }else if(filteredMovies.length === 0){
    content = <div id="alert">
      We are sorry we could find no titles matching your search criteria.
      To learn more about the state of lesbian cinema, click here.
      Otherwise, similar searches with results are:  
    </div>
  }else{
    content = sortMovies(filteredMovies, sort).map(movie => (
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
