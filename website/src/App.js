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
import StateOfQueerCinema from './pages/Overview';
import Menu from './pages/components/Menu';
import FAQ from './pages/FAQ';
import Disclaimers from './pages/Disclaimers';
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
            <Route exact path='/data/overview' element={<StateOfQueerCinema/>} />
            <Route exact path='/browse' element={<Browse />} />
            <Route exact path='/rankings' element={<Rank />} />
            <Route exact path='/movies/:id' element={<Movie />} /> 
            <Route exact path="/data/overtime" element={<OverTime />} /> 
            <Route exact path="/data/country" element={<Country />} /> 
            <Route exact path="/faq" element={<FAQ />} />
            <Route exact path="/disclaimers" element={<Disclaimers />} />
          </Routes>
          {/* <Menu /> */}
        </Router>
      </div>
    )
  }
}


export default App;
