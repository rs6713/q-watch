import React, { Component } from 'react';
import Footer from './components/Footer';

class Movie extends Component {
  constructor(props){
    super(props)

  }

  render () {
    return (
        <div id="Movie" className="page">
          Movie
          <Footer />
        </div>
    )
  }
}

export default Movie