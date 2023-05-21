import React, { Component, useState, useEffect, useRef} from 'react';
import * as d3 from 'd3';
import {getColorScale} from './utils';
import {calculateCumulative, onlyUnique, createZKey} from '../data/utils'



function LineChart(data, {
  svg,
  x = ([x]) => x, // given d in data, returns the (temporal) x-value
  y = ([, y]) => y, // given d in data, returns the (quantitative) y-value
  z = () => 1, // given d in data, returns the (categorical) z-value
  defined, // for gaps in data
  curve = d3.curveLinear, // method of interpolation between points
  marginTop = 20, // top margin, in pixels
  marginRight = 30, // right margin, in pixels
  marginBottom = 30, // bottom margin, in pixels
  marginLeft = 40, // left margin, in pixels
  width = 640, // outer width, in pixels
  height = 400, // outer height, in pixels
  xType = d3.scaleLinear, // the x-scale type
  xDomain, // [xmin, xmax]
  xRange = [marginLeft, width - marginRight], // [left, right]
  xFormat,
  yType = d3.scaleLinear, // the y-scale type
  yDomain, // [ymin, ymax]
  yRange = [height - marginBottom, marginTop], // [bottom, top]
  yFormat, // a format specifier string for the y-axis
  yLabel, // a label for the y-axis
  zDomain, // array of z-values
  strokeLinecap = "round", // stroke line cap of the line
  strokeLinejoin = "round", // stroke line join of the line
  strokeWidth = 2, // stroke width of line, in pixels
  strokeOpacity = 1, // stroke opacity of line
} = {}) {

  // Remove old plots
  svg.selectAll("*").remove();

  // Compute values.
  const X = d3.map(data, x);
  const Y = d3.map(data, y);
  const Z = d3.map(data, z);
  //const I = d3.range(X.length);
  if (defined === undefined) defined = (d, i) => !isNaN(X[i]) && !isNaN(Y[i]);
  const D = d3.map(X, defined);

  // Compute default domains.
  if (xDomain === undefined) xDomain = d3.extent(X);
  if (yDomain === undefined) yDomain = [0, d3.max(Y)];
  if (zDomain === undefined) zDomain = Z;
  zDomain = new d3.InternSet(zDomain);

  // Omit any data not present in the z-domain.
  const I = d3.range(X.length).filter(i => zDomain.has(Z[i]));


  // Construct scales and axes.
  const xScale = xType(xDomain, xRange);
  const yScale = yType(yDomain, yRange);
  const color = getColorScale(Z.filter(onlyUnique));//d3.scaleOrdinal(zDomain, colors);
  const xAxis = d3.axisBottom(xScale).ticks(width / 80, 'd').tickSizeOuter(0);
  const yAxis = d3.axisLeft(yScale).ticks(height / 40, yFormat);

  // Construct formats.
  yFormat = yScale.tickFormat(null, yFormat);
  xFormat = xScale.tickFormat(null, 'd')
  //"+,d"
  // const xAxis = d3.axisTop(xScale).ticks(width / 80, xFormat);
  // const format = xScale.tickFormat(100, xFormat);


  // Construct a line generator.
  const line = d3.line()
      .defined(i => D[i])
      .curve(curve)
      .x(i => xScale(X[i]))
      .y(i => yScale(Y[i]));

  svg.append("g")
      .attr("transform", `translate(0,${height - marginBottom})`)
      .call(xAxis);
  svg.append("g")
      .attr("transform", `translate(${marginLeft},0)`)
      .call(yAxis)
      .call(g => g.select(".domain").remove())
      .call(g => g.selectAll(".tick line").clone()
          .attr("x2", width - marginLeft - marginRight)
          .attr("stroke-opacity", 0.1))
      .call(g => g.append("text")
          .attr("x", -marginLeft)
          .attr("y", 10)  
          .attr("fill", "currentColor")
          .attr("text-anchor", "start")
          .text(yLabel));

  const serie = svg.append("g")
      .selectAll("g")
      .data(d3.group(I, i => Z[i]))
      .join("g");
        
  
  // const path = serie.append("path")
  //     .attr("fill", "none")
  //     .attr("stroke", ([key]) => color(key))
  //     .attr("stroke-width", strokeWidth)
  //     .attr("stroke-linecap", strokeLinecap)
  //     .attr("stroke-linejoin", strokeLinejoin)
  //     .attr("stroke-opacity", strokeOpacity)
  //     .style("mix-blend-mode", "multiply")
  //     .attr("d", ([, I]) => line(I));

  // svg.append("g")
  //     .attr("transform", `translate(${marginLeft},0)`)
  //     .call(yAxis)
  //     .call(g => g.select(".domain").remove())
  //     .call(g => g.selectAll(".tick line").clone()
  //         .attr("x2", width - marginLeft - marginRight)
  //         .attr("stroke-opacity", 0.1))
  //     .call(g => g.append("text")
  //         .attr("x", -marginLeft)
  //         .attr("y", 10)
  //         .attr("fill", "currentColor")
  //         .attr("text-anchor", "start")
  //         .text(yLabel));

  const path = serie.append("path")
  .attr("fill", "none")
  .attr("stroke", ([key]) => color(key))
  .attr("stroke-width", strokeWidth)
  .attr("stroke-linecap", strokeLinecap)
  .attr("stroke-linejoin", strokeLinejoin)
  .attr("stroke-opacity", strokeOpacity)
  .style("mix-blend-mode", "multiply")
  .attr("d", ([, I]) => line(I));

// serie.append("g")
//   .attr("font-family", "sans-serif")
//   .attr("font-size", 10)
//   .attr("text-anchor", "middle")
//   .attr("stroke-linejoin", "round")
//   .attr("stroke-linecap", "round")
// .selectAll("text")
// .data(([, I]) => I)
// .join("text")
//   .attr("dy", "0.35em")
//   .attr("x", i => xScale(X[i]))
//   .attr("y", i => yScale(Y[i]))
  // .text(i => yFormat(Y[i]))
  // .call(text => text
  //   .filter((_, j, I) => j === I.length - 1)
  //   .append("tspan")
  //     .attr("font-weight", "bold")
      // .attr("fill", "none")
      // .attr("stroke", halo)
      // .attr("stroke-width", haloWidth)
      // .text(i => Z[i] !== 1 ? ` ${Z[i]}` : ''))
  // .call(text => text.clone(true))
  // .attr("fill", "none")
  // .attr("stroke", halo)
  // .attr("stroke-width", haloWidth)


  // Add one dot in the legend for each name.
  console.log('z ', Z)
  let zLabels = Z.filter(onlyUnique);
  if(zLabels.length > 1){
    svg.selectAll("mydots")
    .data(zLabels)
    .enter()
    .append("circle")
      .attr("cx", 100)
      .attr("cy", function(d,i){ return 100 + i*25}) // 100 is where the first dot appears. 25 is the distance between dots
      .attr("r", 7)
      .style("fill", function(d){ return color(d)})

    // Add one dot in the legend for each name.
    svg.selectAll("mylabels")
    .data(zLabels)
    .enter()
    .append("text")
      .attr("x", 120)
      .attr("y", function(d,i){ return 100 + i*25}) // 100 is where the first dot appears. 25 is the distance between dots
      .attr("font-weight", "bold")
      .style("fill", 'black')
      .text(function(d){ return d})
      .attr("text-anchor", "left")
      .style("alignment-baseline", "middle")
  }


  return Object.assign(svg.node(), {scales: {color}}); //svg.node();
}

