import React, { Component, useState, useEffect} from 'react';
import Footer from './components/Footer';

import Filters from './components/Filters';
import Labels from './components/Labels';
import MovieList from './components/MovieList';
import Options from './components/Options';
import Indexer from './components/Indexer';
import MainMenu from './components/MainMenu'

import {ReactComponent as Filter} from '../static/icons/filter.svg'
import {ReactComponent as Share} from '../static/icons/share.svg'
import {ReactComponent as Copy} from '../static/icons/copy.svg'
import {ReactComponent as Minus} from '../static/icons/minus.svg'
import Button from './components/Button'
import {

  useSearchParams
} from 'react-router-dom';
import {
  generateCriteriaDescription,
  getCriteriaFromSearchParams,
  createUpdateSearchParams,
} from './search';


const SORT = {
  "Most Popular": ["NUM_RATING", -1],
  "Least Popular": ["NUM_RATING", 1],
  "Highest Rating": ["AVG_RATING", -1],
  "Lowest Rating": ["AVG_RATING", 1],
  "Most Recent Release": ["YEAR", -1],
  "Least Recent Release": ["YEAR", 1],
  'A-Z': ['TITLE', 1]
}

const DEFAULT_PARAMS = {
  'SORT': 'Most Recent Release',
  'INDEX': 1
}


function Browse(){

  const [searchParams, setSearchParams] = useSearchParams();
  const updateSearchParams = createUpdateSearchParams(setSearchParams, searchParams);

  let criteria = getCriteriaFromSearchParams(searchParams);

  let sort = searchParams.get('sort') || DEFAULT_PARAMS['SORT'];
  let index = parseInt(searchParams.get('index') || DEFAULT_PARAMS['INDEX']);

  const [labels, setLabels] = useState(null);
  const [movies, setMovies] = useState(null);
  const [nIndexes, setNIndexes] = useState(null);
  const [nMatches, setNMatches] = useState(null);

  const [filterActive, setFilterActive] = useState(false);
  const [shareActive, setShareActive] = useState(false);
  const [linkCopied, setLinkCopied] = useState(false);

  useEffect(() => {
    fetch('/api/movie/labels').then(res => res.json()).then(data => {
      setLabels(data);
    });
  }, []);


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
          "index": index,
          'properties': [
            "TITLE",
            "YEAR",
            "BIO",
            "FILENAME", "CAPTION",
            "AVG_RATING", "NUM_RATING",
            "GENRES", "TYPES",
           'RUNTIME', 'AGE', 'COUNTRY', 'LANGUAGE',
            'REPRESENTATIONS'
          ]
        })//this.state.filterCriteria
      }).then(res => res.json()).then(data => {
        setMovies(data["data"]);
        setNIndexes(data["n_indexes"]);
        setNMatches(data["n_matches"]);
      })
    }
  }
  useEffect(() => {
    if(linkCopied){
      setTimeout(() => {setLinkCopied(false)}, 3000)
    }
  }, [linkCopied])

  useEffect(() => {
    // sort = searchParams.get('sort') || DEFAULT_PARAMS['SORT'];
    // index = parseInt(searchParams.get('index') || DEFAULT_PARAMS['INDEX']);
    // criteria = getCriteriaFromSearchParams(searchParams);
    setNMatches(null);
    setMovies(null);
    console.log('Triggered effect: ', sort, index, criteria)
    get_movies()
  }, [searchParams])

  return (
    <div id="Browse" className="page">
      {(filterActive) && <div className="cover" onClick={()=>{setFilterActive(false); setShareActive(false)}} />}
      <MainMenu/>

      <Filters active={filterActive} nMatches={nMatches} updateFilters={updateSearchParams} filters={criteria} setActive={setFilterActive}/>

      <div id="ControlPanel">
        <Options name='Sort' updateOption={(s)=>{updateSearchParams({'sort': s, 'index': 1})}} option={sort} options={ Object.keys(SORT)} />
        <Labels labelType={'GENRES'} labels={labels && labels['GENRES']} updateLabel={updateSearchParams} label={criteria["GENRES"]}/>
        
        
        <div id="FiltersToggle" onClick={()=>{setFilterActive(!filterActive)}} className={filterActive? 'active': ''} ><Filter/>Filters</div>
        <Button symbol={<Share/>} onClick={()=>{setShareActive(!shareActive)}}/>
        
      </div>
      <div id="MovieList">
        <MovieList movies={movies} />
        {movies !== null && movies.length !== 0 && <div className='spacer'> </div>}
        <Indexer nIndexes={nIndexes} updateIndex={(i)=>{updateSearchParams({'index': i})}} index={index} />
        <Footer />
      </div>
      
      {shareActive &&
        <div className='announcement_container'>
        <div className='announcement'>
          <h2>
            Share Search - {nMatches} 
            <Minus onClick={()=>{setShareActive(false)}}/>
          </h2>
          <table className='description'>
            {/* <h3>{nMatches} Movies</h3> */}
              {generateCriteriaDescription(labels, criteria).map(item => {
                return <tr>
                  <td>{item.TITLE}</td>
                  <td>{item.DESCRIP}</td>
                </tr>
              })}
              {Object.keys(criteria).length == 0 && <div>
                <div>No Criteria</div><br/>
                <span><b>Woww...</b> So you just like a little bit of everything, right?? &#128539;</span>
              </div>}
          </table>
          <div className='callToAction' onClick={()=>{navigator.clipboard.writeText(window.location.href); setLinkCopied(true);}}>
            <Copy/>
            <span>{linkCopied? 'Link Copied!' : 'Copy Link to Search'}</span>
          </div><br/>
          {!nMatches && <div>
              Look, we can't stop you from sharing a link to an empty list, but it's a cruel thing to do. &#128514;
          </div>}
        </div>
        </div>
      }
    </div>
  )
}
export default Browse
