/*
Utilities to handle processing of search parameters for movie filters, rank logic
Translates movie criterion to/from search parameters.
*/
// Filters that have array matches e.g. multiple languages can be selected
const ARRAY_FILTERS = ['COUNTRY', 'LANGUAGE', 'group'];
// Filters with dictionary criterion e.g. runtime, less_then, greater_than
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

  for(let key of Object.keys(criteria)){
    let ids = criteria[key];
    let vals, rule, typ;

    if(['number', 'string'].indexOf(typeof ids) !== -1){
      ids = [ids]
    }else {
      if (DICT_FILTERS.indexOf(key) !== -1){
        typ = criteria[key].TYPE.slice(0, 1).toUpperCase() + criteria[key].TYPE.slice(1).toLowerCase()
        rule = criteria[key].RULE? criteria[key].RULE.toLowerCase(): ' or '
        ids = criteria[key].VALUE
      }
    }
    if(Object.keys(labels).indexOf(key) !== -1 || Object.keys(labels).indexOf(key + 'S') !== -1){
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

      let requirement = criteria[key].REQUIREMENT
      if(requirement !== undefined){
        vals += ` (${requirement.slice(0, 1) + requirement.toLowerCase().slice(1)})`
      }
    }else{
      vals = vals.join('&#8226;');
    }

    descriptions.push(
      {'TITLE': keyNice, 'DESCRIP': vals}
    )
  }
  return descriptions
}

function getCriteriaFromSearchParams(searchParams, ignoreCols, onlyCols){
  /*
    Convert search parameters to a valid movie-criterion dictionary, used for /movies api.
    Params
    ------
    ignoreCols - parameter keys to ignore, not keep in newCriteria
    onlyCols - if specified, only these parameter keys are kept in the newCriteria
  */
  console.log('Getting criteria from search params')
  let newCriteria = {}
  ignoreCols = ignoreCols || [];

  for(let [key, val] of searchParams.entries()){
    // If we specified onlyCols, and this key is not one of them, skip
    if(onlyCols !== undefined && onlyCols.indexOf(key) == -1){
      continue
    }
    // Excluded columns, we don't process
    if(['sort', 'index', ...ignoreCols].indexOf(key) !== -1){
      continue
    }
    // Convert numerical strs to integer
    if(val.match(/^[0-9]+$/) != null){
      val = parseInt(val)
    }
    // Convert boolean strs to boolean
    if(['true', 'false'].indexOf(val) !== -1){
      val = (val == 'true')
    }

    // Processed 'val' for a valid column is either taken as a constant,
    // appended to an array (if col in ARRAY_FILTERS)
    // assigned to a dict (if col in DICT_FILTERS)

    // Value needs to be appended to an array, if it is an array filter
    if(ARRAY_FILTERS.indexOf(key) !== -1){
      newCriteria[key] = [
        ...(newCriteria[key] || []),
        val
      ]
    // Key, Value, needs to be de-composed to subkey, value, and used to create/append to a dict
    }else if(DICT_FILTERS.indexOf(key.split('-')[0]) !== -1){
      // Key is of form [col_name]-[dict_key_name]
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
    // Else assign value
    }else{
      newCriteria[key] = val;
    }
  }
  for(let [k, v] of Object.entries(newCriteria)){
    if(DICT_FILTERS.indexOf(k.split('-')[0]) !== -1){
      if(['INCLUDE', 'EXCLUDE'].indexOf(v['TYPE']) == -1){
        newCriteria[k]['VALUE'] = newCriteria[k]['VALUE'][0]
      }
      // There are no values to include/exclude
      if(Object.keys(newCriteria[k]).indexOf('VALUE') == -1){
        newCriteria[k]['VALUE'] = [];
      }
    }
  }
  return newCriteria
}

function createUpdateSearchParams(setSearchParams, searchParams){
  /* Return function that can be called to update searchParams, to passed in params
     using setSearchParams
  */
  return function updateSearchParams(params){
    console.log('New Filters: ', params)

    let newSearchParams = {};
    for(let [key, val] of searchParams.entries()){

      if(ARRAY_FILTERS.indexOf(key) !== -1 || (
        DICT_FILTERS.indexOf(key.split('-')[0]) !== -1 && key.split('-')[1] == 'VALUE'
      )){
        newSearchParams[key] = [
          ...(newSearchParams[key] || []),
          val
        ]
      }else{
        newSearchParams[key] = val
      }
    }

    if(Object.keys(params).length && Object.keys(params).indexOf('index') == -1 && Object.keys(newSearchParams).indexOf('index') != -1){
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

      if(['number', 'string', "boolean"].indexOf(typeof params[key]) !== -1){
        newSearchParams[key] = params[key]
      }
      else if(Array.isArray(params[key])){
        newSearchParams[key] = params[key]
      }else if (DICT_FILTERS.indexOf(key) !== -1){
        if(params[key]){
          for(const [k, v] of Object.entries(params[key])){
            if(v!== null){
              newSearchParams[key+'-'+k] = v
            }else{
              if(Object.keys(newSearchParams).indexOf(key + '-' + k) !== -1){
                delete newSearchParams[key+'-'+k]
              }
            }
          }
        }
      }
    }
    console.log('New Search Params: ', newSearchParams)
    setSearchParams(newSearchParams)
  }
}

export {
  DICT_FILTERS,
  generateCriteriaDescription,
  getCriteriaFromSearchParams,
  createUpdateSearchParams
}
