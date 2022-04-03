import React, { Component } from 'react';
import {Link} from 'react-router-dom';
import Search from '../pages/components/Search';
import '../App.scss'

const PHRASES = [
  "**I will go down with this ship.... (screams in Dido)**",
  "Come for the lesbians. Stay for the lesbians.",
]

class Main extends Component {
  constructor(props){
    super(props)
    this.state={

    }
  }

  loadBackground(){
    //TODO: Get images from server side
    var movies = [
      {
        "gif": 'debs-000.gif',
        "year": 2004,
        "title": "D.E.B.S",
        "id": 5
      },
      {
        "gif": 'desert-hearts-000.gif',
        "year": 1986,
        "title": "Desert Hearts",
        "id": 5
      },
      {
        "gif": 'i-cant-think-straight-000.webp',
        "year": 2009,
        "title": "I can't think straight",
        "id": 5
      },
      {
        "gif": 'rafiki-000.gif',
        "year": 2018,
        "title": "Rafiki",
        "id": 5
      },
      {
        "gif": 'ammonite-000.gif',
        "year": 2021,
        "title": "Ammonite",
        "id": 8
      },
    ]
    var randIndex = Math.floor(Math.random()*movies.length);
    this.setState({
      movie: movies[randIndex]
    })
  }

  componentWillMount(){
    this.loadBackground()
  }
  
  render () {
    //'url(../static/' + this.state.backgroundgif + ')'
    return (
        <div id="Main" className="page">
          <div id="TitlePage">
            <div className="background" style={{backgroundImage: 'url(' + window.location.origin + '/movie-gifs/' + this.state.movie.gif.replace('./', '') + ')' }} />
            <div id="Title" >
              <h1>Q-WATCH</h1>
              <Search placeholder="Query Queer Watches" />
            </div>
            <div id="MovieInfo">
              <Link to={"/movies/" + this.state.movie.id} >
                <h3>{this.state.movie.title}</h3>
                <h3>{this.state.movie.year}</h3>
              </Link>
            </div>
          </div>
        </div>
    )
  }
}

export default Main