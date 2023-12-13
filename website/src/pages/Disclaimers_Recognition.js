import React from 'react';
import MainMenu from './components/MainMenu';
import Footer from './components/Footer';

// Images Required
import queerfilm from '../static/images/queer_film.webp';
import bfi_flare from '../static/images/bfi_flare.jpg';
import lesbian_flag from '../static/images/lesbianflag.jpg';
import autostraddle from '../static/images/autostraddle.png';
import cinemagoer from '../static/images/cinemagoer.png';
import pecadillo from '../static/images/pecadillo.png';
import sesame from '../static/images/sesame_but_different.png';
import teddy from '../static/images/logo_teddy.png';


function ListItem({title, subtitle, text, img, link}){
  return <div className='listItem'>
      
    {img && <img src={img} />}
    <h2>{title}</h2>
    {subtitle && <h3>{subtitle}</h3>}
    <p>{text}</p>
    {link && <a target='_blank' href={link}></a>}
  </div>;

}

function DisclaimersRecognition(){
  return (
    <div className='page' id='disclaimers'>
      <MainMenu/>

      <div id='credit'>
        <h2 className='bubbletext'>&#127942;<br/>Credit Giving</h2>
        <p className='description'>
          We couldn't have done this alone. We are community. We stand on the shoulders of giants. We certainly aren't the first, and won't be the last to create a resource to help our fellow queers query queer content. <br/><br/><b>We would love to be the best-searchable archive of queer content online, but gladly welcome a world where someone else does it better.</b>
        </p>
        <div className='list'>
        
        <ListItem
            title='Queer Film Reviews'
            subtitle='Queer Film Reviews'
            img={queerfilm}
            text="Michael is the real MVP, amassing 1000's of reviews of queer and gay-themed films, shorts, series, and more. A self-confessed cinephile he'll let you know which ones are worth watching – and which ones aren’t"
            link='https://queerfilmreviews.com/'
            />
          <ListItem
            title='BFI Flare'
            subtitle='London LGBTIQ+ Film Festival'
            img={bfi_flare}
            text='BFI Flare not only documents so many diverse feature-length and short films, through the BFI Player, many can be watched for relatively low prices.'
            link='https://whatson.bfi.org.uk/flare/Online/default.asp'
            />
            <ListItem
            img={lesbian_flag}
            title='Ultimate Lesbian Film List'
            subtitle='Excel sheet of 100s Lesbian Movies'
            text='We stand on the shoulders of giants. This list was invaluable in identifying lesser known lesbian movies from times by-gone, recorded by a fellow devotee'
            link='https://docs.google.com/spreadsheets/d/1ceuNsDgm5M6q82zvw_Q-o6LGiZGNE_FglgGrJhvwmTo/'
            />
            <ListItem
            title='AutoStraddle'
            subtitle='Lesbian & Trans Centered Online Magazine'
            img={autostraddle}
            text='Autostraddle is a formerly independently owned online magazine and social network for lesbian, bisexual, and queer women, as well as non-binary people and trans people of all genders.'
            link='https://www.autostraddle.com/'
            />
            <ListItem
            title='CinemaGoer'
            subtitle='IMDB Open-Source Scraper'
            img={cinemagoer}
            text='Cinemagoer (previously known as IMDbPY) is a Python package for retrieving and managing the data of the IMDb movie database about movies and people.'
            link='https://cinemagoer.github.io/'
            />
            <ListItem
            title='Pecadillo on Demand'
            subtitle='LGBT Streaming'
            img={pecadillo}
            text='PeccadilloPOD is the online streaming home of award winning independent film publisher Peccadillo Pictures. Stream LGBTQ+ films and international cinemas.'
            link='https://www.peccadillopod.com/'
            />
            <ListItem
              title='Sesame But Different'
              subtitle='Lesbian Couple Run Blog, Art, Business'
              img={sesame}
              text='Starting as a lesbian slice-of-life comic, about their real life relationship, now they create unique one-of-a-kind LGBT greetings cards. They also took the time to create an Ultimate List of Lesbian Movies.'
              link='https://sesamebutdifferent.com/blogs/chia-poppys-corner/ultimate-list-of-lesbian-movies-to-watch'
            />
            <ListItem
              title='Teddy Awards'
              subtitle='International LGBT Film Award'
              img={teddy}
              text='The Teddy Award is an Berlin International film award for films with LGBT topics, highlighting LGBT movies from a diverse range of cultural backgrounds.'
              link='https://teddyaward.tv/en/'
            />
        </div>

        

      </div>
      <div id='lists'>
        <h2 className='bubbletext'>&#129534;<br/>The Lists</h2>
        <p className='description'>Just make sure you go ahead and credit our list of lists, when you make your list of lists of lists.</p>
        {/* <h3>The Lists</h3> */}
        <ul>
          <li>
            <h3></h3><a 
              href='https://www.timeout.com/film/the-50-best-gay-movies-the-best-in-lgbt-film-making'
              target = '_blank'
              ><span>Timeout</span> - Top 50 Best Films in LGBT Film Making</a>
          </li>
          <li>
            <h3></h3><a href='https://www.autostraddle.com/autostraddle-encyclopedia-of-cinema/'
            target='_blank'
            ><span>Autostraddle</span> - The Autostraddle Encyclopedia of Lesbian Cinema
            </a>
          </li>
          <li>
            <h3></h3><a href='https://www.autostraddle.https://www.autostraddle.com/100-best-lesbian-queer-bisexual-movies-285412//autostraddle-encyclopedia-of-cinema/'
            target='_blank'
            ><span>Autostraddle</span> - The 50 Best Lesbian Movies Of All Time
            </a>
          </li>
          <li>
            <h3></h3><a href='https://editorial.rottentomatoes.com/guide/best-lgbt-movies-of-all-time/'
            target='_blank'
            ><span>Rotten Tomatoes</span> - 200 Best LGBT Movies of all time
            </a>
          </li>
          <li>
            <h3></h3><a href='https://www.bfi.org.uk/lists/30-best-lgbt-films-all-time'
            target='_blank'
            ><span>British Film Institute</span> - The 30 Best LGBTQ+ Films of All Time
            </a>
          </li>
          <li>
            <h3></h3><a href='https://www.esquire.com/entertainment/movies/g3392/best-gay-lgbt-movies-of-all-time/'
            target='_blank'
            ><span>Esquire</span> - The 58 Best LGBTQ Movies Ever Made
            </a>
          </li>
        </ul>
        </div>
      <Footer />

    </div>
  )
}

export default DisclaimersRecognition

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