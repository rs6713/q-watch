import React from 'react';
import { useEffect, useState } from 'react';
import * as d3 from 'd3';
import Footer from './components/Footer'
import PieChart from './Graphs/PieChart'
import ChartLine from './Graphs/ChartLine';
import ChartBar from './Graphs/ChartBar';
import MainMenu from './components/MainMenu';
import styles from '../scss/defaults.scss';
import {PercentDelta, PercentAlert, thresholdStatement, PercentAbsolute, Absolute} from './components/Delta';
import {
  getLowestXValues,
  getLowestXValuesAgg,
  getLowestXValueKeys,
  getMaxValueKey,
  getMaxValue,
  getHighestXValues,
  getHighestXValuesAgg,
  getHighestXValueKeys,
  getMaxKey,
  groupDataAgg,
} from './data/utils'

function getWindowDimensions() {
  const { innerWidth: pageWidth, innerHeight: pageHeight } = window;
  return {
    pageWidth, pageHeight
  };
}

function useWindowDimensions() {
  const [windowDimensions, setWindowDimensions] = useState(getWindowDimensions());

  useEffect(() => {
    function handleResize() {
      setWindowDimensions(getWindowDimensions());
    }

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return windowDimensions;
}

function StateOfQueerCinema(){
  const [movies, setMovies] = useState(null);
  const [movieTotal, setMovieTotal] = useState(null);
  const [movieCounts, setMovieCounts] = useState(null);

  const { pageHeight, pageWidth } = useWindowDimensions();

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
          'Year_Type': ['TYPES', 'YEAR'],
          'Tags': ['TAGS'],
          'Year': ['YEAR'],
        }
      })//this.state.filterCriteria
    }).then(res => res.json()).then(data => {
      setMovieCounts(data)
    })
  }, []);

  useEffect(() => {
  fetch('/api/movies', {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'cache-control': 'no-store',
    },
    body: JSON.stringify({
      "properties": [
        'TITLE', 'YEAR', 'COUNTRY', 'BOX_OFFICE_USD', 'BUDGET_USD',
        'TYPES', 'GENRES', 'REPRESENTATIONS', 'TROPE_TRIGGERS'
      ]
    })//this.state.filterCriteria
  }).then(res => res.json()).then(data => {
    setMovies(data["data"]);
    setMovieTotal(data["n_matches"]);
  })
}, [])

  let maxYear = movieCounts !== null ? Math.max(...Object.keys(movieCounts['Year'])) : -1

  const countryBoxOffice = movies? groupDataAgg(movies, ['COUNTRY'], {
    val:'BOX_OFFICE_USD',
    returnType:'dict'}
  ): null;
  const countryBudget = movies? groupDataAgg(movies, ['COUNTRY'], {
    val:'BUDGET_USD',
    returnType:'dict'
  }): null;
  const tropePercent = movies? (Math.round((movies.map(m => m['TROPE_TRIGGERS'] == null ? 1: 0).reduce((a,b) => a+b, 0) / movies.length * 100))) : '?';

  let chartBarLimit = pageWidth < styles.WIDTH_MOBILE ? 10 : (pageWidth < styles.WIDTH_TABLET ? 20 : 30);

  return (
    <div id='Overview' className='page'>
      {/* <div id='Race' className='block'>
        
        <PercentAlert dataset={movieCounts} dataChoice='Representations' value='QTIPOC' statement={thresholdStatement(50)}/>
        <PercentAlert dataset={movieCounts} dataChoice='Representations' value='Plus-Sized' statement={thresholdStatement(50)}/>
        <PercentAlert dataset={movieCounts} dataChoice='Representations' value='POC Love' statement={thresholdStatement(50)}/>
      </div> */}
      <MainMenu/>
      <div id='Types'>
        <h3 className='bubbletext'>&#127752;<br/>Somewhere</h3>
        <div className='stats'>
        <PercentAbsolute
            dataset={movieCounts}
            dataChoice='LGBTQIA+ Categories'
            value='Gay'
            statement='Gay'
            substatement='% of Movies featuring Gay Characters/Stories'
          />
          <PercentAbsolute
            dataset={movieCounts}
            dataChoice='LGBTQIA+ Categories'
            value='Lesbian'
            statement='Lesbian'
            substatement='% of Movies featuring Lesbian Characters/Stories'
          />
          
          <PercentAbsolute
            dataset={movieCounts}
            dataChoice='LGBTQIA+ Categories'
            value='Transgender'
            statement='Transgender'
            substatement='% of Movies featuring Transgender Characters/Stories'
          />
          <PercentAbsolute
            dataset={movieCounts}
            dataChoice='LGBTQIA+ Categories'
            value='Polyamory'
            statement='Polyamory'
            substatement='% of Movies featuring Polyamorous Characters/Stories'
          />
          <PercentAbsolute
            dataset={movieCounts}
            dataChoice='LGBTQIA+ Categories'
            value='Ace/Aro'
            statement='Aro/Ace'
            substatement='% of Movies featuring Aro/Ace Characters/Stories'
          />
          <PercentAbsolute
            dataset={movieCounts}
            dataChoice='LGBTQIA+ Categories'
            value='Intersex'
            statement='Intersex'
            substatement='% of Movies featuring Intersex Characters/Stories'
          />
        </div>
        <div className='sidegraphs'>
         {movies && 
          <ChartBar limit={chartBarLimit} dataset={{
            'data': groupDataAgg(movies, [ 'TYPES']),
            'xLabel': 'LGBTQIA+ Categories',
            'yLabel': 'Total Movies',
            'x': 'TYPES',
            'y': 'VALUE',
            'z': ['TYPES']
          }}></ChartBar>
          }
          {movies && 
            <ChartLine dataset={{
              'data': groupDataAgg(movies, ['YEAR', 'TYPES']),
              'xLabel': 'Date',
              'yLabel': 'Total Movies',
              'x': 'YEAR',
              'y': 'VALUE',
              'z': ['TYPES'],
              'agg': 'cumulative'
            }} xDomain={[1980, Math.max(...movies.map(m=> parseInt(m.YEAR)))]}></ChartLine>
          }
        </div>
      </div>
      <div id='Geography'>
        <h3 className='bubbletext'>&#127758;<br/>¿Dónde están?</h3>
        <div className='stats'>
          <PercentAbsolute
            dataset={movieCounts}
            dataChoice='Country'
            value='United States'
            statement='United States'
            substatement='By far the most common country LGBTQIA+ movies take place in is the United States'
          />
          <PercentAbsolute
            dataset={movieCounts}
            dataChoice='Country'
            value={movieCounts && getHighestXValueKeys(movieCounts['Country'], 5)}
            statement='Top Five'
            substatement={movieCounts? `The majority of LGBTQIA+ movies take place in: ${getHighestXValueKeys(movieCounts['Country'], 5).join(', ')}.` : ''}
          />
          <PercentAbsolute
            dataset={movieCounts}
            dataChoice='Country'
            value={movieCounts && getLowestXValueKeys(movieCounts['Country'], 20)}
            statement='Ignored World'
            substatement={movieCounts && `The bottom 20/${Object.keys(movieCounts['Country']).length} countries (w/ 1+ movies) make up a fraction of the overall representation.`}
          />
          <PercentAbsolute
            dataset={{'Country': countryBoxOffice}}
            dataChoice='Country'
            value={getHighestXValueKeys(countryBoxOffice, 5)}
            statement='Top Five $'
            substatement={movies && `The majority of LGBTQIA+ movies Box Office come from: ${getHighestXValueKeys(countryBoxOffice, 5).join(', ')}.`}
          />
          <PercentAbsolute
            dataset={{'Country': countryBudget}}
            dataChoice='Country'
            value={getHighestXValueKeys(countryBudget, 5)}
            statement='Top Five $'
            substatement={movies && `The majority of LGBTQIA+ movies Budget come from: ${getHighestXValueKeys(countryBudget, 5).join(', ')}.`}
          />
          <Absolute
            value={movieCounts && (
              Math.round(Object.values(movieCounts['Country']).filter(v => v < movieCounts['Country']['Space']).length / Object.keys(movieCounts['Country']).length * 100) + '%')
            }
            statement='Space Dominance'
            substatement={movieCounts && `More movies take place in space, than in ${Object.values(movieCounts['Country']).filter(v => v < movieCounts['Country']['Space']).length}/${Object.keys(movieCounts['Country']).length} countries with 1+ LGBTQIA+ movies.`}
          />
        </div>
        {movies && 
          <ChartBar dataset={{
            'data': groupDataAgg(movies, ['COUNTRY']),
            'xLabel': 'Country',
            'yLabel': 'Total Movies',
            'x': 'COUNTRY',
            'y': 'VALUE',
            'z': ['COUNTRY']
          }} limit={chartBarLimit} yType={d3.scaleLog} xHighlight={['Space']}></ChartBar>
          }
         {/* TODO Stack area plot of continents over time */}
      </div>
      <div id='Temporal'>
        <h3 className='bubbletext'>&#8987;<br/>Time After Time</h3>
        <div className='stats'>
          <Absolute
            value={movieCounts && movieCounts['Year'][getMaxKey(movieCounts['Year'])]}
            statement={'This Year'}
            substatement={movieCounts && `Movies released so far this year (${getMaxKey(movieCounts['Year'])})`}
          />
          <PercentAbsolute
            dataset={movieCounts}
            dataChoice='Year'
            value={Array.from(Array(10).keys()).map(i => maxYear - i)}
            statement='Last 10 Years'
            substatement={`Percent of LGBTQIA+ Movies released in the last 10 years ${maxYear-10}-${maxYear}`}
          />
          <Absolute
            value={movieCounts && getMaxValue(movieCounts['Year'])}
            statement={movieCounts ? ('Peak ' + getMaxValueKey(movieCounts['Year'])) : 'Biggest Year'}
            substatement={movieCounts ? `Most Movies Released in any one Year`: null}
          />

        </div>
        {/* xDomain={[1980, Math.max(...movies.map(m=> parseInt(m.YEAR)))]} */}
        <div className='sidegraphs'>
          {movies && 
              <ChartLine dataset={{
                'data': groupDataAgg(movies, ['YEAR']),
                'xLabel': 'Year',
                'yLabel': 'Total Movies',
                'x': 'YEAR',
                'y': 'VALUE',
                'agg': 'cumulative'
              }} ></ChartLine>
            }
            {movies && 
              <ChartLine dataset={{
                'data': groupDataAgg(movies, ['YEAR']),
                'xLabel': 'Year',
                'yLabel': 'Movies Released Each Year',
                'x': 'YEAR',
                'y': 'VALUE',
              }} ></ChartLine>
            }
        </div>
      </div>
      <div id='Representations'>
        <h3 className='bubbletext'>&#x270a;<br/>Representttt</h3>
        <div className='stats'>
          <PercentAbsolute
            dataset={movieCounts}
            dataChoice='Representations'
            value='Black Love'
            statement='Black Love'
            substatement={`Percent of LGBTQIA+ Movies that feature Black Love`}
          />
          <PercentAbsolute
            dataset={movieCounts}
            dataChoice='Representations'
            value='POC Love'
            statement='POC Love'
            substatement={`Percent of LGBTQIA+ Movies that feature POC Love`}
          />
          <PercentAbsolute
            dataset={movieCounts}
            dataChoice='Representations'
            value='QTIPOC'
            statement='QTIPOC'
            substatement={`Percent of LGBTQIA+ Movies with 1+ QTIPOC characters`}
          />
          <PercentAbsolute
            dataset={movieCounts}
            dataChoice='Representations'
            value='Plus-Sized'
            statement='Plus-Sized'
            substatement={`Percent of LGBTQIA+ Movies with 1+ Plus-Sized characters`}
          />
          <PercentAbsolute
            dataset={movieCounts}
            dataChoice='Age'
            value='Senior'
            statement='Senior'
            substatement={`Percent of LGBTQIA+ Movies with Characters 50+ in age.`}
          />
          <PercentAbsolute
            dataset={movieCounts}
            dataChoice='Age'
            value='Childhood'
            statement='Childhood'
            substatement={`Percent of LGBTQIA+ Movies with Characters < 13 in age.`}
          />
          <PercentAbsolute
            dataset={movieCounts}
            dataChoice='Representations'
            value='Disability'
            statement='Disability'
            substatement={`Percent of LGBTQIA+ Movies with 1+ Characters with Disabilities`}
          />
          <PercentAbsolute
            dataset={movieCounts}
            dataChoice='Representations'
            value='Muslim'
            statement='Muslim'
            substatement={`Percent of LGBTQIA+ Movies with 1+ Muslim Characters`}
          />
          <PercentAbsolute
            dataset={movieCounts}
            dataChoice='Representations'
            value='Jewish'
            statement='Jewish'
            substatement={`Percent of LGBTQIA+ Movies with 1+ Jewish Characters`}
          />

        </div>
        <div className='sidegraphs'>
          {movies && 
              <ChartBar dataset={{
                'data': groupDataAgg(movies, ['REPRESENTATIONS']),
                'xLabel': 'Representation',
                'yLabel': 'Total Movies',
                'x': 'REPRESENTATIONS',
                'y': 'VALUE',
                'z': ['REPRESENTATIONS'],
              }}  limit={chartBarLimit}></ChartBar>
            }
          {movies && 
              <ChartLine dataset={{
                'data': groupDataAgg(movies, ['YEAR', 'REPRESENTATIONS']),
                'xLabel': 'Date',
                'yLabel': 'Total Movies',
                'x': 'YEAR',
                'y': 'VALUE',
                'z': ['REPRESENTATIONS'],
                'agg': 'cumulative'
              }} xDomain={[1980, Math.max(...movies.map(m=> parseInt(m.YEAR)))]}></ChartLine>
            }
          </div>
          {/*line plot of percent representations in yearly released movies over time*/}
      </div>
      <div id='Sadness'>
        <h3 className='bubbletext'>&#128546;&#129297;<br/>Selling Sadness</h3>
        <p className='description'>
          <b>According to Hollywood, our favourite thing is to pay to be re-traumatized.</b><br/><br/>Only <b>{tropePercent}%</b> of movies are without a trope/trigger warning. If Media Becomes Reality, and so much of a person's identity can become based on the stories they are told about people like them. What does this mean for the health of our community?
        </p>
        <div className='stats'>
          <Absolute
            value={movieCounts && movieCounts['Tropes / Triggers']['Suicide/SH']}
            statement='Suicide'
            substatement="Movies where LGBTQIA+ characters die by suicide, self-harm, or struggle with suicidal ideation."
          />
          <Absolute
            value={movieCounts && movieCounts['Tropes / Triggers']['Unaccepting Family']}
            statement='Unaccepting Family'
            substatement="If I weren't me, I'd disown me too.."
          />
          <Absolute
              value={movieCounts && movieCounts['Tags']['AIDS']}
              statement='AIDS'
              substatement='Movies starring characters with AIDS and discussing the wider epidemic.'
            />
            <Absolute
            value={movieCounts && movieCounts['Tags']['Prison/Madhouse/Camp']}
            statement='Imprisioned'
            substatement='Movies starring LGBTQIA+ characters that are imprisioned in prisons, madhouses or concentration camps.'
          />
          <Absolute
            value={movieCounts && movieCounts['Tags']['Conversion Therapy']}
            statement='Conversion Therapy'
            substatement='Movies discussing people placed into Conversion Therapy Programmes.'
          />
        </div>

        {/* {movies && 
            <ChartLine dataset={{
              'data': groupDataAgg(movies, ['YEAR', 'TROPE_TRIGGERS']).filter(
                d => ['Suicide/SH', 'Hate Crimes', 'Bury your gays',  'Gore/Murder'].indexOf(d['TROPE_TRIGGERS']) != -1
              ),
              'xLabel': 'Date',
              'yLabel': 'Total Movies',
              'x': 'YEAR',
              'y': 'VALUE',
              'z': ['TROPE_TRIGGERS'],
            }} xDomain={[1950, Math.max(...movies.map(m=> parseInt(m.YEAR)))]}></ChartLine>
          }
          {movies && 
            <ChartLine dataset={{
              'data': groupDataAgg(movies, ['YEAR', 'TROPE_TRIGGERS']).filter(
                d => [ 'Underaged Partner','Teacher/Student', 'Domestic Abuse'].indexOf(d['TROPE_TRIGGERS']) != -1
              ),
              'xLabel': 'Date',
              'yLabel': 'Total Movies',
              'x': 'YEAR',
              'y': 'VALUE',
              'z': ['TROPE_TRIGGERS'],
            }} xDomain={[1950, Math.max(...movies.map(m=> parseInt(m.YEAR)))]}></ChartLine>
          } */}
      </div>
      <div id='LoveIt'>
        <h3 className='bubbletext'>&#128674;<br/>Ships that Ship</h3>
        <p className='description'>
          <b>What love stories are we telling ourselves?</b><br/><br/>
          We don't know how many LGBT movies we've watched and said to ourselves, "I'm just gonna pretend they decided the character was 18, (and Armie Hammer looks 23 and not like the 30 year old man that he most definitely is)", but probably toooo many.
        </p>
        <div className='stats'>
          <Absolute
            value={movieCounts && movieCounts['Tags']['Happy Ending']}
            statement='Happy Endings'
            substatement='LGBTQIA+ Movies with Significant Happy Endings'
          />
          <Absolute
            value={movieCounts && movieCounts['Tags']['Sad Ending']}
            statement='Sad Endings'
            substatement='LGBTQIA+ Movies with Significant Sad Endings'
          />
          <Absolute
            value={movieCounts && movieCounts['Tags']['Age Gap Relationship']}
            statement='Glucose Guardians'
            substatement='LGBTQIA+ Movies with Significant Age Gaps'
          />

          <Absolute
            value={movieCounts && movieCounts['Tropes / Triggers']['Teacher/Student']}
            statement='Teacher / Student'
            substatement="Teachers & Student Relationships (statistics are not endorsements)"
          />
          <Absolute
            value={movieCounts && movieCounts['Tags']['Enemies to Lovers']}
            statement='Enemies to Lovers'
            substatement='LGBTQIA+ Movies where enemies become lovers.'
          />
          <Absolute
            value={movieCounts && movieCounts['Tags']['Friends to Lovers']}
            statement='Friends to Lovers'
            substatement='LGBTQIA+ Movies where friends become lovers.'
          />
          
        </div>
      </div>
      <div id='tagged'>
        <h3 className='bubbletext'>&#128125;<br/>Subject Me</h3>
        <p className='description'>
          <b>Queers don't like Action and Adventure. They like Rom-Coms, Photography and the Victorian Era.</b>
          <br/><br/>(Apparently)
        </p>
          <div className='stats'>
            <Absolute
              value={movieCounts && movieCounts['Tags']['Christmas']}
              statement='Christmas'
              substatement='LGBTQIA+ Movies but even whiter than usual.'
            />
            <Absolute
              value={movieCounts && movieCounts['Tags']['Alien / Monsters']}
              statement='Aliens & Monsters'
              substatement='Spoiler: Transphobes were the real monsters all along.'
            />
            <Absolute
              value={movieCounts && movieCounts['Tags']['Activism / Court Case']}
              statement='Activism'
              substatement='Movies that centre activism and legal cases.'
            />
            <Absolute
              value={movieCounts && movieCounts['Tags']['Christianity']}
              statement='Christianity'
              substatement='Movies that feature Christianity.'
            />
            <Absolute
              value={movieCounts && movieCounts['Tags']['True Story / Real People']}
              statement='Bio'
              substatement='Movies based on real people and stories.'
            />
            <Absolute
              value={movieCounts && movieCounts['Tags']['Aristocracy']}
              statement='Royalty'
              substatement='The lesser mentioned way to F*ck the Monarchy.'
            />
            <Absolute
              value={movieCounts && movieCounts['Tags']['Sports']}
              statement='Sports'
              substatement="Let's get hot, dirty and sweaty."
            />
            <Absolute
              value={movieCounts && movieCounts['Tags']['Science']}
              statement='Science'
              substatement='Apparently queers like to experiment &#128064;.'
            />
            <Absolute
              value={movieCounts && movieCounts['Tags']['Drag Queens']}
              statement='Drag Queens'
              substatement="Queens."
            />
          </div>
          {movies && 
          <ChartBar dataset={{
            'data': groupDataAgg(movies, ['GENRES']),
            'xLabel': 'Genres',
            'yLabel': 'Total Movies',
            'x': 'GENRES',
            'y': 'VALUE',
            'z': ['GENRES']
          }} limit={chartBarLimit}></ChartBar>
          }
      </div>


{/* 
        <PercentAlert dataset={movieCounts}
        dataChoice='Country' value={['United States', 'United Kingdom', 'Canada', 'France']} />

        <PercentAlert dataset={movieCounts}
        dataChoice='Age' value='Senior' />
        <PercentAlert dataset={movieCounts}
        dataChoice='Age' value='Childhood' />

        <PercentAlert dataset={movieCounts}
        dataChoice='Genres' value='Sci-Fi/Fantasy' />

<PercentAlert dataset={movieCounts}
        dataChoice='Tropes / Triggers' value='Suicide/SH' />
        <PercentAlert dataset={movieCounts}
        dataChoice='Tropes / Triggers' value='Homophobia' />
        <PercentAlert dataset={movieCounts}
        dataChoice='Tropes / Triggers' value='Death' />
        <PercentAlert dataset={movieCounts}
        dataChoice='Tropes / Triggers' value='Cheating' />
        <PercentAlert dataset={movieCounts}
        dataChoice='Tags' value='Sexual Awakening' />
        <PercentAlert dataset={movieCounts}
        dataChoice='Tags' value='Age Gap Relationship' />

<PercentAlert dataset={transMovieCounts}
        dataChoice='Tropes / Triggers' value='Gore/Murder' />
        <PercentAlert dataset={transMovieCounts}
        dataChoice='Tropes / Triggers' value='Cis Playing Trans' />
        <PercentAlert dataset={transMovieCounts}
        dataChoice='Tropes / Triggers' value='Transphobia' />
        <PercentAlert dataset={transMovieCounts}
        dataChoice='Country' value='United States' qualifier='Over' valueStatement='are based in the United States' />
        <PercentAlert dataset={transMovieCounts} dataChoice='Representations' value='Plus-Sized' />
        <PercentAlert dataset={transMovieCounts} dataChoice='Representations' value='POC Love' />

<PieChart dataset={transMovieCounts} dataChoice={'Tropes / Triggers'}/> */}
      <Footer />
    </div>

  )

}

export default StateOfQueerCinema