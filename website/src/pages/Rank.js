/* Page to Rank by Count, Box Office, Budget different groupings of LGBT Movies */

import React, {useState, useEffect, useMemo} from 'react';
import {useSearchParams} from 'react-router-dom';

import Footer from './components/Footer';
import Filters from './components/Filters';
import Loader from './components/Loader';
import Options from './components/Options';
import Switch from './components/Switch';
import MainMenu from './components/MainMenu';
import Button from './components/Button';
import Share from './components/Share';

import BarHierarchy from './Graphs/BarHierarchy';
import {
  getCriteriaFromSearchParams,
  createUpdateSearchParams,
} from './search';
import {deepEqual} from '../utils';

import {ReactComponent as ShareIcon} from '../static/icons/share.svg'
import {ReactComponent as Filter} from '../static/icons/filter.svg'

// How to Rank Movie Groups
const RANK_OPTIONS = {
  "Count": "COUNT",
  "Popularity": "NUM_RATING",
  "Rating": "AVG_RATING",
  "Box Office ($)": "BOX_OFFICE_USD",
  "Budget ($)": "BUDGET_USD",
}

// Metrics to use to summarize grouops
const SUMMARY_OPTIONS = {
  "BOX_OFFICE_USD": {
    "Total": 'sum',
    "Average": 'mean'
  },
  "BUDGET_USD": {
    "Total": 'sum',
    "Average": 'mean'
  },
  "AVG_RATING": {
    "Average": 'mean'
  },
  "NUM_RATING": {
    "Average": 'mean'
  },
  "COUNT": {
    "Total": "sum"
  }
}

const GROUP_OPTIONS = {
  "LGBTQ+ Identity": "TYPES",
  "Genre": "GENRES",
  "Representations": "REPRESENTATIONS",
}


function Rank(){

  const [searchParams, setSearchParams] = useSearchParams();
  const updateSearchParams = createUpdateSearchParams(setSearchParams, searchParams);
  const [criteria, setCriteria] = useState({});
  const [filterActive, setFilterActive] = useState(false);

  const rank = useMemo(() => searchParams.get('rank') || 'BOX_OFFICE_USD', [searchParams]);
  const summary = useMemo(() => searchParams.get('summary') && Object.values(SUMMARY_OPTIONS[(searchParams.get('rank')|| 'BOX_OFFICE_USD')]).indexOf(searchParams.get('summary')) !== -1 ?  searchParams.get('summary') : Object.values(SUMMARY_OPTIONS[searchParams.get('rank') || 'BOX_OFFICE_USD'])[0], [searchParams]);

  // Movie Results
  const [movies, setMovies] = useState(null);
  const [nMatches, setNMatches] = useState(null);
  const label_var = useMemo(() => ['YEAR'], []);
  const group =  useMemo(() => getCriteriaFromSearchParams(searchParams, [], ['group'])['group'] || ['TYPES'], [searchParams]);

  const ascending = useMemo(() => getCriteriaFromSearchParams(searchParams, [], ['ascending'])['ascending']|| false, [searchParams]);
  const ignoreZeros = useMemo(() => getCriteriaFromSearchParams(searchParams, [], ['ignoreZeros'])['ignoreZeros'] || false, [searchParams]);

  
  const [labels, setLabels] = useState(null);
  const [shareActive, setShareActive] = useState(false);

  const filteredMovies = movies && movies.filter(movie => (rank === 'COUNT') ||( movie[rank] !== 0) || (!ignoreZeros));
  // useMemo(
  //   () => movies && movies.filter(movie => rank === 'COUNT' || movie[rank] !== 0 || !ignoreZeros),
  //   [ignoreZeros, rank, movies]
  // )

  useEffect(() => {
    fetch('/api/movie/labels').then(res => res.json()).then(data => {
      setLabels(data);
    });
  }, []);



  function get_movies(){
    /* Get movies matching filters, in rank order */

    // Movie Properties we need to fetch
    let properties =  ['TITLE', 'YEAR', 'TYPES', ...Object.values(RANK_OPTIONS), 'GENRES', 'REPRESENTATIONS'];
    properties.splice(properties.indexOf('COUNT'), 1) ;

    fetch('/api/movies', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'cache-control': 'no-store',
      },
      body: JSON.stringify({
        "criteria": criteria,
        "sort": rank != 'COUNT' ? [rank, ascending ? 1 : -1] : [],
        "properties": properties
      })
    }).then(res => res.json()).then(data => {

      setMovies(data["data"]);
      setNMatches(data["n_matches"]);
    })
  }

  /* On search params change, if changes movie search criteria, or no movies loaded yet, fetch movies */
  useEffect(() => {
    let newCriteria = getCriteriaFromSearchParams(
      searchParams,
      ['rank', 'summary', 'group', 'ascending', 'ignoreZeros']
    );

    if(!deepEqual(criteria, newCriteria) || movies === null){
      setCriteria(newCriteria);
    }
  }, [searchParams])

  useEffect(() => {

    setNMatches(null);
    setMovies(null);
    get_movies()
  }, [criteria])

  return (
    <div id="Rankings" className="page GraphPage">
      <MainMenu />
      {filterActive && <div className="cover" onClick={()=>{setFilterActive(false)}} />}
      
      <Filters
        active={filterActive}
        nMatches={nMatches}
        updateFilters={updateSearchParams}
        filters={criteria}
        setActive={setFilterActive} 
      />

      <div id="ControlPanel">
        <Options
          updateOption={(r) => {updateSearchParams({'rank': r})}}
          option={rank}
          name='Ranking'
          options={RANK_OPTIONS}
        />
        <Options 
          updateOption={(g) => {updateSearchParams({'group': g})}}
          option={group}
          name='Grouping'
          options={GROUP_OPTIONS}
          multi={true}
        />
        <Options
          updateOption={(s) => {updateSearchParams({'summary': s})}}
          option={summary}
          name='Summary'
          options={SUMMARY_OPTIONS[rank]}
        />

        <Switch
          state={ascending}
          setState={(a) => {updateSearchParams({'ascending': a})}}
          onMessage={<div>Ascending Order</div>}
          offMessage={<div>Descending Order</div>} 
        />
        <Switch 
          state={ignoreZeros}
          setState={(r) => {updateSearchParams({'ignoreZeros': r})}}
          onMessage={<div>Ignore Zeros/Unknown</div>}
          offMessage={<div>Show All</div>}
        />

        <div className='filler' />
        <div id="FiltersToggle" onClick={()=>{setFilterActive(!filterActive)}} className={filterActive? 'active': ''} ><Filter/>Filters</div>
        <Button symbol={<ShareIcon/>} onClick={()=>{setShareActive(!shareActive)}}/>
        {shareActive && <Share
          labels={labels}
          criteria={criteria}
          nMatches={nMatches}
          setShareActive={setShareActive}
        />}
      </div>
      
      <div className='Graph'>
        <Loader isLoading={movies === null} />
        {movies !== null && 
          <BarHierarchy
            dataset={filteredMovies}
            sort_ascending={ascending}
            grouping_vars={group}
            name_var={'TITLE'}
            label_vars={label_var}
            value_var={rank}
            summary_var={summary}
          />
        }
      </div>
      <Footer />
    </div>
  )
}

export default Rank