const ChartLine = ({dataset, ...kwargs}) => {
  const ref = useRef();
  if(kwargs == null){
    kwargs = {}
  }
  console.log('Kwargs: ', kwargs)

  let graphContainer;
  var graphStyle;


  const [SVGdimensions, setSVGdimensions] = React.useState({ 
    height: 0,
    width: 0
  })

  useEffect(() => {
    graphContainer = ref.current.parentElement;
    graphStyle = getComputedStyle(graphContainer);
    function handleResize() {

      var paddingX = parseFloat(graphStyle.paddingLeft) + parseFloat(graphStyle.paddingRight);
      var paddingY = parseFloat(graphStyle.paddingTop) + parseFloat(graphStyle.paddingBottom);
      console.log(graphContainer.paddingTop, graphContainer.clientWidth)
      setSVGdimensions({
        height: graphContainer.clientHeight - paddingY,
        width: graphContainer.clientWidth - paddingX
      })
      addDataElements();
    }
    window.addEventListener('resize', handleResize)
    handleResize();

    return _ => {
      window.removeEventListener('resize', handleResize)
    }
  }, [])

  function addDataElements(){
    
    if(dataset === null){
      return;
    }
    const svg = d3.select(ref.current);

    createZKey(dataset)

    var data = dataset['data'].sort((a, b) => a[dataset['x']] > b[dataset['x']] ? 1 : -1)
    
    if(dataset['agg'] === 'cumulative'){

      data = calculateCumulative(
        data,
        dataset['x'],
        dataset['y'],
        dataset['z_key']
      )
    }

    const l = LineChart(data, {
      svg,
      x: d => d[dataset['x']],
      y: d => d[dataset['y']],
      z: (dataset['z_key'] ? d => d[dataset['z_key']] : undefined),
      yLabel: dataset.yLabel,
      xLabel: dataset.xLabel,
      width: SVGdimensions['width'],
      height: SVGdimensions['height'],
      ...kwargs
      //color: "steelblue"
    })
  }

  useEffect(()=>{
    const svg = d3.select(ref.current)
    svg.attr("width", SVGdimensions['width'])
    .attr("height", SVGdimensions['height'])
    .attr("viewBox", [0, 0, SVGdimensions['width'], SVGdimensions['height']])
    .attr("style", "max-width: 100%; height: auto; height: intrinsic;");
    addDataElements();
  }, [dataset])

  useEffect(()=>{
    const svg = d3.select(ref.current)
    svg.attr("width", SVGdimensions['width'])
    .attr("height", SVGdimensions['height'])
    .attr("viewBox", [0, 0, SVGdimensions['width'], SVGdimensions['height']])
    .attr("style", "max-width: 100%; height: auto; height: intrinsic;");
    addDataElements();
  }, [])

  return (
    <div className='Graph'>
      <svg id='LineChart'
        ref={ref}
      />
    </div>
  )
}

export default ChartLine;