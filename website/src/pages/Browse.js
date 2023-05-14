import React, { Component, useState, useEffect} from 'react';
import Footer from './components/Footer';

import Filters from './components/Filters';
import Labels from './components/Labels';
import MovieList from './components/MovieList';
import Options from './components/Options';
import Indexer from './components/Indexer';

import {ReactComponent as Filter} from '../static/icons/filter.svg'
import {ReactComponent as Share} from '../static/icons/share.svg'
import {ReactComponent as Copy} from '../static/icons/copy.svg'
import Button from './components/Button'
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

const DEFAULT_PARAMS = {
  'SORT': 'Most Recent Release',
  'INDEX': 1
}
const ARRAY_FILTERS = ['COUNTRY', 'LANGUAGE'];
const DICT_FILTERS = [
  'TYPES',
  'RUNTIME',
  'REPRESENTATIONS',
  'TROPE_TRIGGERS',
  'AGE',
  'INTENSITY',
  'AVG_RATING',
  'TAGS'
]

function getCriteriaFromSearchParams(searchParams){
  let newCriteria = {}
  console.log('getcriteriafromsearchparams')

  for(let [key, val] of searchParams.entries()){
    if(['sort', 'index'].indexOf(key) !== -1){
      continue
    }
    if(val.match(/^[0-9]+$/) != null){
      val = parseInt(val)
    }

    console.log(key, val, ARRAY_FILTERS.indexOf(key))
    if(ARRAY_FILTERS.indexOf(key) !== -1){
      newCriteria[key] = [
        ...(newCriteria[key] || []),
        val
      ]
    }else if(DICT_FILTERS.indexOf(key.split('-')[0]) !== -1){
      let k = key.split('-')[0]
      let v = key.split('-')[1]
      if(['VALUE'].indexOf(v) !== -1){
        if(k in newCriteria){
          newCriteria[k][v] = [...(newCriteria[k][v] || []), val]
        }else{
          newCriteria[k] = {[v]: [val]}
        }
      }else{
        if(k in newCriteria){
          newCriteria[k][v] = val
        }else{
          newCriteria[k] = {[v]: val}
        }
      }
    }else{
      newCriteria[key] = val;
    }
  }
  for(let [k, v] of Object.entries(newCriteria)){
    if(DICT_FILTERS.indexOf(k.split('-')[0]) !== -1){
      if(['INCLUDE', 'EXCLUDE'].indexOf(v['TYPE']) == -1){
        //console.log
        newCriteria[k]['VALUE'] = newCriteria[k]['VALUE'][0]
      }
    }
  }
  console.log('Updated Criteria to: ', newCriteria)
  return newCriteria
}



