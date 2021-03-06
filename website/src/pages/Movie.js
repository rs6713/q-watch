import React, { Component } from 'react';
import {Link} from 'react-router-dom';
import Footer from './components/Footer';
import Rating from './components/Rating';
import {formatRuntime} from '../utils.js';
import Bubbles from './components/Bubbles';
import ExpandableBubbles from './components/ExpandableBubbles'
import {sourceDisclaimer} from '../constants'
import Source from './components/Source';
import {ReactComponent as ReturnMovie} from '../static/icons/return.svg';
import {ReactComponent as ShuffleMovie} from '../static/icons/shuffle.svg';

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
    id: 8,
    title: "Ammonite",
    year: "2021",
    rating: 2.4,
    bio: "Acclaimed paleontologist Mary Anning works alone selling common fossils to tourists to support her ailing mother, but a chance job offer changes her life when a visitor hires her to care for his wife.",
    screenshots: [
      "/movie-pictures/ammonite-000.jpg",
      "/movie-pictures/ammonite-001.webp",
      "/movie-pictures/ammonite-002.jpg"
    ],
    runtime: (60 * 60 * 1.6),
    ageRating: 15,
    language: "ENG",
    quote: "A level of sexual gratuity unmatched since Blue is the Warmest Color",
    sources: [132, 453],
    tags: ["Romance", "Drama", "Period-Piece"],
    warnings: ["Mental Health", "Bereavement"],
    representations: ["WLW", "Scientists", "Age Difference"],
    trailer: "https://www.youtube.com/embed/Yd_nsFJAXV4"
  }
]

class Movie extends Component {
  constructor(props){
    super(props)
    var path = window.location.href.split("/")
    var id = path[path.length-1]

    this.state = {
      movie: movies.filter(m => m.id==id)[0],
      playTrailer: false
    }

  }

  render () {
    return (
        <div id="Movie" className="page">
          <div id="MovieControls">
            
            <ShuffleMovie aria-label="Choose Random Movie" title="Choose random movie." className="ShuffleMovie"/>
            <Link to="/browse">
              <ReturnMovie aria-label="Return to Browse" title="Return to Browse" className="ReturnMovie" />
            </Link>
          </div>

          {
            this.state.playTrailer && 
              <div className="cover" onClick={()=>{this.setState({playTrailer: false})}} />
          }
          {
            this.state.playTrailer && this.state.movie.trailer && 
            <iframe className="trailer" src={this.state.movie.trailer} frameBorder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            autoPlay={true} allowFullScreen></iframe>
          }
          <div id="MovieContainer">
            
            <div id="MovieContents">
              <Rating score={this.state.movie.rating} rotated={true} />
              <h1>{this.state.movie.title}</h1>
              <h2>
                {formatRuntime(this.state.movie.runtime)}&nbsp;&#9679;&nbsp;
                Rating {this.state.movie.ageRating}&nbsp;&#9679;&nbsp;
                {this.state.movie.language}
              </h2>
              <p>{this.state.movie.bio}</p>
              <div id="aside">{this.state.movie.year}</div>
              
              <Bubbles items={this.state.movie.tags} />
              {this.state.movie.sources.length > 0 &&
                <div id="findMe">
                  <h2>
                    Find Me On
                    {this.state.movie.trailer && <span id="watchTrailer" onClick={()=>{this.setState({playTrailer: true})}}>
                      Watch Trailer
                    </span>
                    }
                  </h2>
                  <span className="disclaimer">({sourceDisclaimer})</span>
                  <div>
                    {this.state.movie.sources.map((source, i) => <Source key={i} id={source.id} />)}
                  </div>
                </div>
              }
              {
                this.state.movie.warnings.length > 0 && <ExpandableBubbles items={this.state.movie.warnings} aside="(Potential for upsetting content/spoilers)" title="Trope/Trigger Warnings" />
              }
              {
                this.state.movie.representations.length > 0 && <ExpandableBubbles items={this.state.movie.representations} title="Representation Matters" expandable={false} />
              }


              <div id="quote">
                "{this.state.movie.quote}"
              </div>
              


            </div>
            <div id="MovieScreenshots">
              {this.state.movie.screenshots.map((img)=>(
                <img src={img} />
              ))}
            </div>
          </div>
          <Footer />
        </div>
    )
  }
}

export default Movie