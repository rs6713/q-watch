import React, { Component, useState, useEffect} from 'react';
import Footer from './components/Footer';
import {useSearchParams} from 'react-router-dom';

import Filters from './components/Filters';
import Loader from './components/Loader';
import Options from './components/Options';
import ChartCountry from './Graphs/ChartCountry';
import MainMenu from './components/MainMenu';
import Button from './components/Button';
import Share from './components/Share';
import Alert from './components/Alert';
import {ReactComponent as ShareIcon} from '../static/icons/share.svg'

import {
  getCriteriaFromSearchParams,
  createUpdateSearchParams,
} from './search';
import {labels} from './utils';


import {ReactComponent as Filter} from '../static/icons/filter.svg'


const RANK_OPTIONS = {
  "Count": "COUNT",
  "Box Office ($)": "BOX_OFFICE_USD",
  "Budget ($)": "BUDGET_USD",
}

function deepEqual(x, y) {
  return (x && y && typeof x === 'object' && typeof y === 'object') ?
    (Object.keys(x).length === Object.keys(y).length) &&
      (Object.keys(x).reduce(function(isEqual, key) {
        return isEqual && deepEqual(x[key], y[key]);
      }, true) || Object.keys(x).length == 0) : (x === y);
}


function Country(){

  const [searchParams, setSearchParams] = useSearchParams();
  const updateSearchParams = createUpdateSearchParams(setSearchParams, searchParams);
  const [criteria, setCriteria] = useState({})
  //getCriteriaFromSearchParams(searchParams, ['rank']);
  const [shareActive, setShareActive] = useState(false);
  
  const [filterActive, setFilterActive] = useState(false);

  const [movies, setMovies] = useState(undefined);
  const [nMatches, setNMatches] = useState(undefined);


  function get_movies(){
    fetch('/api/movies', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        //'cache-control': 'no-store',
      },
      body: JSON.stringify({
        "criteria": criteria,
        "properties": ['TITLE', 'YEAR', 'COUNTRY', 'BOX_OFFICE_USD', 'BUDGET_USD']
      })//this.state.filterCriteria
    }).then(res => res.json()).then(data => {
      setMovies(data["data"]);
      setNMatches(data["n_matches"]);
    }).catch(err => {
      setMovies(null);
      setNMatches(null);
    })
  }

  useEffect(() => {
    let newCriteria = getCriteriaFromSearchParams(searchParams, ['rank']);

    if(!deepEqual(criteria, newCriteria) || movies === undefined){
      setCriteria(newCriteria);
    }
    // setCriteria(newCriteria);
    // setNMatches(null);
    // setMovies(null);
    // get_movies()
  }, [searchParams])

  useEffect(() => {
    setNMatches(undefined);
    setMovies(undefined);
    get_movies()
  }, [criteria])

  return (
    <div id="Country" className="page GraphPage">
      {filterActive && <div className="cover" onClick={()=>{setFilterActive(false)}} />}
      <MainMenu/>
      <Filters active={filterActive} nMatches={nMatches} updateFilters={updateSearchParams} filters={criteria} setActive={setFilterActive} />
      

      <div id="ControlPanel">
        <Options updateOption={(r) => {updateSearchParams({'rank': r})}} option={searchParams.get('rank') || 'COUNT'} name='Ranking' options={RANK_OPTIONS} multi={false}/>
        <div className='filler' />
        <div id="FiltersToggle" onClick={()=>{setFilterActive(!filterActive)}} className={filterActive? 'active': ''} ><Filter/>Filters</div>
        <Button symbol={<ShareIcon/>} onClick={()=>{setShareActive(!shareActive)}}/>
      </div>
      {shareActive && <Share
        labels={labels}
        criteria={criteria}
        nMatches={nMatches}
        setShareActive={setShareActive}
      />}
    
      <div className='Graph'>
        <Loader isLoading={movies === undefined} />
        {movies &&
          <ChartCountry dataset={movies} value_var={searchParams.get('rank') || 'COUNT'} />
        }
        {
          movies === null && <Alert 
            header='Whoops'
            subtitle='Apologies we have an error on our side preventing us from serving you this data.'
          />
        }
      </div>
      <Footer />
    </div>
  )
}

export default Country