function Browse(){

  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const [filterActive, setFilterActive] = useState(false);
  const [movies, setMovies] = useState(null);

  //let {sort, index, ...restParams} = Object.fromEntries(searchParams)
  let sort = searchParams.get('sort') || DEFAULT_PARAMS['SORT'];
  let index = parseInt(searchParams.get('index') || DEFAULT_PARAMS['INDEX']);
  let criteria = getCriteriaFromSearchParams(searchParams);
  
  //console.log(sort, index, criteria)

  const [nIndexes, setNIndexes] = useState(null);
  const [nMatches, setNMatches] = useState(null);
  const [labelsLoaded, setLabelsLoaded] = useState(false);
  const [shareActive, setShareActive] = useState(false);
  const [linkCopied, setLinkCopied] = useState(false);

  function updateSearchParams(params){
    let newSearchParams = Object.fromEntries(searchParams.entries())
    console.log('Current Search Params: ', newSearchParams)

    if(Object.keys(params).length && Object.keys(params).indexOf('index') == -1){
      newSearchParams['index'] = 1
    }

    // Should only be one entry
    for(const key of Object.keys(params)){

      if(params[key] == null){
        if (DICT_FILTERS.indexOf(key) !== -1){
          for(let k of Object.keys(newSearchParams)){
            if(k.startsWith(key + '-')){
              delete newSearchParams[k]
            }
          }
        }else{
          delete newSearchParams[key]
        }
        continue
      }
      //
      //if(ARRAY_FILTERS.indexOf(key) !== -1)
  
      if(['number', 'string'].indexOf(typeof params[key]) !== -1){
        newSearchParams[key] = params[key]
      }
      else if(Array.isArray(params[key])){
        newSearchParams[key] = params[key]
      }else if (DICT_FILTERS.indexOf(key) !== -1){
        console.log(key, params[key], params)
        if(params[key]){
          for(const [k, v] of Object.entries(params[key])){
            newSearchParams[key+'-'+k] = v
          }
        }
      }
    }
    console.log('Updating searchParams to: ', newSearchParams)
    setSearchParams(newSearchParams)
  }

  // function createParams(options){
  //   let params = {
  //     'index': index,
  //     'sort': sort,
  //     ...options
  //   }
  //   return `?${createSearchParams(params)}`
  // }

  function updateIndex(index){
    setSearchParams({...Object.fromEntries(searchParams.entries()), index})
    //navigate({pathname: '/browse', search: createParams({'index':index}) })
  }

  function updateSort(sort){
    setSearchParams({...Object.fromEntries(searchParams.entries()), sort, index:1})
    //navigate({pathname: '/browse', search: createParams({'sort':sort}) })
  }

  // useEffect(() => {
  //   //console.log('searchparams update')
  //   //console.log(Object.fromEntries(searchParams.entries()))
  //   //setSort(searchParams.get('sort') || DEFAULT_PARAMS['SORT'])
    
  // }, [searchParams]);

  
  // console.log(searchParams);

  
  //   navigate({
  //     pathname: '/browse',
  //     search: `?${createSearchParams(criteria)}`,
  //   });


  function get_movies(){
    if(criteria !== null){
      console.log(criteria)
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
  useEffect(() => {
    if(linkCopied){
      setTimeout(() => {setLinkCopied(false)}, 3000)
    }
  }, [linkCopied])

  useEffect(() => {
    // if(movies != null){
    //   setMovies(null);
    //   if(index != 1){
    //     setIndex(1);
    //   }else{
    //     get_movies();
    //   }
    // }
    // if(isLoaded === true){
    sort = searchParams.get('sort') || DEFAULT_PARAMS['SORT'];
    index = parseInt(searchParams.get('index') || DEFAULT_PARAMS['INDEX']);
    criteria = getCriteriaFromSearchParams(searchParams);

    setMovies(null);
    console.log('Triggered effect: ', sort, index, criteria)
    get_movies()
  }, [searchParams])

  function generateCriteriaDescription(criteria){
    let descriptions = []
    for(let key of Object.keys(criteria)){
      descriptions.push(
        {'TITLE': key, 'DESCRIP': criteria[key]}
      )
    }
    return descriptions
  }

  // useEffect(() => {
  //   setMovies(null);
  //   setNIndexes(null);
  //   setNMatches(null);
    
  //   get_movies();
    
  // }, [criteria, sort, index])

  // Data Fetching Called at criteria updates
  // useEffect(() => {
  //   if(movies != null){
  //     setMovies(null);
  //     // Loading is true while movies are null
  //     get_movies();
  //   }
  // }, [index]);



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

  return (
    <div id="Browse" className="page">
      {(filterActive || shareActive) && <div className="cover" onClick={()=>{setFilterActive(false); setShareActive(false)}} />}

      <Filters active={filterActive} nMatches={nMatches} updateFilters={updateSearchParams} filters={criteria} />

      <div id="ControlPanel">
        <Options name='Sort' updateOption={updateSort} option={sort} options={ Object.keys(SORT)} />
        <Labels labelType="GENRES" updateLabel={updateSearchParams} setLoaded={setLabelsLoaded} label={criteria["GENRES"]}/>
        
        <div id="FiltersToggle" onClick={()=>{setFilterActive(!filterActive)}} className={filterActive? 'active': ''} ><Filter/>Filters</div>
        <Button symbol={<Share/>} onClick={()=>{setShareActive(!shareActive)}}/>
      </div>
      <div id="MovieList">
        <MovieList movies={movies} />
        {movies !== null && movies.length !== 0 && <div className='spacer'> </div>}
        <Indexer nIndexes={nIndexes} updateIndex={updateIndex} index={index} />
      </div>
      <Footer />
      {shareActive &&
        <div className='announcement'>
          <h2>Share Search - {nMatches} Movies</h2>
          <div className='description'>
            {/* <h3>{nMatches} Movies</h3> */}
              {generateCriteriaDescription(criteria).map(item => {
                return <div>
                  <span>{item.TITLE}</span>
                  <span>{item.DESCRIP}</span>
                </div>
              })}
              {Object.keys(criteria).length == 0 && <div>
                <span>No Criteria</span>
                <span>Wow! So you just like a little bit of everything, right??</span>
              </div>}
          </div>
          <div className='callToAction' onClick={()=>{navigator.clipboard.writeText(window.location.href); setLinkCopied(true);}}>
            <Copy/>
            <span>{linkCopied? 'Link Copied!' : 'Copy Link to Search'}</span>
          </div>
        </div>
      }
    </div>
  )
}
export default Browse
