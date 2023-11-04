import React, { Component, useState, useEffect, useRef} from 'react';
import * as d3 from 'd3';
import resizeGraph, {cartesian, createHierarchicalData, textLineWrap} from './utils';

const DURATION = 750;

const color = d3.scaleOrdinal([true, false], ["#cc81dd", "#85f2e8"])
var BARSTEP, BARPADDING, BARGAP, MARGIN;


function down(svg, svgX, d, x, xAxis, fontSize) {

  if (!d.children ) return;// 

  // Rebind the current node to the background.
  svg.select(".background").datum(d);

  // Define two sequenced transitions.
  const transition1 = svg.transition().duration(DURATION);
  //const transition1X = svgX.transition().duration(DURATION);
  const transition2X = svgX.transition().duration(DURATION).delay(DURATION);
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
  const enter = bar(svg, svgX, down, d, ".y-axis", fontSize, x, xAxis)
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
  svgX.selectAll(".x-axis").transition(transition2X)
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
  /* x Domain map, i - y offset */
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

function bar(svg, svgX, down, d, selector, fontSize, x, xAxis) {
  const g = svg.insert("g", selector)
      .attr("class", "enter")
      .attr("transform", `translate(0,${BARSTEP * BARPADDING})`)
      .attr("text-anchor", "end")
      .style("font", `${fontSize}px Futura PT`);
      

  const bar = g.selectAll("g")
    .data(d.children)
    .join("g")
      .attr("cursor", d => !d.children ? null : "pointer")
      .on("click", (event, d) => down(svg, svgX, d, x, xAxis, fontSize));

  bar.append("text")
      .attr("x", MARGIN.left - 6)
      .attr("y", BARSTEP * (1 - BARPADDING) / 2)
      .attr("dy", ".35em")
      .text(d => d.data.name)
      .call(textLineWrap, MARGIN.left - 6, BARPADDING);

  bar.append("rect")
      .attr("x", x(0))
      .attr("width", d => x(d.score) - x(0))
      .attr("height", BARSTEP * (1 - BARPADDING));

  return g;
}

function up(svg, svgX, d, fontSize, x, xAxis) {
  if (!d.parent || !svg.selectAll(".exit").empty()) return;

  // Rebind the current node to the background.
  svg.select(".background").datum(d.parent);

  // Define two sequenced transitions.
  const transition1 = svg.transition().duration(DURATION);
  const transition1X = svgX.transition().duration(DURATION);
  const transition2 = transition1.transition();

  // Mark any currently-displayed bars as exiting.
  const exit = svg.selectAll(".enter")
      .attr("class", "exit");

  // Update the x-scale domain.
  x.domain([0, d3.max(d.parent.children, d => d.score)]);

  // Update the x-axis.
  svgX.selectAll(".x-axis").transition(transition1X)
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
  const enter = bar(svg, svgX, down, d.parent, ".exit", fontSize, x, xAxis)
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

function calculateScore(object, summary_var){
  object.scores = [];
  if(object.children){
    for(let child of object.children){
      object.scores.push(calculateScore(child, summary_var));
    }

    object.score = object.scores.reduce((a, b) => a + b, 0) / (summary_var == 'mean' ? object.scores.length : 1)
    return object.score;
  }else{
    object.score = object.value
    return object.score;
  }
}

const BarHierarchy = ({dataset, sort_ascending, grouping_vars, name_var, label_vars, value_var, summary_var}) => {
  const refX = useRef();
  const refGraph = useRef();

  // Establish margin, barspacing according to fontsize on page.
  var fontSize = parseFloat(getComputedStyle(document.getElementById('ControlPanel')).fontSize);
  BARSTEP = 2 * fontSize;
  BARPADDING = 3 / fontSize;
  MARGIN = ({top: 4 * fontSize, right: 2 * fontSize, bottom: 0, left: 12 * fontSize})


  var title = `Ranking ${grouping_vars} by ${summary_var} ${value_var}`

  // Control dimensions of graph as page resizes.
  const [SVGdimensions, setSVGdimensions] = React.useState({ 
    height: 0,
    width: 0
  })
  React.useEffect(resizeGraph(setSVGdimensions), []);

  React.useEffect(() => {
    console.log(BARSTEP, BARPADDING, MARGIN)
    console.log(dataset, sort_ascending, grouping_vars, name_var, label_vars, value_var, summary_var)

    let hierarchy_data = createHierarchicalData(dataset, name_var, value_var, grouping_vars, label_vars)
    let root = d3.hierarchy(hierarchy_data).sum(d => d.value)

    // Graph height, required so page covers all children
    let height = (() => {
      var max = 1;
      if(root.children === undefined) return 0;
      let longestChildren = root.children.length;
      for(let child of root.children){
        longestChildren = Math.max(longestChildren, child.children.length)
      }

      return longestChildren * (BARSTEP + BARPADDING) + MARGIN.bottom;
    })();
    height = Math.max(height + 1, SVGdimensions['height'] - MARGIN.top - fontSize);

    console.log(height)

    let yAxis = g => g
    .attr("class", "y-axis")
    .attr("transform", `translate(${MARGIN.left + 0.5},0)`)
    .call(g => g.append("line")
        .attr("stroke", "currentColor")
        .attr("y1", 0)
        .attr("y2", height - MARGIN.bottom))

    let xAxis = g => g
      .attr("class", "x-axis")
      .attr("transform", `translate(0,${MARGIN.top})`)
      .call(d3.axisTop(x).ticks(SVGdimensions['width'] / 80, "s"))
      .call(g => (g.selection ? g.selection() : g).select(".domain").remove())


    
    // Calculate and add .score attribute, sum of all children, or own value
    calculateScore(root, summary_var)
    root = root.sort((a, b) => (b.score - a.score) * (sort_ascending ? -1 : 1))
    .eachAfter(d => d.index = d.parent ? d.parent.index = d.parent.index + 1 || 0 : 0)
    
    // let width = container.clientWidth - paddingX;
    // var x = d3.scaleLinear().range([MARGIN.left, width - MARGIN.right])
    console.log([MARGIN.left, SVGdimensions['width'] - MARGIN.right], MARGIN.right, SVGdimensions['width'])
    var x = d3.scaleLinear().range([MARGIN.left, Math.max(MARGIN.left + 1, SVGdimensions['width'] - MARGIN.right)])
    x.domain([0, Math.max(root.score)]);

    const svgX = d3.select(refX.current)
    // Title
    svgX.selectAll('*').remove();
    svgX.attr('width', SVGdimensions['width']);
    svgX.attr('height', MARGIN.top + fontSize);
    svgX.append('rect').attr('class', 'background').attr('fill', 'white')
    .attr('width', SVGdimensions['width'])
    .attr('height', MARGIN.top + fontSize)


    svgX.append("text")
    .attr("x", (SVGdimensions['width'] / 2))         
    .attr("y", (MARGIN.top / 2) - (fontSize / 2))
    .attr("text-anchor", "middle")  
    .style("text-decoration", "underline")
    .attr("font-size", fontSize)
    .attr("fill", "black")
    .text(title);

    // x axis
    svgX.append("g")
    .call(xAxis);

    const svg = d3.select(refGraph.current)
    svg.selectAll("*").remove();
    svg.attr("width", SVGdimensions['width'])
      .attr("height", height) // height)

    // Graph Background
    svg.append("rect")
        .attr("class", "background")
        .attr("fill", "white")
        .attr("pointer-events", "all")
        .attr("width", SVGdimensions['width'])
        .attr("height", height)// height)
        //.attr("viewBox", "0 0 "+ toString(SVGdimensions['width']) + ' ' + toString(SVGdimensions['height'] - MARGIN.top - fontSize))
        .attr("cursor", "pointer")
        .on("click", (event, d) => up(svg, svgX, d, fontSize, x, xAxis));

    // y axis
    svg.append("g")
        .call(yAxis);

    // how to navigate down the hierarchy
    //down(svg, root, x, xAxis, fontSize);
    down(svg, svgX, root, x, xAxis, fontSize);

  }, [ sort_ascending, grouping_vars, SVGdimensions, summary_var, dataset]);//


  return (
    <div id = 'BarHierarchy'>
      <svg id='BarHierarchyX'
        ref={refX}
      />
      <div id='BarHierarchyGraph'>
        <svg
          ref={refGraph}
        />
      </div>
    </div>
  )
}

export default BarHierarchy;