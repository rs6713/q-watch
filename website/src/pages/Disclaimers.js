import React from 'react';
import MainMenu from './components/MainMenu';
import Footer from './components/Footer';

function ListItem({title, subtitle, text, img}){
  return <div className='listItem'>
    {img && <img src={'/icons/' + img} />}
    <h2>{title}</h2>
    {subtitle && <h3>{subtitle}</h3>}
    <p>{text}</p>
  </div>
}

function Disclaimers(){
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
            title={<a target='_blank' href='https://queerfilmreviews.com/'>Queer Film Reviews</a>}
            subtitle='Queer Film Reviews'
            img='queer_film.webp'
            text="Michael is the real MVP, amassing 1000's of reviews of queer and gay-themed films, shorts, series, and more. A self-confessed cinephile he'll let you know which ones are worth watching – and which ones aren’t"
            />
          <ListItem
            title={<a target='_blank' href='https://whatson.bfi.org.uk/flare/Online/default.asp'>BFI Flare</a>}
            subtitle='London LGBTIQ+ Film Festival'
            img='bfi_flare.jpg'
            text='BFI Flare not only documents so many diverse feature-length and short films, through the BFI Player, many can be watched for relatively low prices.'
            />
            <ListItem
            img='lesbianflag.jpg'
            title={<a target='_blank' href='https://docs.google.com/spreadsheets/d/1ceuNsDgm5M6q82zvw_Q-o6LGiZGNE_FglgGrJhvwmTo/'>Ultimate Lesbian Film List</a>}
            subtitle='Excel sheet of 100s Lesbian Movies'
            text='We stand on the shoulders of giants. This list was invaluable in identifying lesser known lesbian movies from times by-gone, recorded by a fellow devotee'
            />
            <ListItem
            title='AutoStraddle'
            subtitle='Lesbian & Trans Centered Online Magazine'
            img='autostraddle.png'
            text='Autostraddle is a formerly independently owned online magazine and social network for lesbian, bisexual, and queer women, as well as non-binary people and trans people of all genders.'
            />
            <ListItem
            title='CinemaGoer'
            subtitle='IMDB Open-Source Scraper'
            img='cinemagoer.png'
            text='Cinemagoer (previously known as IMDbPY) is a Python package for retrieving and managing the data of the IMDb movie database about movies and people.'
            />
            <ListItem
            title='Pecadillo on Demand'
            subtitle='LGBT Streaming'
            img='pecadillo.png'
            text='PeccadilloPOD is the online streaming home of award winning independent film publisher Peccadillo Pictures. Stream LGBTQ+ films and international cinemas.'
            />
            <ListItem
              title={<a href='https://sesamebutdifferent.com/blogs/chia-poppys-corner/ultimate-list-of-lesbian-movies-to-watch' target='_blank'>Sesame But Different</a>}
              subtitle='Lesbian Couple Run Blog, Art, Business'
              img='sesame_but_different.png'
              text='Starting as a lesbian slice-of-life comic, about their real life relationship, now they create unique one-of-a-kind LGBT greetings cards. They also took the time to create an Ultimate List of Lesbian Movies.'
            />
            <ListItem
              title={<a href='https://teddyaward.tv/en/' target='_blank'>Teddy Awards</a>}
              subtitle='International LGBT Film Award'
              img='logo_teddy.png'
              text='The Teddy Award is an Berlin International film award for films with LGBT topics, highlighting LGBT movies from a diverse range of cultural backgrounds.'
            />
        </div>
        <h3>The Lists</h3>
        <ul>
          <li>
            <h3></h3><a 
              href='https://www.timeout.com/film/the-50-best-gay-movies-the-best-in-lgbt-film-making'
              target = '_blank'
              >Timeout - Top 50 Best Films in LGBT Film Making</a>
          </li>
          <li>
            <h3></h3><a href='https://www.autostraddle.com/autostraddle-encyclopedia-of-cinema/'
            target='_blank'
            >Autostraddle - The Autostraddle Encyclopedia of Lesbian Cinema
            </a>
          </li>
          <li>
            <h3></h3><a href='https://www.autostraddle.https://www.autostraddle.com/100-best-lesbian-queer-bisexual-movies-285412//autostraddle-encyclopedia-of-cinema/'
            target='_blank'
            >Autostraddle - The 50 Best Lesbian Movies Of All Time
            </a>
          </li>
          <li>
            <h3></h3><a href='https://editorial.rottentomatoes.com/guide/best-lgbt-movies-of-all-time/'
            target='_blank'
            >Rotten Tomatoes - 200 Best LGBT Movies of all time
            </a>
          </li>
          <li>
            <h3></h3><a href='https://www.bfi.org.uk/lists/30-best-lgbt-films-all-time'
            target='_blank'
            >British Film Institute - The 30 Best LGBTQ+ Films of All Time
            </a>
          </li>
          <li>
            <h3></h3><a href='https://www.esquire.com/entertainment/movies/g3392/best-gay-lgbt-movies-of-all-time/'
            target='_blank'
            >Esquire - The 58 Best LGBTQ Movies Ever Made
            </a>
          </li>
        </ul>

      </div>
      <div id='dataIssues'>
        <h2 className='bubbletext'>&#128190;<br/>Data Error</h2>

        <p>This dataset was generated in a semi-automated fashion using a combination of web-scraping and manual data entry. As such we encountered the following issues:
          <ol>
            <li>Due to time constraints it was not possible for every movie to be watched before it was categorised. </li>
            <li>Information for old or indie-production movies would often have less data available online to aid categorization. </li>
          </ol>
          <h3>Apologizing Alreadyyy</h3>
          We tried our best but please, if you see a TAG/ Descriptor that seems innappropriate, it probably was a mistake, either by data or entry error, please let us know and email us at <b>qwatch.gmail.com</b></p>
          <p>If you take issue with any of our labels, terminologies, we welcome feedback. Although please bear in mind, there is variety of thought in any political space, for instance one of our labels for movie representation is 'Plus Sized' while many in the community have proudly reclaimed the term 'Fat', we did not feel it was fair for us to make that choice for everyone.</p>
      </div>
      tropes triggers - able playing disabled...
      <div id='identity'>
        <h2 className='bubbletext'>&#127754;<br/>Binarizing Fluids</h2>
        <p>Human experience, and as such our portrayal of it is complicated; throw in a capitalism-based economy that seeks to profit from artistic expression, the absence or erasure of identity to appeal to a presumed homogeneous audience, or the conditional presence of identities in their most palatable forms, and we ask you to correctly label such movies. We categorized our movies, not because we felt it was always possible to correctly assign a movie a binary label such as country, race, representation, but that in doing so would allow the efficient search of such media. Ultimately we want people to be able to experience media that represents them, so we tended to err on the side of inclusion rather than exclusion when it came to designating labels. With that being said, here are some guidelines and assumptions we determined. This was a work in progress throughout the data collection process, and while we made efforts to retrace our steps and be consistent in these decisions, mistakes may have been made.</p>

        <h3>Race</h3>
        The racial representation of a movie is determined by the characters, not the actors. If an actor is white presenting, and there is no indication in the movie that their character is anything other than white, especially when all other characters are white, this movie will not appear under QTIPOC labels. We do consider these movies on a global scale, and understand racial perception is not a fixed quality,. People of mixed heritage, or who are "racially ambiguous" often find 
        <h3>Location Location</h3>
        The Country of a Movie is defined as "the primary country the movie took place in". It does not capture where the movies were produced, the cultural background of the main characters, or which Country financiered the movie. <br/><br/>At time of writing we do not allow a movie to fall under multiple country tags, where a movie takes place in multiple countries, priority is given to the one with the most screentime, symbollic importance or is most representative of the culture of the main characters.<br/><br/> As always there are ambiguities. Films like 'Beau Travail' and 'The Philosophers' raise interesting questions about where films are based. If a geographic location is completely devoid of its original cultural context, can this movie be said to take place in this country?
        <ol>
          <li><b>Beau Travail</b> - A film about French troops training at a military base in Djibouti, East Africa.</li>
          <li><b>The Philosophers</b> - A film based in Jakarta, Indonesia, concerning an international school comprised of almost entirely American actors</li>
        </ol>

        <h3>LGBT Labelling</h3>
        A lot of earlier lesbian cinema can be argued to fall under the Bisexual label. A cis (probably blonde) woman is dating/married to her long term male partner, bored but comfortable, until suddenly a sexy brunette rocks up and turns her world upside down. However, cheating, can be a bit of a bummer, so to reduce empathy for the male partner, we are encouraged implicitly or explicitly to view the woman not as a bisexual but a baby lesbian, just discovering her sexuality, only found to be in this unfortunate situation because of the heternormative society we must endure. We do not place movies such as this under the Bisexual label, if no character is shown to be capable and enthusiastic to date people of multiple genders.

        We want to avoid the premature labelling of children, who are still in the process of developing their identities as trans, lesbian or gay. For example, the movie Tomboy, is intentionally left ambiguous, non-prescriptive, what did this genderplay mean for this pre-pubescent child? Will they grow up to be lesbian? Butch? Transgender? However that does not mean, we cannot label these movies. When we assign a movie a LGBT Category, we are saying people with this sexual identity, trans identity, may see, and feel themselves represented in this movie. As such a movie like Tomboy, may fall under both the Lesbian, and Transgender label, both groups can identify with the experiences explored, whether it being kissing a girl for the first time and knowing you're not supposed to, cross-dressing and hiding it from your parents etc.
      </div>
      <div id='proportionalRepresentation'>
        <h2 className='bubbletext'>&#128208;<br/>Proportional Rep??</h2>
        While creating a searchable archive of queer media was our upmost priority, what it also did was provide us with a unique opportunity to take this tagged, and labelled dataset and perform data analysis. Media representation cannot improve until we truly take stock, and understand what marginal groups are so hidden, so forgotten from public consciousness that we do not even perceive them as an underrepresented group in the face of such a lack of representative media.<br/><br/> With that being said, understand, while we may report on the relative representation of groups, it is not our stance that proportional representation is the goal. These statistics do not take into account underlying presence of marginalised group in the global or country specific regions that we are considering. 
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