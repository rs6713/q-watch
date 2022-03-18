import React, { Component } from 'react';
import Search from '../pages/components/Search';
import '../App.scss'

class Main extends Component {
  constructor(props){
    super(props)

  }

  render () {
    return (
        <div id="Main" className="page">
          <div id="TitlePage">
            <div className="background" />
            <div id="Title" >
              <h1>Q-WATCH</h1>
              <Search placeholder="Query Queer Watches" />
            </div>
          </div>
        </div>
    )
  }
}

export default Main