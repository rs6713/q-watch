import React from 'react';
import MainMenu from './components/MainMenu';
import Footer from './components/Footer';

function Disclaimers(){
  return (
    <div className='page' id='disclaimers'>
      <MainMenu/>
      
      <div id='credit'>
        <h2 className='bubbletext'>Credit Giving</h2>
        Credits
          b4watch
          Cinemagoer
          Ultimate Lesbian Film List
          BFI Flare
          https://sesamebutdifferent.com/
          bfi instistute
          film freeway - festival entry
          https://www.timeout.com/film/the-50-best-gay-movies-the-best-in-lgbt-film-making lists, autostraddle lists.
      </div>
      <div id='dataIssues'>
        <h2 className='bubbletext'>Data Error</h2>

        <p>Disclaimer: This dataset was generated in a semi-automated fashion using a combination of web-scraping and manual data entry. Due to time constraints it was not possible for every movie to be watched before it was categorised. Old or indie-production movies often have less data available online. We tried our best but please, if you see a TAG/ Descriptor that seems innappropriate, it probably was a mistake, let us know and email us at <b>qwatch.gmail.com</b></p>
          <p>If you take issue </p>
      </div>
      <div id='identity'>
        <h3>Binarizing Fluids</h3>
        <h2 className='bubbletext'>Binarizing Fluids</h2>
        Films like Beau Travail and The Philosophers create intereseting questions about where films are based. 
          A military base in Africa filled with french troops Beau Travail
          A fantasy based education exercise where an international school almost entirely American actors
          appearance of children movies under explicit lgbt tags. see the little prince(ss)
      </div>
      <div id='proportionalRepresentation'>
        <h2 className='bubbletext'>Proportional Rep??</h2>

      </div>
      <Footer />
    </div>
  )
}

export default Disclaimers

// function InlineChart(data, {
//   x = ([x]) => x, // given d in data, returns the (temporal) x-value
//   y = ([, y]) => y, // given d in data, returns the (quantitative) y-value
//   z = () => 1, // given d in data, returns the (categorical) z-value
//   defined, // for gaps in data
//   curve = d3.curveLinear, // method of interpolation between points
//   marginTop = 30, // top margin, in pixels
//   marginRight = 50, // right margin, in pixels
//   marginBottom = 30, // bottom margin, in pixels
//   marginLeft = 30, // left margin, in pixels
//   width = 640, // outer width, in pixels
//   height = 400, // outer height, in pixels
//   xType = d3.scaleUtc, // type of x-scale
//   xDomain, // [xmin, xmax]
//   xRange = [marginLeft, width - marginRight], // [left, right]
//   yType = d3.scaleLinear, // type of y-scale
//   yDomain, // [ymin, ymax]
//   yRange = [height - marginBottom, marginTop], // [bottom, top]
//   zDomain, // array of z-values
//   yFormat, // a format specifier string for the labels
//   colors = d3.schemeCategory10, // stroke color of line
//   strokeLinecap = "round", // stroke line cap of the line
//   strokeLinejoin = "round", // stroke line join of the line
//   strokeWidth = 1.5, // stroke width of line, in pixels
//   strokeOpacity = 1, // stroke opacity of line
//   halo = "#fff", // color of label halo 
//   haloWidth = 6 // padding around the labels
// } = {}) {
//   // Compute values.
//   const X = d3.map(data, x);
//   const Y = d3.map(data, y);
//   const Z = d3.map(data, z);
//   if (defined === undefined) defined = (d, i) => !isNaN(X[i]) && !isNaN(Y[i]);
//   const D = d3.map(data, defined);

//   // Compute default domains, and unique the z-domain.
//   if (xDomain === undefined) xDomain = d3.extent(X);
//   if (yDomain === undefined) yDomain = [0, d3.max(Y)];
//   if (zDomain === undefined) zDomain = Z;
//   zDomain = new d3.InternSet(zDomain);

//   // Omit any data not present in the z-domain.
//   const I = d3.range(X.length).filter(i => zDomain.has(Z[i]));

//   // Construct scales and axes.
//   const xScale = xType(xDomain, xRange);
//   const yScale = yType(yDomain, yRange);
//   const color = d3.scaleOrdinal(zDomain, colors);
//   const xAxis = d3.axisBottom(xScale).ticks(width / 80).tickSizeOuter(0);

//   // Construct formats.
//   yFormat = yScale.tickFormat(null, yFormat);

//   // Construct a line generator.
//   const line = d3.line()
//       .defined(i => D[i])
//       .curve(curve)
//       .x(i => xScale(X[i]))
//       .y(i => yScale(Y[i]));

//   const svg = d3.create("svg")
//       .attr("width", width)
//       .attr("height", height)
//       .attr("viewBox", [0, 0, width, height])
//       .attr("style", "max-width: 100%; height: auto; height: intrinsic;");

//   svg.append("g")
//       .attr("transform", `translate(0,${height - marginBottom})`)
//       .call(xAxis);

//   const serie = svg.append("g")
//     .selectAll("g")
//     .data(d3.group(I, i => Z[i]))
//     .join("g");

//   const path = serie.append("path")
//       .attr("fill", "none")
//       .attr("stroke", ([key]) => color(key))
//       .attr("stroke-width", strokeWidth)
//       .attr("stroke-linecap", strokeLinecap)
//       .attr("stroke-linejoin", strokeLinejoin)
//       .attr("stroke-opacity", strokeOpacity)
//       .style("mix-blend-mode", "multiply")
//       .attr("d", ([, I]) => line(I));

//   serie.append("g")
//       .attr("font-family", "sans-serif")
//       .attr("font-size", 10)
//       .attr("text-anchor", "middle")
//       .attr("stroke-linejoin", "round")
//       .attr("stroke-linecap", "round")
//     .selectAll("text")
//     .data(([, I]) => I)
//     .join("text")
//       .attr("dy", "0.35em")
//       .attr("x", i => xScale(X[i]))
//       .attr("y", i => yScale(Y[i]))
//       .text(i => yFormat(Y[i]))
//       .call(text => text
//         .filter((_, j, I) => j === I.length - 1)
//         .append("tspan")
//           .attr("font-weight", "bold")
//           .text(i => ` ${Z[i]}`))
//       .call(text => text.clone(true))
//       .attr("fill", "none")
//       .attr("stroke", halo)
//       .attr("stroke-width", haloWidth);

//   return Object.assign(svg.node(), {scales: {color}})halo;
// }