import React, { Component, useState, useEffect, useRef} from 'react';
import * as d3 from 'd3';
import resizeGraph from './utils';

const DURATION = 750;

const color = d3.scaleOrdinal([true, false], ["#cc81dd", "#85f2e8"])
var BARSTEP, BARPADDING, BARGAP, MARGIN;


const createRoot = (data, sort_ascending) => {
  return  d3.hierarchy(data)
    .sum(d => d.value)
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

function wrap(text, width) {
  let i = 0;
  let maxWrap = 0;
  text.each(function() {
    console.log('Text ', d3.select(this).text().split(/\s+/).reverse())
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
    console.log('dy ', dy, ' lineHeight ', lineHeight)
    while (word = words.pop()) {
      line.push(word);
      tspan.text(line.join(" "));
      if (tspan.node().getComputedTextLength() > width && (line.length > 1)) {
        line.pop();
        tspan.text(line.join(" "));
        line = [word];
        if(wrapped_text== false){
          tspan.attr("dy", - (BARPADDING/2))
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

function down(svg, d, x, xAxis, fontSize) {
  if (!d.children || d3.active(svg.node())) return;

  // Rebind the current node to the background.
  svg.select(".background").datum(d);

  // Define two sequenced transitions.
  const transition1 = svg.transition().duration(DURATION);
  const transition2 = transition1.transition();

  // Mark any currently-displayed bars as exiting.
  const exit = svg.selectAll(".enter")
      .attr("class", "exit");

  // Entering nodes immediately obscure the clicked-on bar, so hide it.
  exit.selectAll("rect")
      .attr("fill-opacity", p => p === d ? 0 : null);

  // Transition exiting bars to fade out.
  exit.transition(transition1)
      .attr("fill-opacity", 0)
      .remove();

  // Enter the new bars for the clicked-on data.
  // Per above, entering bars are immediately visible.
  const enter = bar(svg, down, d, ".y-axis", fontSize, x, xAxis)
      .attr("fill-opacity", 0);

  // Have the text fade-in, even though the bars are visible.
  enter.transition(transition1)
      .attr("fill-opacity", 1);

  // Transition entering bars to their new y-position.
  enter.selectAll("g")
      .attr("transform", stack(d.index, x))
    .transition(transition1)
      .attr("transform", stagger(x));

  // Update the x-scale domain.
  x.domain([0, d3.max(d.children, d => d.score)]);

  // Update the x-axis.
  svg.selectAll(".x-axis").transition(transition2)
      .call(xAxis);

  // Transition entering bars to the new x-scale.
  enter.selectAll("g").transition(transition2)
      .attr("transform", (d, i) => `translate(0,${BARSTEP * i})`);

  // Color the bars as parents; they will fade to children if appropriate.
  enter.selectAll("rect")
      .attr("fill", color(true))
      .attr("fill-opacity", 1)
    .transition(transition2)
      .attr("fill", d => color(!!d.children))
      .attr("width", d => x(d.score) - x(0));
}

function stack(i, x) {
  let value = 0;
  return d => {
    const t = `translate(${x(value) - x(0)},${BARSTEP * i})`;
    value += d.score;
    return t;
  };
}

function stagger(x) {
  let value = 0;
  return (d, i) => {
    const t = `translate(${x(value) - x(0)},${BARSTEP * i})`;
    value += d.score;
    return t;
  };
}

function bar(svg, down, d, selector, fontSize, x, xAxis) {
  const g = svg.insert("g", selector)
      .attr("class", "enter")
      .attr("transform", `translate(0,${MARGIN.top + BARSTEP * BARPADDING})`)
      .attr("text-anchor", "end")
      .style("font", `${fontSize}px Futura PT`);
      

  const bar = g.selectAll("g")
    .data(d.children)
    .join("g")
      .attr("cursor", d => !d.children ? null : "pointer")
      .on("click", (event, d) => down(svg, d, x, xAxis, fontSize));

  bar.append("text")
      .attr("x", MARGIN.left - 6)
      .attr("y", BARSTEP * (1 - BARPADDING) / 2)
      .attr("dy", ".35em")
      .text(d => d.data.name)
      .call(wrap, MARGIN.left);

  bar.append("rect")
      .attr("x", x(0))
      .attr("width", d => x(d.score) - x(0))
      .attr("height", BARSTEP * (1 - BARPADDING));

  return g;
}

const BarHierarchy = ({dataset, sort_ascending, grouping_vars, name_var, label_vars, value_var, summary_var}) => {
  const ref = useRef();

  var fontSize = parseFloat(getComputedStyle(document.getElementById('ControlPanel')).fontSize);
  BARSTEP = 2 * fontSize;
  BARPADDING = 3 / fontSize;
  MARGIN = ({top: 4 * fontSize, right: 2 * fontSize, bottom: 0, left: 10 * fontSize})


  var title = `Ranking ${label_vars} by ${summary_var} ${value_var}`

  const [SVGdimensions, setSVGdimensions] = React.useState({ 
    height: 0,
    width: 0
  })
  React.useEffect(resizeGraph(setSVGdimensions), []);


  useEffect(() => {
  




function up(svg, d) {
  if (!d.parent || !svg.selectAll(".exit").empty()) return;

  // Rebind the current node to the background.
  svg.select(".background").datum(d.parent);

  // Define two sequenced transitions.
  const transition1 = svg.transition().duration(DURATION);
  const transition2 = transition1.transition();

  // Mark any currently-displayed bars as exiting.
  const exit = svg.selectAll(".enter")
      .attr("class", "exit");

  // Update the x-scale domain.
  x.domain([0, d3.max(d.parent.children, d => d.score)]);

  // Update the x-axis.
  svg.selectAll(".x-axis").transition(transition1)
      .call(xAxis);

  // Transition exiting bars to the new x-scale.
  exit.selectAll("g").transition(transition1)
      .attr("transform", stagger(x));

  // Transition exiting bars to the parent’s position.
  exit.selectAll("g").transition(transition2)
      .attr("transform", stack(d.index, x));

  // Transition exiting rects to the new scale and fade to parent color.
  exit.selectAll("rect").transition(transition1)
      .attr("width", d => x(d.score) - x(0))
      .attr("fill", color(true));

  // Transition exiting text to fade out.
  // Remove exiting nodes.
  exit.transition(transition2)
      .attr("fill-opacity", 0)
      .remove();

  // Enter the new bars for the clicked-on data's parent.
  const enter = bar(svg, down, d.parent, ".exit", fontSize, x, xAxis)
      .attr("fill-opacity", 0);

  enter.selectAll("g")
      .attr("transform", (d, i) => `translate(0,${BARSTEP * i})`);

  // Transition entering bars to fade in over the full duration.
  enter.transition(transition2)
      .attr("fill-opacity", 1);

  // Color the bars as appropriate.
  // Exiting nodes will obscure the parent bar, so hide it.
  // Transition entering rects to the new x-scale.
  // When the entering parent rect is done, make it visible!
  enter.selectAll("rect")
      .attr("fill", d => color(!!d.children))
      .attr("fill-opacity", p => p === d ? 0 : null)
    .transition(transition2)
      .attr("width", d => x(d.score) - x(0))
      .on("end", function(p) { d3.select(this).attr("fill-opacity", 1); });
}



let yAxis = g => g
    .attr("class", "y-axis")
    .attr("transform", `translate(${MARGIN.left + 0.5},0)`)
    .call(g => g.append("line")
        .attr("stroke", "currentColor")
        .attr("y1", MARGIN.top)
        .attr("y2", height - MARGIN.bottom))

let xAxis = g => g
  .attr("class", "x-axis")
  .attr("transform", `translate(0,${MARGIN.top})`)
  .call(d3.axisTop(x).ticks(SVGdimensions['width'] / 80, "s"))
  .call(g => (g.selection ? g.selection() : g).select(".domain").remove())


  console.log(sort_ascending, grouping_vars, name_var, label_vars, value_var)
  console.log(dataset[0])
  

  let hierarchy_data = createHierarchicalData(dataset, name_var, value_var, grouping_vars, label_vars)

  let root = createRoot(hierarchy_data, sort_ascending);

  let height = (() => {
    var max = 1;
    //root.each
    root.each(d => d.children && (max = Math.max(max, d.children.length)));
    console.log('Max', max)
    return max * BARSTEP + MARGIN.top + MARGIN.bottom;
  })();

  // let container = document.getElementsByClassName('Graph')[0];
  // var cs = getComputedStyle(container);
  // var paddingX = parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight);
  // var paddingY = parseFloat(cs.paddingTop) + parseFloat(cs.paddingBottom);


  // let width = container.clientWidth - paddingX;
  // var x = d3.scaleLinear().range([MARGIN.left, width - MARGIN.right])
  var x = d3.scaleLinear().range([MARGIN.left, SVGdimensions['width'] - MARGIN.right])

  function calculateScore(object){
    object.scores = [];
    if(object.children){
      console.log(object.children)
      for(let child of object.children){
        object.scores.push(calculateScore(child));
      }
      object.score =  object.scores.reduce((a, b) => a + b, 0) / (summary_var == 'mean' ? object.scores.length : 1)
      return object.score;
    }else{
      object.score = object.value 
      return object.score;
    }
  }

  calculateScore(root)
  root = root.sort((a, b) => (b.score - a.score) * (sort_ascending ? -1 : 1))
  .eachAfter(d => d.index = d.parent ? d.parent.index = d.parent.index + 1 || 0 : 0)
  
  x.domain([0, root.score]);

  //let minHeight = container.clientHeight - paddingY;
  height = Math.max(height, SVGdimensions['height']);

  console.log('Height: ', height)

  const svg = d3.select(ref.current)
  svg.selectAll("*").remove();
  svg.attr("width", SVGdimensions['width'])
    .attr("height", height)

  // Graph Background
  svg.append("rect")
      .attr("class", "background")
      .attr("fill", "white")
      .attr("pointer-events", "all")
      .attr("width", SVGdimensions['width'])
      .attr("height", height)
      .attr("cursor", "pointer")
      .on("click", (event, d) => up(svg, d));

  // Title
  svg.append("text")
  .attr("x", (SVGdimensions['width'] / 2))         
  .attr("y", (MARGIN.top / 2) - (fontSize / 2))
  .attr("text-anchor", "middle")  
  .style("text-decoration", "underline")  
  .attr("font-size", fontSize)
  .attr("fill", "black")
  .text(title);

  // x axis
  svg.append("g")
      .call(xAxis);

  // y axis
  svg.append("g")
      .call(yAxis);

  // how to navigate down the hierarchy
  down(svg, root, x, xAxis, fontSize);

}, [dataset, sort_ascending, grouping_vars]);



  return (
      <svg id='BarHierarchy'
        ref={ref}
      />
  )
}

export default BarHierarchy;