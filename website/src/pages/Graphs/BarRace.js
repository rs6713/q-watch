import React, { Component, useState, useEffect, useRef} from 'react';
import * as d3 from 'd3';
import { max } from 'd3';

const duration = 250;
const k = 10; // Number of interpolated datapoints
const n = 12; // Number of bars in our graph.

const BarRace = ({data, grouping_vars, name_var, label_vars, value_var}) => {
  const ref = useRef();

  let graphContainer;
  var graphStyle;
  let fontSize; 


  const [SVGdimensions, setSVGdimensions] = React.useState({ 
    minHeight: 0,
    width: 0
  })

  React.useEffect(() => {
    function handleResize() {

      graphContainer = document.getElementsByClassName('Graph')[0];
      graphStyle = getComputedStyle(graphContainer);
      fontSize = parseFloat(getComputedStyle(document.getElementById('ControlPanel')).fontSize);

      var paddingX = parseFloat(graphStyle.paddingLeft) + parseFloat(graphStyle.paddingRight);
      var paddingY = parseFloat(graphStyle.paddingTop) + parseFloat(graphStyle.paddingBottom);

      setSVGdimensions({
        minHeight: graphContainer.clientHeight - paddingY,
        width: graphContainer.clientWidth - paddingX
      })
    }
    window.addEventListener('resize', handleResize)
    handleResize();

    return _ => {
      window.removeEventListener('resize', handleResize)
    }
  }, [])

  let year_data = d3.merge(
    Array.from(
        d3.map(data, d => (
          d3.map(
            Array.from(d3.cross(
              ...d3.map(grouping_vars, gv => d[gv].map(g => g.LABEL))
            )),
            lbls => ({
              'GROUP': lbls.join(', '),
              'YEAR': d.YEAR,
              'VALUE': d.sort_key,
              'TITLE': d.TITLE
            })
        ))
      )
    )
  )
  console.log(year_data)

  let groups = new Set(year_data.map(d => d.GROUP))
  console.log('Groups: ', groups)

  const margin = ({top: 20, right: 5 * max(Array.from(groups).map(g => g.length)), bottom: 20, left: 20})
  console.log(margin)
  const svg = d3.select(ref.current)
  let height = SVGdimensions['minHeight']

  svg.selectAll("*").remove();
  svg.attr("width", SVGdimensions['width'])
    .attr("height", height)

  svg.append("rect")
      .attr("class", "background")
      .attr("fill", "white")
      .attr("pointer-events", "all")
      .attr("width", SVGdimensions['width'])
      .attr("height", height)
      .attr("cursor", "pointer")


  

  const barSize = (height - margin.top - margin.bottom) / n


  let x = d3.scaleLinear([0, 1], [margin.left, SVGdimensions['width'] - margin.right])
  let y = d3.scaleBand()
    .domain(d3.range(n + 1))
    .rangeRound([margin.top, margin.top + barSize * (n + 1 + 0.1)])
    .padding(0.1)


  // console.log(
  //   Array.from(d3.rollup(year_data, 
  //     //([d]) => d,
  //     d1 => d1 ,
  //     // (d1, d2) => ({
  //     // 'VALUE': d1 !== undefined ? d2 !== undefined? d1.VALUE + d2.VALUE: d1.VALUE : 0
  //     // //'VALUE':d.map(o => o.VALUE).reduce((a, b) => a+b),
  //     // //'TITLE': d1.TITLE.length ? (!!d1.TITLE.forEach ? [...d1.TITLE] : [d1.TITLE]): [d2.TITLE],//]d1? [...d1.TITLE, d2.TITLE] : [d2.TITLE]
  //     // }),
  //   d => +d.YEAR, d => d.GROUP))
  // )
  let years = Array.from(d3.rollup(year_data, d => d, d => +d.YEAR, d => d.GROUP))
    .map(([year, data]) => [new Date(`${year}-01-01`), data])
    .sort(([a], [b]) => d3.ascending(a, b))
  console.log('Years: ', years)

  function rank(value) {
    const data = Array.from(groups, group => ({group, value: value(group)}));
    data.sort((a, b) => d3.descending(a.value, b.value));
    for (let i = 0; i < data.length; ++i) data[i].rank = Math.min(n, i);
    return data;
  }

  function getValue(dateMovies){
    if (dateMovies === undefined){
      return 0
    }
    return dateMovies.map(d => d.VALUE).reduce((a, b) => a + b)
  }

  function generateKeyframes(){
    const keyframes = [];
    let ka, a, kb, b;
    let group_totals = {};
    for ([[ka, a], [kb, b]] of d3.pairs(years)) {
      console.log(ka, kb)
      console.log(a)
      for (let i = 0; i < k; ++i) {
        const t = i / k;
        let new_group_values = rank(group => {
          
          let newGroupVal = (getValue(b.get(group)) || 0) / k;

          group_totals[group] = (group_totals[group] || 0) + newGroupVal;
          return group_totals[group]
        });
        keyframes.push([
          new Date(ka * (1 - t) + kb * t),
          new_group_values
        ]);
      }
    }
    keyframes.push([new Date(kb), rank(group => b.get(group) || 0)]);
    return keyframes;
  };
  let keyframes = generateKeyframes();


  console.log('Keyframes: ', keyframes)

  let nameframes = d3.groups(keyframes.flatMap(([, data]) => data), d => d.group)

  let prev = new Map(nameframes.flatMap(([, data]) => d3.pairs(data, (a, b) => [b, a])))
  let next = new Map(nameframes.flatMap(([, data]) => d3.pairs(data)))

  function bars(svg) {
    let bar = svg.append("g")
        .attr("fill-opacity", 0.6)
      .selectAll("rect");
  
    return ([date, data], transition) => bar = bar
      .data(data.slice(0, n), d => d.group)
      .join(
        enter => enter.append("rect")
          .attr("fill", color())
          .attr("height", y.bandwidth())
          .attr("x", x(0))
          .attr("y", d => y((prev.get(d) || d).rank))
          .attr("width", d => x((prev.get(d) || d).value) - x(0)),
        update => update,
        exit => exit.transition(transition).remove()
          .attr("y", d => y((next.get(d) || d).rank))
          .attr("width", d => x((next.get(d) || d).value) - x(0))
      )
      .call(bar => bar.transition(transition)
        .attr("y", d => y(d.rank))
        .attr("width", d => x(d.value) - x(0)));
  }

  function labels(svg) {
    let label = svg.append("g")
        .style("font", `bold ${fontSize}px var(--Futura PT)`)
        .style("font-variant-numeric", "tabular-nums")
        .attr("text-anchor", "start")
      .selectAll("text");
  
    return ([date, data], transition) => label = label
      .data(data.slice(0, n), d => d.group)
      .join(
        enter => enter.append("text")
          .attr("transform", d => `translate(${x((prev.get(d) || d).value)},${y((prev.get(d) || d).rank)})`)
          .attr("y", y.bandwidth() / 2)
          .attr("x", 6)
          .attr("dy", "-0.25em")
          .text(d => d.group)
          .call(text => text.append("tspan")
            .attr("fill-opacity", 0.7)
            .attr("font-weight", "normal")
            .attr("x", 6)
            .attr("dy", "1.15em")),
        update => update,
        exit => exit.transition(transition).remove()
          .attr("transform", d => `translate(${x((next.get(d) || d).value)},${y((next.get(d) || d).rank)})`)
          .call(g => g.select("tspan").tween("text", d => textTween(d.value, (next.get(d) || d).value)))
      )
      .call(bar => bar.transition(transition)
        .attr("transform", d => `translate(${x(d.value)},${y(d.rank)})`)
        .call(g => g.select("tspan").tween("text", d => textTween((prev.get(d) || d).value, d.value))))
  }

 let formatNumber = d3.format(",d")

  function textTween(a, b) {
    const i = d3.interpolateNumber(a, b);
    return function(t) {
      this.textContent = formatNumber(i(t));
    };
  }

  function axis(svg) {
    const g = svg.append("g")
        .attr("transform", `translate(0,${margin.top})`);
  
    const axis = d3.axisTop(x)
        .ticks(SVGdimensions['width'] / 160)
        .tickSizeOuter(0)
        .tickSizeInner(-barSize * (n + y.padding()));
  
    return (_, transition) => {
      g.transition(transition).call(axis);
      g.select(".tick:first-of-type text").remove();
      g.selectAll(".tick:not(:first-of-type) line").attr("stroke", "white");
      g.select(".domain").remove();
    };
  }

  function ticker(svg) {
    const now = svg.append("text")
        .style("font", `bold ${barSize}px var(--Futura PT)`)
        .style("font-variant-numeric", "tabular-nums")
        .attr("text-anchor", "end")
        .attr("x", SVGdimensions['width'] - 6)
        .attr("y", margin.top + barSize * (n - 0.45))
        .attr("dy", "0.32em")
        .text(formatDate(keyframes[0][0]));
  
    return ([date], transition) => {
      transition.end().then(() => now.text(formatDate(date)));
    };
  }

  function color(){
    const scale = d3.scaleOrdinal(d3.schemeTableau10);
    if (data.some(d => d.category !== undefined)) {
      const categoryByName = new Map(data.map(d => [d.group, d.category]))
      scale.domain(Array.from(categoryByName.values()));
      return d => scale(categoryByName.get(d.group));
    }
    return d => scale(d.group);
  }

  let formatDate = d3.utcFormat("%Y")

  const updateBars = bars(svg);
  const updateAxis = axis(svg);
  const updateLabels = labels(svg);
  const updateTicker = ticker(svg);


  async function start_run(){
    for (const keyframe of keyframes) {
      const transition = svg.transition()
          .duration(duration)
          .ease(d3.easeLinear);

      // Extract the top bar’s value.
      x.domain([0, keyframe[1][0].value]);

      updateAxis(keyframe, transition);
      updateBars(keyframe, transition);
      updateLabels(keyframe, transition);
      updateTicker(keyframe, transition);

      await transition.end();
    }
  }
  start_run();


  return (
    <svg id='BarRace'
      ref={ref}
    />
  )
}

export default BarRace;