import React from 'react';
import { useEffect, useState } from 'react';
import Footer from './components/Footer'
import PieChart from './Graphs/PieChart'
import {PercentDelta, PercentAlert, thresholdStatement} from './components/Delta';


function StateOfQueerCinema(){
  const [movies, setMovies] = useState(null);
  const [movieTotal, setMovieTotal] = useState(null);
  const [movieCounts, setMovieCounts] = useState(null);
  const [transMovieCounts, setTransMovieCounts] = useState(null);

  useEffect(() => {
    fetch('/api/movies/count', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'cache-control': 'no-store',
      },
      body: JSON.stringify({
        "criteria": {
          'TYPES': 4
        },
        "groups": {
          'LGBTQIA+ Categories': ['TYPES'],
          'Genres': ['GENRES'],
          'Tropes / Triggers': ["TROPE_TRIGGERS"],
          'Representations': ['REPRESENTATIONS'],
          'Age': ['AGE'],
          'Intensity': ['INTENSITY'],
          'Country': ['COUNTRY'],
          'Year_Type': ['TYPES', 'YEAR'],
          'Tags': ['TAGS']
        }
      })//this.state.filterCriteria
    }).then(res => res.json()).then(data => {
      console.log(data)
      setTransMovieCounts(data)
    })
  }, []);

  useEffect(() => {
    fetch('/api/movies/count', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'cache-control': 'no-store',
      },
      body: JSON.stringify({
        "groups": {
          'LGBTQIA+ Categories': ['TYPES'],
          'Genres': ['GENRES'],
          'Tropes / Triggers': ["TROPE_TRIGGERS"],
          'Representations': ['REPRESENTATIONS'],
          'Age': ['AGE'],
          'Intensity': ['INTENSITY'],
          'Country': ['COUNTRY'],
          'Year_Type': ['TYPES', 'YEAR'],
          'Tags': ['TAGS']
        }
      })//this.state.filterCriteria
    }).then(res => res.json()).then(data => {
      console.log(data)
      setMovieCounts(data)
    })
  }, []);

  useEffect(() => {
  fetch('/api/movies', {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'cache-control': 'no-store',
    },
    body: JSON.stringify({
      "properties": [
        'TITLE', 'YEAR', 'COUNTRY', 'BOX_OFFICE_USD', 'BUDGET_USD',
        'TYPES', 'GENRES', 'REPRESENTATIONS'
      ]
    })//this.state.filterCriteria
  }).then(res => res.json()).then(data => {
    console.log(data["data"])
    setMovies(data["data"]);
    setMovieTotal(data["n_matches"]);
  })
}, [])

  return (
    <div id='StateOfQueerCinema' className='page'>
      <div id='Race' className='block'>
        
        <PercentAlert dataset={movieCounts} dataChoice='Representations' value='QTIPOC' statement={thresholdStatement(50)}/>
        <PercentAlert dataset={movieCounts} dataChoice='Representations' value='Plus-Sized' statement={thresholdStatement(50)}/>
        <PercentAlert dataset={movieCounts} dataChoice='Representations' value='POC Love' statement={thresholdStatement(50)}/>
      </div>
      <div>
        <PercentAlert dataset={movieCounts}
        dataChoice='Country' value='United States' qualifier='Over' valueStatement='are based in the United States' />

        <PercentAlert dataset={movieCounts}
        dataChoice='Country' value={['United States', 'United Kingdom', 'Canada', 'France']} />

        <PercentAlert dataset={movieCounts}
        dataChoice='Age' value='Senior' />
        <PercentAlert dataset={movieCounts}
        dataChoice='Age' value='Childhood' />

        <PercentAlert dataset={movieCounts}
        dataChoice='Genres' value='Sci-Fi/Fantasy' />

<PercentAlert dataset={movieCounts}
        dataChoice='Tropes / Triggers' value='Suicide/SH' />
        <PercentAlert dataset={movieCounts}
        dataChoice='Tropes / Triggers' value='Homophobia' />
        <PercentAlert dataset={movieCounts}
        dataChoice='Tropes / Triggers' value='Death' />
        <PercentAlert dataset={movieCounts}
        dataChoice='Tropes / Triggers' value='Cheating' />
        <PercentAlert dataset={movieCounts}
        dataChoice='Tags' value='Sexual Awakening' />
        <PercentAlert dataset={movieCounts}
        dataChoice='Tags' value='Age Gap Relationship' />

<PercentAlert dataset={transMovieCounts}
        dataChoice='Tropes / Triggers' value='Gore/Murder' />
        <PercentAlert dataset={transMovieCounts}
        dataChoice='Tropes / Triggers' value='Cis Playing Trans' />
        <PercentAlert dataset={transMovieCounts}
        dataChoice='Tropes / Triggers' value='Transphobia' />
        <PercentAlert dataset={transMovieCounts}
        dataChoice='Country' value='United States' qualifier='Over' valueStatement='are based in the United States' />
        <PercentAlert dataset={transMovieCounts} dataChoice='Representations' value='Plus-Sized' />
        <PercentAlert dataset={transMovieCounts} dataChoice='Representations' value='POC Love' />

<PieChart dataset={transMovieCounts} dataChoice={'Tropes / Triggers'}/>
      </div>
    </div>

  )

}

export default StateOfQueerCinema