import React, { Component, useState, useEffect} from 'react';
import Footer from './components/Footer';

import Filters from './components/Filters';
import Labels from './components/Labels';
import MovieList from './components/MovieList';
import Options from './components/Options';
import Indexer from './components/Indexer';

import {ReactComponent as Filter} from '../static/icons/filter.svg'

import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  NavLink,
  useNavigate,
  createSearchParams,
  useSearchParams
} from 'react-router-dom';

const SORT = {
  "Most Popular": ["NUM_RATING", -1],
  "Least Popular": ["NUM_RATING", 1],
  "Highest Rating": ["AVG_RATING", -1],
  "Lowest Rating": ["AVG_RATING", 1],
  "Most Recent Release": ["YEAR", -1],
  "Least Recent Release": ["YEAR", 1],
}

function Browse(){

  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [filterActive, setFilterActive] = useState(false);
  const [movies, setMovies] = useState(null);
  const sort = searchParams.get('sort') || 'Most Recent Release';
  const index = parseInt(searchParams.get('index') || 1);
  const [criteria, setCriteria] = useState({

  });
  const [nIndexes, setNIndexes] = useState(null);
  const [nMatches, setNMatches] = useState(null);
  const [labelsLoaded, setLabelsLoaded] = useState(false);

  function createParams(options){
    let params = {
      'index': index,
      'sort': sort,
      ...options
    }
    return `?${createSearchParams(params)}`
  }

  function updateIndex(index){
    navigate({pathname: '/browse', search: createParams({'index':index}) })
  }

  function updateSort(sort){
    navigate({pathname: '/browse', search: createParams({'sort':sort}) })
  }

  
  // console.log(searchParams);

  
  //   navigate({
  //     pathname: '/browse',
  //     search: `?${createSearchParams(criteria)}`,
  //   });


  function get_movies(){
    if(criteria !== null){
      fetch('/api/movies', {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'cache-control': 'no-store',
        },
        body: JSON.stringify({
          "criteria": criteria,
          "sort": SORT[sort],
          "index": index
        })//this.state.filterCriteria
      }).then(res => res.json()).then(data => {
        setMovies(data["data"]);
        setNIndexes(data["n_indexes"]);
        setNMatches(data["n_matches"]);
      })
    }
  }

  // useEffect(() => {
  //   if(movies != null){
  //     setMovies(null);
  //     if(index != 1){
  //       setIndex(1);
  //     }else{
  //       get_movies();
  //     }
  //   }
  // }, [sort])

  useEffect(() => {
    setMovies(null);
    setNIndexes(null);
    setNMatches(null);
    
    get_movies();
    
  }, [criteria])

  // Data Fetching Called at criteria updates
  // useEffect(() => {
  //   if(movies != null){
  //     setMovies(null);
  //     // Loading is true while movies are null
  //     get_movies();
  //   }
  // }, [index]);



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
    <div id="Browse" className="page">
      {filterActive && <div className="cover" onClick={()=>{setFilterActive(false)}} />}

      <Filters active={filterActive} nMatches={nMatches} updateFilters={updateCriteria} filters={criteria} />

      <div id="ControlPanel">
        <Options name='Sort' updateOption={updateSort} option={sort} options={ Object.keys(SORT)} />
        <Labels labelType="GENRES" updateLabel={updateCriteria} setLoaded={setLabelsLoaded}/>
        
        <div id="FiltersToggle" onClick={()=>{setFilterActive(!filterActive)}} className={filterActive? 'active': ''} ><Filter/>Filters</div>
      </div>
      <div id="MovieList">
        <MovieList movies={movies} />
        <Indexer nIndexes={nIndexes} updateIndex={updateIndex} index={index} />
      </div>
      <Footer />
    </div>
  )
}
export default Browse
