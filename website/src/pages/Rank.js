import React, { Component, useState, useEffect} from 'react';
import Footer from './components/Footer';

import Filters from './components/Filters';
import Loader from './components/Loader';
import Options from './components/Options';
import Switch from './components/Switch';
import BarHierarchy from './Graphs/BarHierarchy';

import {ReactComponent as Filter} from '../static/icons/filter.svg'

import DEFAULT_MOVIES from './default_rank.json';

const RANK_OPTIONS = {
  "Popularity": "NUM_RATING",
  "Rating": "AVG_RATING",
  "Box Office": "BOX_OFFICE",
  "Budget": "BUDGET",
}

const GROUP_OPTIONS = {
  "LGBTQ+ Identity": "TYPES",
  "Genre": "GENRES",
  "Representations": "REPRESENTATIONS",
}


function Rank(){

  const [filterActive, setFilterActive] = useState(false);
  const [ascending, setAscending] = useState(false);
  const [ignoreZeros, setIgnoreZeros] = useState(true);
  const [rank, setRank] = useState("BOX_OFFICE");
  const [movies, setMovies] = useState(DEFAULT_MOVIES);
  const [nMatches, setNMatches] = useState(null);
  const [criteria, setCriteria] = useState({});
  const [group, setGroup] = useState([])

  function get_movies(){
    fetch('/api/movies', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'cache-control': 'no-store',
      },
      body: JSON.stringify({
        "criteria": criteria,
        "sort": [rank, ascending ? 1 : -1],
        "properties": ['TITLE', 'YEAR', 'TYPES', rank, 'GENRES', 'REPRESENTATIONS']
      })//this.state.filterCriteria
    }).then(res => res.json()).then(data => {
      console.log(data["data"])
      setMovies(data["data"]);
      setNMatches(data["n_matches"]);
    })
  }

  useEffect(() => {
    console.log('Setting rank ', rank, ' criteria', criteria)
    // setMovies(null);
    // setNMatches(null);
    // get_movies();
  }, [rank, criteria])

  function updateCriteria(update){

    let newCriteria = criteria === null? {...update} : {...criteria, ...update}

    // Cancelled criteria are removed
    for(let key in newCriteria){
      if(newCriteria[key] === null){
        delete newCriteria[key];
      }
    }
    setCriteria(
      newCriteria
    )
  }

  return (
    <div id="Rankings" className="page GraphPage">
      {filterActive && <div className="cover" onClick={()=>{setFilterActive(false)}} />}

      <Filters active={filterActive} nMatches={nMatches} updateFilters={updateCriteria} filters={criteria} />

      <div id="ControlPanel">
        <Options updateOption={setRank} option={rank} name='Ranking' options={RANK_OPTIONS} />
        <Options updateOption={setGroup} option={group} name='Grouping' options={GROUP_OPTIONS} multi={true}/>
        <Switch state={ascending} setState={setAscending} onMessage={<div>Ascending Order</div>} offMessage={<div>Descending Order</div>} />
        <Switch state={ignoreZeros} setState={setIgnoreZeros} onMessage={<div>Ignore Zeros/Unknown</div>} offMessage={<div>Show All</div>} />
        <div className='filler' />
        <div id="FiltersToggle" onClick={()=>{setFilterActive(!filterActive)}} className={filterActive? 'active': ''} ><Filter/>Filters</div>
      </div>
      
      <div className='Graph'>
        <Loader isLoading={movies === null} />
        {movies !== null && 
        <BarHierarchy dataset={movies.filter(movie => movie.sort_key !== 0 || !ignoreZeros)} sort_ascending={ascending} grouping_vars={group} name_var={'TITLE'} label_vars={['YEAR']} value_var={rank} />
        }
      </div>
      <Footer />
    </div>
  )
}

export default Rank