import React, {useState, useEffect} from 'react';
import MainMenu from './components/MainMenu';
import Footer from './components/Footer';

import intersex from '../static/images/intersex.png'

function DisclaimersGoals(){

  const [movieCounts, setMovieCounts] = useState(null);
  useEffect(() => {
    fetch('/api/movies/count', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'cache-control': 'no-store',
      },
      body: JSON.stringify({
        "groups": {
          'LGBTQIA+ Categories': ['TYPES'],
          'Representations': ['REPRESENTATIONS'],
          'Age': ['AGE'],
        }
      })//this.state.filterCriteria
    }).then(res => res.json()).then(data => {
      setMovieCounts(data)
    })
  }, []);
  
  return (
    <div className='page' id='disclaimers'>
      <MainMenu/>
  
      <div id='proportionalRepresentation'>
        <h2 className='bubbletext'>&#128208;<br/>Representation</h2>
        <p className='description'>
        While creating a searchable archive of queer media was our upmost priority, it also provided us with the unique opportunity to take this tagged, and labelled dataset and perform data analysis. <b>Media representation cannot improve until we truly take stock</b>, and start to understand what marginal groups are so hidden, so forgotten from public consciousness that we do not even perceive them as underrepresented.
        <br/><br/>
        </p>
         
         <div id='intersex'>
          <p>
  Only <b>{movieCounts !== null ? Math.round(movieCounts["Age"]['Senior']/movieCounts['TOTAL']*100*100)/100: '?'}%</b> of media concern Senior Stories (and we are being very generous with our definition of senior here). Our Queer Elders, those that came before us, often faced far greater discrimination, persecution and hardship, and paved the way for our rights today. <b>We pay lip service but do we pay respect?</b><br/><br/> 
          With that being said, understand, while we may report on the relative representation of groups, <b>it is <u>not</u> our stance that proportional representation is the goal</b>. <br/><br/>The statistics we explore do not take into account the underlying presence of marginalised groups in the global or country specific regions. The goal as always is to make sure everyone can feel represented, see authentic stories of their lived experiences, cultural backgrounds, see characters who look like them, live like them, love like them. The argument for strictly proportional representation can hurt as much as it can help, for marginal groups so small in number that such a system would demand near to no media representation at all.
          </p>
          <div>
          <img src={intersex} />
          <p> Some estimates of the rate of intersex births are as low as <b>0.02%–0.05%</b> but we make no such claim that an appropriate level of representation in our dataset would be <b>{movieCounts !== null ? Math.round(movieCounts['TOTAL'] * 0.01 * 0.05*100)/100 : '?'}</b> movies.</p>
          </div>
         </div>
         <br/><br/>
         <p className='description'>We must be wary of artificial responses to the call for a representative queer media space. <br/><b>Capitalism and business will co-opt any political movement they can.</b> </p>
         <div id='portrayals'>
            <p>While problematic portrayals and stories should be criticised, it is difficult to look at any single piece of art, and criticise it for the lack of any single identity. For a diverse, and equitable media space, is not made in a plethora of rainbow movies, overflowing with watered-down and palatable identities. </p><p>We need filmmakers, writers, actors from all walks of life, encouraged and supported, to tell the stories of their communities. There are many steps to this, but awareness of issues in media representation, and diversifying the media one consumes are great ones. </p>
         </div>
         <p className='description'>Our struggles are inter-connected, and regrettable a truly equitable space will not be possible til many of the world's ills are rectified. Our biases, the absences in the stories we tell ourselves, are merely a reflection of those in the real world.</p>
      </div>
   
      <Footer />

    </div>
  )
}

export default DisclaimersGoals

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