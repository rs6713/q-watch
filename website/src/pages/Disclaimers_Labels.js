import React, {useState, useEffect} from 'react';
import MainMenu from './components/MainMenu';
import Footer from './components/Footer';
import { PercentAbsolute} from './components/Delta';

function ListItem({title, subtitle, text, img}){
  return <div className='listItem'>
    {img && <img src={'/icons/' + img} />}
    <h2>{title}</h2>
    {subtitle && <h3>{subtitle}</h3>}
    <p>{text}</p>
  </div>
}

function DisclaimersLabels(){

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
          'Genres': ['GENRES'],
          'Tropes / Triggers': ["TROPE_TRIGGERS"],
          'Representations': ['REPRESENTATIONS'],
          'Age': ['AGE'],
          'Intensity': ['INTENSITY'],
          'Country': ['COUNTRY'],
          'Rep_Trope': ['REPRESENTATIONS', "TROPE_TRIGGERS"],
        }
      })//this.state.filterCriteria
    }).then(res => res.json()).then(data => {
      setMovieCounts(data)
    })
  }, []);

  return (
    <div className='page' id='disclaimers'>
      <MainMenu/>

   

      <div id='identity'>
        <h2 className='bubbletext'>&#127754;<br/>Binarizing Fluids</h2>
        <p className='description'>Human experience, and as such our portrayal of it is complicated; throw in a capitalism-based economy that seeks to profit from artistic expression, the erasure of identity to appeal to a presumed homogeneous audience, or the conditional presence of identities in their most palatable forms, and we ask you to correctly label such movies. <br/><br/><b>We categorized our movies, not because we felt it was always possible to correctly assign a movie a binary label such as country, race, LGBT Identity, but that in doing so would allow the efficient search of such media.</b> Ultimately we want people to be able to experience media that represents them, so we tended to err on the side of inclusion rather than exclusion when it came to designating labels.<br/><br/> With that being said, here are some guidelines and assumptions we determined. This was a work in progress throughout the data collection process, and while we made efforts to retrace our steps and be consistent in these decisions, mistakes may have been made.</p>
        <h3 className='bubbletext'>Disability</h3>
        <div id='Disability'>
          <p>
            One of the tropes we look out for is when disabled roles, are once again taken by an able-bodied, neurotypical actor: <b><i>'Able Playing Disabled'</i></b>. Unfortunately LGBTQIA+ media, like media as a whole is extremely devoid of effective and authentic disability representation. However there are some disabilities like terminal or debilitating conditions e.g. late-stage cancer, dementia, where we felt this trope label was not appropriate. <br/><br/>When we segment 'Mental Health' and 'Disability' it is not as a comment that Mental Health Conditions such as depression, or anxiety cannot be disabling. It is that movies, typically show Mental Health conditions as temporary, with specific causes, that are often cured, or at the very least are not examined through the lens of disability. Furthermore, film producers are still far more willing to portray a finite list of mental health conditions in a "palatable" way than disabiltiies at large.<br/><b>By separating these two labels, we hope to aid queers with disabiltiies find movies that represent them.</b> Movies that present Mental Health Conditions as Disabilities are given both labels.
          </p>
          <PercentAbsolute
              dataset={movieCounts}
              dataChoice='Representations'
              value='Disability'
              statement='Disability'
              substatement={`Percent of LGBTQIA+ Movies with 1+ Characters with a Disability`}
            />
        </div>
        <h3 className='bubbletext'>Race</h3>
        <div id='Race'>
        <b>The racial representation of a movie is determined by the characters, not the actors.</b> If an actor is white presenting, and there is no indication in the movie that their character is anything other than white, whether by name, culture etc, especially when all other characters/actors are white, or the part is small, this movie will not in general appear under QTIPOC labels.Not assigning a movie the QTIPOC label, is not meant as a commentary on the actor's race or ethnicity.  
        <ol><li>For example, Alia Shawkat is an actress of mixed Iraqi, European descent, she has played both white and arabic characters throughout her career. In the movie "The Intervention", she is the only non-white actor in the 8-person production, and plays a character named 'Lola', this movie does not have the QTIPOC label. In 'Duck Butter', she plays one of just two main characters, there are other POC side-characters, she also served as the writer, and her character is named 'Nima', a name of arabic origin. This movie has the QTIPOC label.</li></ol>

        People of mixed heritage, or who are considered "racially ambiguous" often find themselves in the difficult position of being "too other" for white roles but not "[x]" enough for "[x]" roles. It is common for actors to play roles, outside of their race/background, as often studios cast based on "they look like/can pass for" vs "they are".
        
         <br/><br/>At all times, we make the effort to try and understand what was the intended race/ethnicity/cultural background for the POC characters by the movie producers, where this is not possible we default to the race/ethnicity/cultural background of the actor. We do consider these movies on a global scale, and understand racial perception is not a fixed quality. 
         <div>
         <PercentAbsolute
            dataset={movieCounts}
            dataChoice='Representations'
            value='QTIPOC'
            statement='QTIPOC'
            substatement={`Percent of LGBTQIA+ Movies with 1+ QTIPOC Characters`}
          />
          <span>>></span>
          <PercentAbsolute
            dataset={movieCounts}
            dataChoice='Representations'
            value='POC Love'
            statement='POC Love'
            substatement={`Percent of LGBTQIA+ Movies with POC Characters loving POC Characters`}
          />
          <p><b>However simply being on screen is not enough.</b> <br/><br/>We see time and again, that even when QTIPOC characters are on screen they are rarely in company, and if they do have love stories the majority of the time, their partner is white.</p>
         </div>
         </div>
        <h3 className='bubbletext'>Location Location</h3>
        <b>The Country of a Movie is defined as "the primary country the movie took place in".</b> However this does not capture where the movies were produced, the cultural background of the main characters, or which Country financiered the movie. <br/><br/>At time of writing we do not allow a movie to fall under multiple country tags, where a movie takes place in multiple countries, priority is given to the one with the most screentime, symbollic importance or is most representative of the culture of the main characters.<br/><br/> As always there are ambiguities. Films like <i>'Beau Travail'</i> and <i>'The Philosophers'</i> raise interesting questions about where films are based. If a geographic location is completely devoid of its original cultural context, can this movie be said to authentically take place in this country?
        <ol>
          <li><b>Beau Travail</b> - A film about French troops training at a military base in Djibouti, East Africa.</li>
          <li><b>The Philosophers</b> - A film based in Jakarta, Indonesia, concerning an international school comprised of almost entirely American actors</li>
        </ol>

        <h3 className='bubbletext'>LGBT Labelling</h3>
        A lot of earlier lesbian cinema can be argued to fall under the Bisexual label:<ol><li><i>A cis (probably blonde) woman is dating/married to her long term cishet male partner, bored but comfortable, until suddenly a sexy lesbian (probably brunette) rocks up and turns her world upside down.</i></li></ol> However, cheating... can be a bit of a bummer, so to reduce empathy for the male partner, we are encouraged, implicitly or explicitly, to view the woman not as a bisexual but a baby lesbian, just discovering her sexuality, only found to be in this unfortunate situation because of the heternormative society we must endure.<br/> <b>We do not place movies such as this under the Bisexual label, it feels the intent of the movie was not to portray bisexuality, particularly if no character is shown to be enthusiastic to date people of multiple genders.</b>
        <br/><br/>
        We want to avoid the premature labelling of children, who are still in the process of developing their identities as cis or trans, straight or gay. There is room for ambiguity. For example, the movie Tomboy, is intentionally left ambiguous, non-prescriptive, what did this genderplay mean for this pre-pubescent child? Will they grow up to be lesbian? Butch? Transgender? However that does not mean, we cannot label these movies. <br/><br/><b>When we assign a movie a LGBT identity, we are saying people with this sexual identity, gender identity, may see, and feel themselves represented in this movie. </b>As such a movie like Tomboy, may fall under both the Lesbian, and Transgender label, both groups can identify with the experiences explored, whether it being kissing a girl for the first time and knowing you're not supposed to, "cross-dressing" and hiding it from your parents etc.
        <br/><br/><br/><br/>
        <div className='description'><b>As we collect further movies, we are actively exploring refining this labelling system, and commit to incrementally improving it.</b></div>
      </div>
     
   
      <Footer />

    </div>
  )
}

export default DisclaimersLabels

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