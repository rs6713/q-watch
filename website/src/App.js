import React, { Component } from 'react';
import {
  BrowserRouter as Router,
  Route,
  Routes
} from 'react-router-dom';
import Main from './pages/Main';
import './App.scss';

class App extends Component {
  constructor (props) {
    super(props)
  }

  render () {
    return (
      <div className='App'>
        <Router basename={process.env.PUBLIC_URL}>
          <Routes>
            <Route exact path='/' element={<Main />} />
          </Routes>
        </Router>
      </div>
    )
  }
}


export default App;
