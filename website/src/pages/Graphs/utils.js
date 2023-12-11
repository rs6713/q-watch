import {interpolateRainbow, interpolateWarm} from 'd3-scale-chromatic';
import * as d3 from 'd3';
var resizeGraph = (setGraphDimensions) => {

  return () => {
  var throttled = false;
  // https://bencentra.com/code/2015/02/27/optimizing-window-resize.html
  function handleResize() {

    if (!throttled) {
      let graphContainer = document.getElementsByClassName('Graph')[0];
      let graphStyle = getComputedStyle(graphContainer);
      var paddingX = parseFloat(graphStyle.paddingLeft) + parseFloat(graphStyle.paddingRight);
      var paddingY = parseFloat(graphStyle.paddingTop) + parseFloat(graphStyle.paddingBottom);

      setGraphDimensions({
        height: graphContainer.clientHeight - paddingY,
        width: graphContainer.clientWidth - paddingX
      })

      // we're throttled!
      throttled = true;
      // set a timeout to un-throttle
      setTimeout(function() {
        throttled = false;
      }, 250);
    }
  }
  window.addEventListener('resize', handleResize)
  handleResize();

  return _ => {
    window.removeEventListener('resize', handleResize)
  }
}
}

function getColorScale(keys){
  let lenKeys = keys.length
  let cs = [];
  for (let i = 0; i< lenKeys; i++){
    cs.push(interpolateWarm(i/lenKeys))
  }
  return d3.scaleOrdinal()
  .domain(keys)
  .range(cs)
}

function cartesian(...args) {
  var r = [], max = args.length-1;
  function helper(arr, i) {
      for (var j=0, l=args[i].length; j<l; j++) {
        var a = arr.slice(0); // clone arr
        a.push(args[i][j]);
        if (i==max)
            r.push(a);
        else
            helper(a, i+1);
      }
  }
  helper([], 0);
  return r;
}

function textLineWrap(text, width, linePad) {
  let i = 0;
  let maxWrap = 0;
  text.each(function() {
    let wrapped_text = false;
    var text = d3.select(this),
        words = text.text().split(/\s+/).reverse(),
        num = text.text().split(/\s+/)[-1],
        word,
        line = [],
        lineNumber = 0,
        lineHeight = 1.1, // ems
        y = text.attr("y"),
        x = text.attr("x"),
        dy = 0,
        tspan = text.text(null).append("tspan").attr("x", x).attr("y", y);
        //.attr("dy", dy + lineHeight * maxWrap + "em")
        if (maxWrap > 0){
          maxWrap = 0;
        }

    while (word = words.pop()) {
      line.push(word);
      tspan.text(line.join(" "));
      if (tspan.node().getComputedTextLength() > width && (line.length > 1)) {
        line.pop();
        tspan.text(line.join(" "));
        line = [word];
        if(wrapped_text== false){
          tspan.attr("dy", - (linePad/2))
        }
        tspan = text.append("tspan").attr("x", x).attr("y", y).attr("dy",  lineHeight + dy + "em").text(word);
        maxWrap += 1;
        wrapped_text = true;
        //.attr("font-weight", (_, i) => i ? null : "bold")
      }
      if(wrapped_text){

      }
    }
    //text.append("tspan").attr("x", 0).attr("y", y).attr("dy", lineNumber * lineHeight + dy + "em").text(num)
  });
}

const createHierarchicalData = (data, name_var, value_var, grouping_vars, label_vars) => {
  /*
  Translate data to hierarchical form
  */
  let dataHierarchy = [];
  // If there are no grouping vars (top level)
  if(grouping_vars === null || grouping_vars.length === 0){
    for(let item of data){
      let newItem = {
        'value': value_var === 'COUNT' ? 1 : item[value_var],
        'children': [],
        'name': item[name_var]
      };

      dataHierarchy.push(newItem);
    }
  }else{
    // For each movie
    for(let item of data){
      let group_keys = [];
      // Collect group keys
      for(let g of grouping_vars){
        if(item[g] !== null){
          group_keys.push(item[g].map(i => i.LABEL))
        }
      }
      // A movie can count under all combinations of it's sub-label categories
      let group_combinations = group_keys.length ? cartesian(...group_keys).map(i => i.join(' - ')): []

      // Item representing movie's name and value
      let i = {'value': value_var == 'COUNT'? 1 : item[value_var], 'name': item[name_var]}

      // Add movie to each of it's group combinations.
      // Creating new array if group combination doesn't already exist.
      for(let key of group_combinations){
        let foundCategory = false;
        for(let newItem of dataHierarchy){
          if(newItem['name'] === key){
            newItem['children'].push(i)
            foundCategory = true;
          }
        }
        if(!foundCategory){
          dataHierarchy.push(
            {'name': key, 'children': [i]}
          )
        }
      }
    }
  }
  return {name: 'root', children: dataHierarchy}
}


export {
  cartesian,
  createHierarchicalData,
  getColorScale,
  textLineWrap
}

export default resizeGraph