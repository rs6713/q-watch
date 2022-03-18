import React, {Component} from 'react';
import {ReactComponent as SearchIcon} from '../../static/icons/search.svg'
import {Link} from 'react-router-dom';
import {ReactComponent as Scissor} from '../../static/icons/scissor.svg'

var movies = [
  {
    id: 1,
    title: "But I'm a Cheerleader",
    year: "1999",
    rating: 4.5
  },
  {
    id: 2,
    title: "Blue is the warmest color",
    year: "1999",
    rating: 4.5
  },
  {
    id: 3,
    title: "Desert Hearts",
    year: "1999",
    rating: 4.5
  },
  {
    id: 4,
    title: "Imagine me and you",
    year: "1999",
    rating: 4.5
  }
]

class Search extends Component {
  constructor(props){
    super(props)
    this.state = {
      query: "",
      movies: []
    }
  }
  componentDidMount() {

    this.getMovies();
  }

  getMovies = () => {
    this.setState({
      movies: movies
    })
  }

  render(){
    return (
      <div className="searchbar">
        <SearchIcon />
        <input placeholder={this.props.placeholder} onChange={event => this.setState({query: event.target.value})} />
        
        <div className="searchresults">
          {
            this.state.movies.filter(movie => {
              if(this.state.query === ""){
                return false;
              }
              if (movie.title.toLowerCase().includes(this.state.query.toLowerCase())) {
                return true;
              }
              return false;
            }).map((movie) => (
              <Link to={"/movies/" + movie.id} >
                <div className="searchresult">
                  <span>{movie.title}</span>
                  <div>{movie.year} &nbsp;&#9679;&nbsp; {movie.rating}&nbsp;<Scissor /></div>
                </div>
              </Link>
            ))
          }
        </div>
      </div>
    )
  }
}

export default Search