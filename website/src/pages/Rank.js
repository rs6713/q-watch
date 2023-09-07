import React, {useState, useEffect} from 'react';
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


const RANK_OPTIONS = {
  "Count": "COUNT",
  "Popularity": "NUM_RATING",
  "Rating": "AVG_RATING",
  "Box Office ($)": "BOX_OFFICE_USD",
  "Budget ($)": "BUDGET_USD",
}

const SUMMARY_OPTIONS = {
  "BOX_OFFICE_USD": {
    "Total": 'sum',
    "Average": 'mean'
  },
  "BUDGET_USD": {
    "Total": 'sum',
    "Average": 'mean'
  },
  "RATING": {
    "Average": 'mean'
  },
  "POPULARITY": {
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
  //let criteria = getCriteriaFromSearchParams(searchParams);

  const [filterActive, setFilterActive] = useState(false);

  //const [rank, setRank] = useState("BOX_OFFICE_USD");
  // const [summary, setSummary] = useState("sum");
  const rank = searchParams.get('rank') || 'BOX_OFFICE_USD';
  const summary = searchParams.get('summary') || 'sum';
  const [movies, setMovies] = useState(null);
  const [nMatches, setNMatches] = useState(null);
  //const [group, setGroup] = useState(["TYPES"])
  const group = getCriteriaFromSearchParams(searchParams, [], ['group'])['group'] || ['TYPES'];
  // const [ascending, setAscending] = useState(false);
  // const [ignoreZeros, setIgnoreZeros] = useState(true);
  const ascending = searchParams.get('ascending') || false;
  const ignoreZeros = searchParams.get('ignoreZeros') || true;
  
  const [labels, setLabels] = useState(null);
  const [shareActive, setShareActive] = useState(false);

  useEffect(() => {
    fetch('/api/movie/labels').then(res => res.json()).then(data => {
      setLabels(data);
    });
  }, []);

  function get_movies(){
    let properties =  ['TITLE', 'YEAR', 'TYPES', ...Object.values(RANK_OPTIONS), 'GENRES', 'REPRESENTATIONS'];
    properties.splice(properties.indexOf('COUNT'), 1) 
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
        "properties": properties
      })//this.state.filterCriteria
    }).then(res => res.json()).then(data => {
      setMovies(data["data"]);
      setNMatches(data["n_matches"]);
    })
  }

  useEffect(() => {
    let newCriteria = getCriteriaFromSearchParams(
      searchParams,
      ['rank', 'summary', 'group', 'ascending', 'ignoreZero']
    );

    if(!deepEqual(criteria, newCriteria) || movies === null){
      setCriteria(newCriteria);
    }
    // setCriteria(newCriteria);
    // setNMatches(null);
    // setMovies(null);
    // console.log('Triggered effect: ',  criteria)
    // get_movies()
  }, [searchParams])

  useEffect(() => {
    //criteria = getCriteriaFromSearchParams(searchParams);
    setNMatches(null);
    setMovies(null);
    console.log('Triggered effect: ',  criteria)
    get_movies()
  }, [criteria])

  console.log(rank, summary, ascending, group)

  return (
    <div id="Rankings" className="page GraphPage">
      <MainMenu />
      {filterActive && <div className="cover" onClick={()=>{setFilterActive(false)}} />}
      
      <Filters active={filterActive} nMatches={nMatches} updateFilters={updateSearchParams} filters={criteria} setActive={setFilterActive} />

      <div id="ControlPanel">
        <Options updateOption={(r) => {updateSearchParams({'rank': r})}} option={rank} name='Ranking' options={RANK_OPTIONS} />
        <Options updateOption={(g) => {updateSearchParams({'group': g})}} option={group} name='Grouping' options={GROUP_OPTIONS} multi={true}/>
        <Options updateOption={(s) => {updateSearchParams({'summary': s})}} option={summary} name='Summary' options={SUMMARY_OPTIONS[rank]}/>
        <Switch state={ascending} setState={(a) => {updateSearchParams({'ascending': a})}} onMessage={<div>Ascending Order</div>} offMessage={<div>Descending Order</div>} />
        <Switch state={ignoreZeros} setState={(r) => {updateSearchParams({'ignoreZeros': r})}} onMessage={<div>Ignore Zeros/Unknown</div>} offMessage={<div>Show All</div>} />
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
        <BarHierarchy dataset={movies.filter(movie => movie[rank] !== 0 || !ignoreZeros)} sort_ascending={ascending} grouping_vars={group} name_var={'TITLE'} label_vars={['YEAR']} value_var={rank} summary_var={summary} />
        }
      </div>
      <Footer />
    </div>
  )
}

export default Rank