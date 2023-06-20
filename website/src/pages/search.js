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


  function generateCriteriaDescription(labels, criteria){
    let descriptions = []
    console.log('Generating criteria desription: ', criteria)
    for(let key of Object.keys(criteria)){
      let ids = criteria[key];
      console.log('ids: ', ids, 'key: ', key)
      let vals, rule, typ;

      if(['number', 'string'].indexOf(typeof ids) !== -1){
        console.log('Key ', key, ' is num/str ', ids)
        ids = [ids]
      }else {
        if (DICT_FILTERS.indexOf(key) !== -1){
          typ = criteria[key].TYPE.slice(0, 1).toUpperCase() + criteria[key].TYPE.slice(1).toLowerCase()
          rule = criteria[key].RULE? criteria[key].RULE.toLowerCase(): ' or '
          ids = criteria[key].VALUE
        }
      }
      if(Object.keys(labels).indexOf(key) !== -1 || Object.keys(labels).indexOf(key + 'S') !== -1){
        console.log(key, Object.keys(labels))
        let k;
        if(Object.keys(labels).indexOf(key) !== -1){
          k = key;
        }else{
          k = key + 'S';
        }
        vals = labels[k].filter(
          o => ids.indexOf(o.ID) !== -1).map(
            o => o.LABEL
          )
      }else{
        vals = ids
      }

      // The keys are first-letter capitalized, joined with '/'
      let keyNice = key.split('_').map(s => s.toLowerCase()).map(
        k => k.slice(0, 1).toUpperCase() + k.slice(1)
      )
      keyNice = keyNice.join('/')

      if (DICT_FILTERS.indexOf(key) !== -1){
        keyNice = keyNice + ` (${typ})`
        vals = vals.join(` ${rule} `)
      }else{
        vals = vals.join('&#8226;');
      }

      descriptions.push(
        {'TITLE': keyNice, 'DESCRIP': vals}
      )
    }
    return descriptions
  }

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

  function createUpdateSearchParams(setSearchParams, searchParams){
    return function(params){
    let newSearchParams = Object.fromEntries(searchParams.entries())

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
    setSearchParams(newSearchParams)
  }}

  function createUpdateIndex(setSearchParams, searchParams){
    return function updateIndex(index){
      setSearchParams({...Object.fromEntries(searchParams.entries()), index})
      //navigate({pathname: '/browse', search: createParams({'index':index}) })
    }
  }

  function createUpdateSort(setSearchParams, searchParams){
    return function updateSort(sort){
      setSearchParams({...Object.fromEntries(searchParams.entries()), sort, index:1})
      //navigate({pathname: '/browse', search: createParams({'sort':sort}) })
    }
  }

export {
  DICT_FILTERS,
  generateCriteriaDescription,
  getCriteriaFromSearchParams,
  createUpdateSearchParams,
  createUpdateIndex,
  createUpdateSort
}