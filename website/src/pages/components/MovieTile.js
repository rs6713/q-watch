import {Link} from 'react-router-dom';
import Image from './Image';
import Rating from './Rating';

function MovieTile({movie}){
  return (
    <Link to={'/movies/' + movie.ID} key={movie.ID}>
      <div className="movietile" key={movie.ID}>
        {/* <div className="screenshot" alt={movie.CAPTION} style={{backgroundImage: 'url(/movie-pictures/' + movie.FILENAME + ')'}} /> */}
        <div className="screenshot">
          {Image(movie.FILENAME, movie.CAPTION)}
        </div>
        <div className="description">
          <h3>{movie.TITLE}</h3>
          <p> {movie.BIO}</p>
        </div>
        <span>{movie.YEAR}</span>
        <Rating score={movie.AVG_RATING} rotated={true}/ >
      </div>
    </Link>
  )
}

export default MovieTile;

