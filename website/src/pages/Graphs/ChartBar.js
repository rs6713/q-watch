import React, { Component, useState, useEffect, useRef} from 'react';
import * as d3 from 'd3';
import {getColorScale} from './utils';
import {calculateCumulative, onlyUnique, createZKey} from '../data/utils'



function BarChart(data, {
  svg,
  x = ([x]) => x, // given d in data, returns the (temporal) x-value
  y = ([, y]) => y, // given d in data, returns the (quantitative) y-value
  z = () => 1, // given d in data, returns the (categorical) z-value
  defined, // for gaps in data
  marginTop = 20, // top margin, in pixels
  marginRight = 0, // right margin, in pixels
  marginBottom = 50, // bottom margin, in pixels
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
} = {}) {

  // Compute values.
  const X = d3.map(data, x);
  const Y = d3.map(data, y);
  const Z = d3.map(data, z);

  const color = getColorScale(Z.filter(onlyUnique));//d3.scaleOrdinal(zDomain, colors);

  // X axis
  const xScale = d3.scaleBand().range(xRange).domain(X).padding(0.2);
  const xAxis = d3.axisBottom(xScale)

  var yScale = yType().range(yRange).domain([1, d3.max(Y)]);

  const yAxis = d3.axisLeft(yScale);

  // Clear svg
  svg.selectAll("*").remove();
  
  svg
  //.attr("transform","translate(" + marginLeft + "," + marginRight + ")")
  //.attr('transform', 'translate()')
  .append("g")
    .attr("transform", `translate(0,${height - marginBottom})`)
    .call(xAxis)
    .selectAll("text")
      .attr("transform", "translate(0,0)rotate(-25)")
      .style("text-anchor", "end");


  if(yType === d3.scaleLinear){
    //yAxis = yAxis.ticks(10, 'd')
  }
  if(yType === d3.scaleSymlog){
    //yAxis = yAxis.ticks(parseInt(Math.log10(d3.max(Y)) + 1))
      // .tickFormat(d => {

      // })
  }

  svg.append("g")
    .attr('transform', `translate(${marginLeft}, 0)`)
    .call(yAxis)
    
    // .tickFormat(function (d) {
    //     var log = Math.log(d) / Math.LN10;
    //     return Math.abs(Math.round(log) - log) < 1e-6 ? Math.round(log) : '';
    // })
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

  // Bars
  svg.selectAll("mybar")
  .data(data)
  .enter()
  .append("rect")
    .attr("x", (_, i) => xScale(X[i]))
    .attr("y", (_, i) => yScale(Y[i]))
    .attr("width", xScale.bandwidth())
    .attr("height", (_, i) => height - marginBottom - yScale(Y[i]))
    .attr("fill", (_, i) => color(Z[i]))

    // .attr("x", function(d) { return x(d.Country); })
    //   .attr("y", function(d) { return y(d.Value); })



  return Object.assign(svg.node(), {scales: {color}}); //svg.node();
}

const ChartBar = ({dataset, limit, ...kwargs}) => {
  const ref = useRef();
  
  if(kwargs == null){
    kwargs = {}
  }

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

    console.log('Bar: ', dataset)

    createZKey(dataset)

    var data = dataset['data'].sort((a, b) => a[dataset['y']] < b[dataset['y']] ? 1 : -1)

    if(limit){
      let other = {
        [dataset['y']]: data.slice(limit).map(d => d[dataset['y']]).reduce((a,b) => a + b, 0),
        [dataset['x']]: 'Other',
        [dataset['z']]: 'Other'
      }

      data = data.slice(0, limit - 1)
      data.push(other)
    }
    
    if(dataset['agg'] === 'cumulative'){

      data = calculateCumulative(
        data,
        dataset['x'],
        dataset['y'],
        dataset['z_key']
      )
    }
    console.log('Bar: ', data)

    const l = BarChart(data, {
      svg,
      x: d => d[dataset['x']],
      y: d => d[dataset['y']],
      z: (dataset['z_key'] ? d => d[dataset['z_key']] : undefined),
      yLabel: dataset.yLabel,
      xLabel: dataset.xLabel,
      width: SVGdimensions['width'],
      height: SVGdimensions['height'],
      ...kwargs
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
      <svg id='BarChart'
        ref={ref}
      />
    </div>
  )
}

export default ChartBar;