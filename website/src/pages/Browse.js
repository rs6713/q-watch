import React, { Component } from 'react';
import {Link} from 'react-router-dom';
import Footer from './components/Footer';
import Rating from './components/Rating';

var movies = [
  {
    id: 1,
    title: "But I'm a Cheerleader",
    year: "1999",
    rating: 4.5,
    bio: "A popart, lesbian classic, an all-american cheerleader must attend conversion therapy.",
    screenshot: 'movie-pictures/but-im-a-cheerleader-001.webp'
  },
  {
    id: 2,
    title: "Blue is the warmest color",
    year: "2013",
    rating: 3.5,
    bio: "If the male gaze were a love scene.",
    screenshot: '/movie-pictures/blue-is-the-warmest-color-000.jpg'
  },
  {
    id: 3,
    title: "Desert Hearts",
    year: "1985",
    rating: 4.7,
    bio: "Who knew it could be so wet in the desert.",
    screenshot: '/movie-pictures/desert-hearts-000.jpg'
  },
  {
    id: 4,
    title: "Imagine me and you",
    year: "2007",
    rating: 4.5,
    bio: "A woman meets the gaze of a florist, there's just one problem, she's already walking down the aisle.",
    screenshot: 'movie-pictures/imagine-me-and-you-000.jpg'
  },
  {
    id: 5,
    title: "Rafiki",
    year: "2018",
    rating: 4.8,
    bio: "Against the backdrop and LGBT rights in Kenya, two girls love.",
    screenshot: 'movie-pictures/rafiki-000.jpg'
  },
  {
    id: 6,
    title: "D.E.B.S",
    year: "2004",
    rating: 4.8,
    bio: "The one who is best at lying, lies best to themselves.",
    screenshot: "movie-pictures/debs-000.png"
  },
  {
    id: 7,
    title: "Lost and Delirious",
    year: "2001",
    rating: 2.7,
    bio: "The girls boarding school dream.",
    screenshot: "/movie-pictures/lost-and-delirious-000.jpg"
  },
  {
    id: 7,
    title: "Ammonite",
    year: "2021",
    rating: 4.7,
    bio: "An overlooked Geologist discovers there is more to life than fossils. (pussy)",
    screenshot: "/movie-pictures/ammonite-000.jpg"
  }
]

class Browse extends Component {
  constructor(props){
    super(props)

  }

  render () {
    return (
        <div id="Browse" className="page">
          <div id="BrowseResults">
            {
              movies.map(movie => (
                <Link to={'/movies/'+movie.id}>
                  <div className="movietile">
                    <div className="screenshot" style={{backgroundImage: 'url(' + movie.screenshot + ')'}} />
                    <div className="description">
                      <h3>{movie.title}</h3>
                      <p> {movie.bio}</p>
                    </div>
                    <span>{movie.year}</span>
                    <Rating score={movie.rating} rotated={true}/ >
                  </div>
                </Link>
              ))
            }
          </div>
          <Footer />
        </div>
    )
  }
}

export default Browse