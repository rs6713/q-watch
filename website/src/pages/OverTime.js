import React, { Component, useState, useEffect} from 'react';
import Footer from './components/Footer';

import Filters from './components/Filters';
import Loader from './components/Loader';
import Options from './components/Options';
import Switch from './components/Switch';
import BarRace from './Graphs/BarRace';

import DEFAULT_MOVIES from './default_rank.json';


import {ReactComponent as Filter} from '../static/icons/filter.svg'


const RANK_OPTIONS = {
  "Count": "COUNT",
  "Box Office": "BOX_OFFICE",
  "Budget": "BUDGET",
}


const GROUP_OPTIONS = {
  "LGBTQ+ Identity": "TYPES",
  "Genre": "GENRES",
  "Representations": "REPRESENTATIONS",
}

function OverTime(){

  const [filterActive, setFilterActive] = useState(false);
  const [rank, setRank] = useState("BOX_OFFICE");
  const [movies, setMovies] = useState(DEFAULT_MOVIES);
  const [nMatches, setNMatches] = useState(null);
  const [criteria, setCriteria] = useState({});
  const [group, setGroup] = useState(["GENRES"])

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
        "properties": ['TITLE', 'YEAR', 'TYPES', 'COUNTRY', 'BOX_OFFICE', 'BUDGET', 'GENRES', 'REPRESENTATIONS']
      })//this.state.filterCriteria
    }).then(res => res.json()).then(data => {
      console.log(data["data"])
      setMovies(data["data"]);
      setNMatches(data["n_matches"]);
    })
  }

  useEffect(() => {
    // console.log('Setting rank ', rank, ' criteria', criteria)
    // setMovies(null);
    // setNMatches(null);
    // get_movies();
  }, [criteria])

  return (
    <div id="OverTime" className="page GraphPage">
      {filterActive && <div className="cover" onClick={()=>{setFilterActive(false)}} />}

      <Filters active={filterActive} nMatches={nMatches} updateFilters={updateCriteria} filters={criteria} />

      <div id="ControlPanel">
        <Options updateOption={setRank} option={rank} name='Ranking' options={RANK_OPTIONS} />
        <Options updateOption={setGroup} option={group} name='Grouping' options={GROUP_OPTIONS} multi={true}/>
        <div className='filler' />
        <div id="FiltersToggle" onClick={()=>{setFilterActive(!filterActive)}} className={filterActive? 'active': ''} ><Filter/>Filters</div>
      </div>
    
      <div className='Graph'>
        <Loader isLoading={movies === null} />
        {movies !== null && 
        <BarRace data={movies} grouping_vars={group} name_var={'TITLE'} label_vars={['YEAR']} value_var={rank} />
        }
      </div>
      <Footer />
    </div>
  )
}

export default OverTime