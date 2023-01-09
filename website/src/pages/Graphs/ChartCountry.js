import React, { Component, useState, useEffect, useRef} from 'react';
import * as d3 from 'd3';
import Legend from "d3-color-legend"

import * as topojson from 'topojson-client';
import world from '../../static/json/countries-50m.json'

// Copyright 2021 Observable, Inc.
// Released under the ISC license.
// https://observablehq.com/@d3/choropleth
function Choropleth(data, {
  svg,
  id = d => d.id, // given d in data, returns the feature id
  value = () => undefined, // given d in data, returns the quantitative value
  title, // given a feature f and possibly a datum d, returns the hover text
  format, // optional format specifier for the title
  scale = d3.scaleSequentialLog,// d3.scaleSequential, // type of color scale
  domain, // [min, max] values; input of color scale
  range = d3.interpolateBlues, // output of color scale
  width = 640, // outer width, in pixels
  height, // outer height, in pixels
  projection, // a D3 projection; null for pre-projected geometry
  features, // a GeoJSON feature collection
  featureId = d => d.id, // given a feature, returns its id
  borders, // a GeoJSON object for stroking borders
  outline = projection && projection.rotate ? {type: "Sphere"} : null, // a GeoJSON object for the background
  unknown = "#ccc", // fill color for missing data
  fill = "white", // fill color for outline
  stroke = "white", // stroke color for borders
  strokeLinecap = "round", // stroke line cap for borders
  strokeLinejoin = "round", // stroke line join for borders
  strokeWidth, // stroke width for borders
  strokeOpacity, // stroke opacity for borders
} = {}) {
  // Compute values.
  const N = d3.map(data, id);
  const V = d3.map(data, value).map(d => d == null ? NaN : +d);
  const Im = new d3.InternMap(N.map((id, i) => [id, i]));
  const If = d3.map(features.features, featureId);

  // Compute default domains.
  if (domain === undefined) domain = d3.extent(V);
  console.log('Domain: ', domain, ' Range: ', range)
  // Construct scales.
  const color = scale(domain, range);
  if (color.unknown && unknown !== undefined) color.unknown(unknown);

  // Compute titles.
  if (title === undefined) {
    format = color.tickFormat(100, format);
    title = (f, i) => `${f.properties.name}\n${format(V[i])}`;
  } else if (title !== null) {
    const T = title;
    const O = d3.map(data, d => d);
    title = (f, i) => T(f, O[i]);
  }

  // Compute the default height. If an outline object is specified, scale the projection to fit
  // the width, and then compute the corresponding height.
  if (height === undefined) {
    if (outline === undefined) {
      height = 400;
    } else {
      const [[x0, y0], [x1, y1]] = d3.geoPath(projection.fitWidth(width, outline)).bounds(outline);
      const dy = Math.ceil(y1 - y0), l = Math.min(Math.ceil(x1 - x0), dy);
      projection.scale(projection.scale() * (l - 1) / l).precision(0.2);
      height = dy;
    }
  }

  // Construct a path generator.
  const path = d3.geoPath(projection);

  if (outline != null) svg.append("path")
      .attr("fill", fill)
      .attr("stroke", "currentColor")
      .attr("d", path(outline));

  svg.append("g")
    .selectAll("path")
    .data(features.features)
    .join("path")
      .attr("fill", (d, i) => color(V[Im.get(If[i])]))
      .attr("d", path)
    .append("title")
      .text((d, i) => title(d, Im.get(If[i])));

  if (borders != null) svg.append("path")
      .attr("pointer-events", "none")
      .attr("fill", "none")
      .attr("stroke", stroke)
      .attr("stroke-linecap", strokeLinecap)
      .attr("stroke-linejoin", strokeLinejoin)
      .attr("stroke-width", strokeWidth)
      .attr("stroke-opacity", strokeOpacity)
      .attr("d", path(borders));

  return Object.assign(svg.node(), {scales: {color}});
}

const ChartCountry = ({dataset, value_var}) => {
  const ref = useRef();

  let graphContainer;
  var graphStyle;


  const [SVGdimensions, setSVGdimensions] = React.useState({ 
    minHeight: 0,
    width: 0
  })

  React.useEffect(() => {
    graphContainer = document.getElementsByClassName('Graph')[0];
    graphStyle = getComputedStyle(graphContainer);
    function handleResize() {

      var paddingX = parseFloat(graphStyle.paddingLeft) + parseFloat(graphStyle.paddingRight);
      var paddingY = parseFloat(graphStyle.paddingTop) + parseFloat(graphStyle.paddingBottom);

      setSVGdimensions({
        minHeight: graphContainer.clientHeight - paddingY,
        width: graphContainer.clientWidth - paddingX
      })
    }
    window.addEventListener('resize', handleResize)
    handleResize();

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
  
    // let grouped_data = [
    //   {'name': 'United Kingdom', [value_var]: 10}
    // ]
    // console.log(dataset)
    console.log(new Set(dataset.map(d => d.COUNTRY)))
    let rename = {
      'United States': 'United States of America'
    }
    let grouped_data = Array.from(d3.rollup(dataset, d => d.map(m => value_var !== 'COUNT' ? m[value_var]: 1).reduce((a, b)=> a+b), d => d.COUNTRY)).map(
      ([country, total]) => ({'name': (rename[country] || country), 'value': total})
    )
    console.log(grouped_data)
  
    let countries = topojson.feature(world, world.objects.countries)
    let countrymesh = topojson.mesh(world, world.objects.countries, (a, b) => a !== b)

    let chart = Choropleth(grouped_data, {
      svg,
      id: d => d.name, // country name, e.g. Zimbabwe
      value: d => d.value, // health-adjusted life expectancy
      range: d3.interpolateYlGnBu,
      features: countries,
      featureId: d => d.properties.name, // i.e., not ISO 3166-1 numeric
      borders: countrymesh,
      projection: d3.geoEqualEarth(),// d3.geoMercator(),// 
      width: SVGdimensions['width']
    })
    //chart.scales.color
    // console.log( Legend(chart.scales.color, {title: "Number of Movies"}))
    // let key = Legend(chart.scales.color, {title: "Number of Movies"})
    // //console.log(key)

    return _ => {
      window.removeEventListener('resize', handleResize)
    }
  }, [value_var, dataset])


  return (
    <svg id='ChartCountry'
      ref={ref}
    />
  )
}

export default ChartCountry;