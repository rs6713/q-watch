import React, { Component, useState, useEffect, useRef} from 'react';
import * as d3 from 'd3';
import {interpolateRainbow, interpolateWarm} from 'd3-scale-chromatic';

const MAX_CATEGORIES = 10
const MIN_PERCENT = 0
const MIN_ABSOLUTE = 3

const PieChart = ({dataset, dataChoice}) => {
  const ref = useRef();

  let graphContainer;
  var graphStyle;


  const [SVGdimensions, setSVGdimensions] = React.useState({ 
    minHeight: 0,
    width: 0
  })
  // const [dataChoice, setDataChoice] = useState('TYPES')

  

  useEffect(() => {
    graphContainer = document.getElementById('PieChart').parentElement;
    graphStyle = getComputedStyle(graphContainer);
    function handleResize() {

      var paddingX = parseFloat(graphStyle.paddingLeft) + parseFloat(graphStyle.paddingRight);
      var paddingY = parseFloat(graphStyle.paddingTop) + parseFloat(graphStyle.paddingBottom);

      setSVGdimensions({
        minHeight: graphContainer.clientHeight - paddingY,
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
    const svg = d3.select(ref.current)

    let height = SVGdimensions['width']//SVGdimensions['minHeight']
    let width = SVGdimensions['width']

    const fontSize = parseFloat(getComputedStyle(document.getElementById('PieChart').parentElement).fontSize);
    let multiplier = 5
    let margin = fontSize * multiplier;

    svg.attr("width", width)
    .attr("height", height)
    
    let data = dataset[dataChoice]

    let dataList = []
    for(let i=0; i< Object.keys(data).length; i++){
      let k = Object.keys(data)[i]
      dataList.push([k, data[k]])
    }
    // descending order
    dataList.sort((a, b) =>  b[1] - a[1]);
    var i = 0
    let j = dataList.length - 1;

    let newDataList = [];
    let other = 0;

    let total = dataList.reduce((a, b) => a.length === 2? a[1] + b[1] : a+b[1])
    if(dataList.length > MAX_CATEGORIES){
      other = dataList.slice(MAX_CATEGORIES).reduce((a, b) => a.length === 2? a[1] + b[1] : a+b[1])
      j = MAX_CATEGORIES - 1
    }

    while(((dataList[j][1]/total*100) < MIN_PERCENT || dataList[j][1] < MIN_ABSOLUTE) && j>=0 && dataList[j][1] ){
      other = other + dataList[j--][1]
    }

    let init_j = j + 1;
    while (i < j)
    {
      newDataList.push(dataList[i++])
      newDataList.push(dataList[j--])
    }
 
    // If the total element in array is odd
    // then print the last middle element.
    if (init_j % 2 != 0) newDataList.push(dataList[i]);
    if(other > 0){
      newDataList.push(['Other', other])
    }
    data = {};
    for(let i = 0; i< newDataList.length;  i++){
      data[newDataList[i][0]] = newDataList[i][1]
    }
    
    
    const g = svg.append("g")
    .attr("transform", `translate(${width/2}, ${height/2})`);

    var radius = (Math.min(width, height) / 2) - margin
    // svg.append("g")
    // .attr("transform", `translate(${width/2}, ${height/2})`);
    // //.attr("transform", "translate(" + -width / 2 + "," + height / 2 + ")");

    let lenKeys = Object.keys(data).length
    let cs = [];
    for (let i = 0; i< lenKeys; i++){
      cs.push(interpolateWarm(i/lenKeys))
    }
    var colorScale = d3.scaleOrdinal()
    .domain(Object.keys(data))
    .range(cs)

  // Compute the position of each group on the pie:
  const pie = d3.pie()
    .value(function(d) {return d[1]; })
    .sort(function(a, b) { return d3.ascending(a.key, b.key);} ) // This make sure that group order remains the same in the pie chart
  const data_ready = pie(Object.entries(data))

  // map to data
  const u = g.selectAll("path")
    .data(data_ready)

  // Build the pie chart: Basically, each part of the pie is a path that we build using the arc function.
  u
    .join('path')
    .transition()
    .duration(1000)
    .attr('d', d3.arc()
      .innerRadius(radius - 50)
      .outerRadius(radius)
    )
    .attr('fill', function(d){ return(colorScale(d.data[0])) })
    .attr("stroke", "white")
    .style("stroke-width", "2px")
    .style("opacity", 1)
    
    .attr('cursor', 'pointer')
    

    let labelRadius = radius + (margin / multiplier * (multiplier/2))
    const arcLabel = d3.arc().innerRadius(labelRadius).outerRadius(labelRadius);
  
    const formatValue = d3.format(",");
    const N = d3.map(data_ready, d => d[0]);
    const V = d3.map(data_ready, d => d[1]);
    let title = i => `${N[i]}\n${formatValue(V[i])}`;

    svg.append("g")
    .attr("transform", `translate(${width/2}, ${height/2})`)
    .attr("font-family", "Futura PT")
    .attr("font-size", fontSize)
    .attr("text-anchor", "middle")
  .selectAll("text")
  .data(data_ready)
  .join("text")
  .attr("transform", d => `translate(${arcLabel.centroid(d)})`)
  .selectAll("tspan")
  .data(d => {
    return `${d.data[0]}\n${formatValue(d.data[1])}`.split('\n');
    //return (d.endAngle - d.startAngle) > 0.25 ? lines : lines.split(/\n/).slice(0, 1);
  })
  .join("tspan")
  .attr("x", 0)
  .attr("font-weight", (_, i) => i ? null : "bold")
  .text(d => d)
  .call(wrap, fontSize * 5)
  .attr("y", (_, i) => `${i * 1.1}em`)

  function wrap(text, width) {
    let i = 0;
    let maxWrap = 0;
    text.each(function() {
      var text = d3.select(this),
          words = text.text().split(/\s+/).reverse(),
          num = text.text().split(/\s+/)[-1],
          word,
          line = [],
          lineNumber = 0,
          lineHeight = 1.1, // ems
          y = text.attr("y"),
          dy = 0,
          tspan = text.text(null).append("tspan").attr("x", 0).attr("y", y).attr("dy", dy + lineHeight * maxWrap + "em");
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
          tspan = text.append("tspan").attr("x", 0).attr("y", y).attr("dy",  lineHeight + dy + "em").text(word);
          maxWrap += 1;
          //.attr("font-weight", (_, i) => i ? null : "bold")
        }
      }
      //text.append("tspan").attr("x", 0).attr("y", y).attr("dy", lineNumber * lineHeight + dy + "em").text(num)
    });
  }



}

  useEffect(()=>{
    const svg = d3.select(ref.current)
    svg.selectAll("*").remove();
    addDataElements();
  }, [dataset, dataChoice])


  return (
    <div className='Graph'>
      <svg id='PieChart'
        ref={ref}
      />
    </div>
  )
}

export default PieChart;