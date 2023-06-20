import React, { Component, useState, useEffect} from 'react';
import Footer from './components/Footer';
import {useSearchParams} from 'react-router-dom';

import Filters from './components/Filters';
import Loader from './components/Loader';
import Options from './components/Options';
import ChartCountry from './Graphs/ChartCountry';
import MainMenu from './components/MainMenu';

import {
  getCriteriaFromSearchParams,
  createUpdateSearchParams,
  createUpdateSort,
  createUpdateIndex,
} from './search';


import {ReactComponent as Filter} from '../static/icons/filter.svg'


const RANK_OPTIONS = {
  "Count": "COUNT",
  "Box Office ($)": "BOX_OFFICE_USD",
  "Budget ($)": "BUDGET_USD",
}


function Country(){

  const [searchParams, setSearchParams] = useSearchParams();
  const updateSearchParams = createUpdateSearchParams(setSearchParams, searchParams);
  const updateSort = createUpdateSort(setSearchParams, searchParams);
  const updateIndex = createUpdateIndex(setSearchParams, searchParams);
  let criteria = getCriteriaFromSearchParams(searchParams);

  
  const [filterActive, setFilterActive] = useState(false);
  const [rank, setRank] = useState('COUNT');

  const [movies, setMovies] = useState(null);
  const [nMatches, setNMatches] = useState(null);
  // const [criteria, setCriteria] = useState({});

  // function updateCriteria(update){

  //   let newCriteria = criteria === null? {...update} : {...criteria, ...update}

  //   // Cancelled criteria are removed
  //   for(let key in newCriteria){
  //     if(newCriteria[key] === null){
  //       delete newCriteria[key];
  //     }
  //   }
  //   setCriteria(
  //     newCriteria
  //   )
  // }

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
        "properties": ['TITLE', 'YEAR', 'COUNTRY', 'BOX_OFFICE_USD', 'BUDGET_USD']
      })//this.state.filterCriteria
    }).then(res => res.json()).then(data => {
      console.log(data["data"])
      setMovies(data["data"]);
      setNMatches(data["n_matches"]);
    })
  }

  useEffect(() => {
    criteria = getCriteriaFromSearchParams(searchParams);
    setNMatches(null);
    setMovies(null);
    console.log('Triggered effect: ',  criteria)
    get_movies()
  }, [searchParams])

  // useEffect(() => {
  //   console.log('Setting rank ', rank, ' criteria', criteria)
  //   setMovies(null);
  //   setNMatches(null);
  //   get_movies();
  // }, [criteria])

  return (
    <div id="Country" className="page GraphPage">
      {filterActive && <div className="cover" onClick={()=>{setFilterActive(false)}} />}
      <MainMenu/>
      <Filters active={filterActive} nMatches={nMatches} updateFilters={updateSearchParams} filters={criteria} />

      <div id="ControlPanel">
        <Options updateOption={setRank} option={rank} name='Ranking' options={RANK_OPTIONS} multi={false}/>
        <div className='filler' />
        <div id="FiltersToggle" onClick={()=>{setFilterActive(!filterActive)}} className={filterActive? 'active': ''} ><Filter/>Filters</div>
      </div>
    
      <div className='Graph'>
        <Loader isLoading={movies === null} />
        {movies !== null && 
          <ChartCountry dataset={movies} value_var={rank} />
        }
      </div>
      <Footer />
    </div>
  )
}

export default Country