import {continents, countries} from 'countries-list'

function getContinent(country){
  for(let country of Object.values(countries)){
    if(country.name == country){
      return continents[country.continent]
    }
  }
  if(country == 'Space'){
    return 'Space'
  }
  return 'Unknown'
}

function getMovieValues(obj, key){
  if(Object.keys(obj).indexOf(key) == -1 || obj[key] === null) return [];

  if(['number', 'string'].indexOf(typeof obj[key]) !== -1){
    return [obj[key]]
  }
  else if(Array.isArray(obj[key])){
    return obj[key].map(o => o.LABEL)
  }else{
    return [obj[key].LABEL]
  }
}

function generateCombinations(arr1, arrs){
  if(arrs === undefined){
    if(arr1.length >= 2){
      return generateCombinations(arr1[0], arr1.slice(1))
    }
    return arr1[0].map(_ => [_]);
  }
  var combinations = [];
  var arr2 = [];
  if(arrs.length == 0){
    return arr1;
  }
  if(arrs.length == 1){
    arr2 = arrs[0].map(a=> [a]);
  }
  if(arrs.length >= 2){
    arr2 = generateCombinations(arrs[0], arrs.slice(1))
  }

  for(let a1 of arr1){
    for(let a2 of arr2){
      combinations.push(
        [a1, ...a2]
      )
    }
  }
  return combinations
}



function groupDataAgg(data, groups, {
  val,
  percent,
  returnType='list'
}={}){
  var groupedData = {};
  var totals, percentGroupIndex;
  // Totals by single group (percent)
  if(percent !== undefined){
    totals = groupDataAgg(data, [percent], {val: val, returnType:'dict'})
    percentGroupIndex = groups.indexOf(percent)

  }

  for(let d of data){
    let gs = groups.map(g=> getMovieValues(d, g)).filter(g=> g.length > 0);
    // If not all keys are present e.g. representations, early exit.
    if(gs.length != groups.length) continue;
    let keys = generateCombinations(gs);

    let v = val === undefined ? 1 : parseInt(getMovieValues(d, val)[0]);

    for(let key of keys){
      let k = key.join(' - ')

      var tempV = v;
      if(percent !== undefined){
        tempV = v / totals[key[percentGroupIndex]] * 100
      }
      if(Object.keys(groupedData).indexOf(k) !== -1){
        groupedData[k] += tempV;
      }else{
        groupedData[k] = tempV;
      }
    }
  }
  // Single dict, where groups are string concatenated to form keys
  if(returnType === 'dict'){
    return groupedData
  }

  // List of objects, where each group is individual key, as well as value
  if(returnType === 'list'){
    let finalGroups = [];
    for(let [k, v] of Object.entries(groupedData)){
      let kvs = k.split(' - ')
      let o = {};
      for(let i=0; i< kvs.length; i++){
        o[groups[i]] = kvs[i];
      }
      o['VALUE'] = v;
      finalGroups.push(o);
    }



    return finalGroups;
  }
}


function getLowestXValueKeys(obj, x){
  return getXKeys(obj, x, -1)
}
function getHighestXValueKeys(obj, x){
  return getXKeys(obj, x, 1)
}


function getXKeys(obj, x, order){
  if (obj == null) return null

  return Object.entries(obj).sort((a, b) => a[1] < b[1]? 1 * order : -1 * order).slice(0, x).map(
    e => e[0]
  )
}

function getXValues(obj, x, order, agg=null){
  if (obj == null) return null

  var vals = Object.values(obj).sort((a, b) => a < b? 1 * order: -1 * order).slice(0, x)
  if(agg == null){
    return vals;
  }else if(agg === 'sum'){
    return vals.reduce((a, b) => a+b, 0)
  }else if(agg === 'mean'){
    return vals.reduce((a, b) => a + b, 0) / vals.length
  }
  return null;
}

function getLowestXValuesAgg(obj, x, agg){
  return getXValues(obj, x, -1, agg)
}
function getHighestXValuesAgg(obj, x, agg){
  return getXValues(obj, x, 1, agg)
}

function getLowestXValues(obj, x){
  return getXValues(obj, x, -1)
}
function getHighestXValues(obj, x){
  return getXValues(obj, x, 1)
}

function getMaxValueKey(obj){
  if (obj == null) return null
  return Object.entries(obj).filter(
    k => k[1] == Math.max(...Object.values(obj))
  )[0][0]
}

function getMaxKey(obj){
  if (obj == null) return null
  return Math.max(...Object.keys(obj))
}

function getMaxValue(obj){
  if (obj == null) return null
  return Math.max(...Object.values(obj))
}

function onlyUnique(value, index, array) {
  return array.indexOf(value) === index;
}

function createZKey(dataset){
  if(dataset['z'] !== undefined){

    if(dataset['z'].length > 1){
      for(let o of dataset['data']){
        let k = [];
        for(let zz of dataset['z']){
          k.push(o[zz])
        }
        o[dataset['z'].join(' - ')] = k.join(' - ')
      }
      dataset['z_key'] = dataset['z'].join(' - ')
    }else{
      dataset['z_key'] = dataset['z'][0]
    }
  }
}


function calculateCumulative(data, x, y, group_key){
  var newdata = [];

  if(group_key !== undefined){
    let zzs = data.map(d => d[group_key])
    zzs = zzs.filter(onlyUnique)

    for(let zs of zzs){
      var prev_val = null;
      var vals = data.filter(d => d[group_key] == zs).sort((a, b) => a[x] > b[x] ? 1 : -1)
      for(let val of vals){
        newdata.push(
          {...val, [y]: val[y] + (prev_val || 0)}
        )
        prev_val = val[y] + (prev_val || 0)
      }
    }
  }else{
    var prev_val = null;
    var vals = data.sort((a, b) => a[x] > b[x] ? 1 : -1)
    for(let val of vals){
      newdata.push(
        {...val, [y]: val[y] + (prev_val || 0)}
      )
      prev_val = val[y] + (prev_val || 0)
    }
  }
  return newdata.sort((a, b) => a[x] > b[x] ? 1 : -1);

}

export {
  groupDataAgg,
  getLowestXValues,
  getLowestXValuesAgg,
  getLowestXValueKeys,
  getMaxValueKey,
  getMaxValue,
  getMaxKey,
  getHighestXValues,
  getHighestXValuesAgg,
  getHighestXValueKeys,
  onlyUnique,
  calculateCumulative,
  createZKey,
}