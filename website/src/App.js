import React, { Component } from 'react';
import {
  BrowserRouter as Router,
  Route,
  Routes
} from 'react-router-dom';
import Main from './pages/Main';
import Browse from './pages/Browse';
import OverTime from './pages/OverTime';
import Country from './pages/Country';
import Rank from './pages/Rank';
import Movie from './pages/Movie';
import Menu from './pages/components/Menu';
import FAQ from './pages/FAQ';
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
            <Route exact path='/browse' element={<Browse />} />
            <Route exact path='/rankings' element={<Rank />} />
            <Route exact path='/movies/:id' element={<Movie />} /> 
            <Route exact path="/visualizations/overtime" element={<OverTime />} /> 
            <Route exact path="/visualizations/bycountry" element={<Country />} /> 
            <Route exact path="/faq" element={<FAQ />} />
          </Routes>
          <Menu />
        </Router>
      </div>
    )
  }
}


export default App;
