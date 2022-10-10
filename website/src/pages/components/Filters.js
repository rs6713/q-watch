import {useEffect, useState} from 'react';
import ExpandableBubbles from './ExpandableBubbles'
import {ReactComponent as Minus} from '../../static/icons/minus.svg'

const baseConfig = {
  title: "Movie Filters",
  filterSections:[
    // {
    //   title: "By Women for Women",
    //   subtitle: "Sometimes things are best done yourself.",
    //   type: "checkbox",
    //   filters:[
    //     {
    //       label: "Female Director",
    //       id: "female_director",
    //       descrip: "The movie is directed by a woman"
    //     },
    //     {
    //       label: "Female Writer",
    //       id:"female_writer",
    //       descrip: "The movie is written by a woman"
    //     }
    //   ]
    // },
    {
      title: "Movie Types",
      id: "TYPES",
      subtitle: "Take you anywhere under the LGBTQIA2+ rainbow.",
      type: "bubble",
      filters:null
    },
    {
      title: "Movie Qualities",
      filters: [
        {
          label: "Age Range",
          id: "age_range",
          type: "slider",
          options: ["Coming of Age", "Young Adult", "30-60", "60+"]
        },
        {
          label: "Language",
          id: "language",
          type: "dropdown",
        },
      ]
    },
    {
      title: "Tropes / Trigger Warnings",
      id: "TROPE_TRIGGERS",
      expandable: true,
      warning: "IMPLIED SPOILERS",
      subtitle: "Early mainstream, queer media was messy at best. Select the tropes you wish to avoid.",
      type: "bubble",
      filters:null
    },
    {
      title: "Representation Matters",
      id: "REPRESENTATIONS",
      warning: "See yourself on the bigscreen.",
      subtitle: "We have tried our best, but if you feel we are missing filters here, please let us know, email us at q-watch.gmail.com.",
      disclaimers: [
        "Unfortunately some options may be missing or extremely broad, due to a lack of representation in the media itself.",
        "Representation here, guarantees presence, but not good representation: see tropes/trigger warnings."
      ],
      type: "bubble",
      filters: null
    },
    // {
    //   title: "Can't find what you're looking for?",
    //   subtitle: "Unfortunately Queer cinema (like most media) can be majority homogeneous. Allowing these options, may help you find more movies for specific demographics/story types",
    //   type: "checkbox",
    //   filters:[
    //     {
    //       LABEL: "Queer Love can be Side Stories/Characters",
    //       ID: "allowSideCharacters"
    //     },
    //     {
    //       LABEL: "Queerness can be implied (only)",
    //       ID: "allowImplied"
    //     }
    //   ]
    // }
  ]
}

function Filters({active, nMatches, updateFilters, filters}){
  /*
  list --> list to filter
  action --> to call with list

  */
  const [config, setConfig] = useState(baseConfig)
  useEffect(() => {
    fetch('/api/movie/labels').then(res => res.json()).then(data => {
      let temp_config = {...config, 'filterSections': []}
      for(let section of config['filterSections']){
        if(section['id'] !== null && Object.keys(data).indexOf(section['id'])!= -1){
          temp_config['filterSections'].push(
            {...section, 'filters': data[section['id']]}
          )
        }else{
          temp_config['filterSections'].push(section)
        }
      }
      setConfig(temp_config)
    });
  }, [])

  function bubbleSelect(itemId, filter){
    let currentIds = filters[filter['id']] || [];
    // Toggle item in/out of filter list
    if(currentIds.indexOf(itemId) !== -1){
      currentIds.splice(currentIds.indexOf(itemId))
      if(currentIds.length === 0){
        updateFilters({[filter['id']]: null});
      }else{
        updateFilters({[filter['id']]: currentIds});
      }
    }else{
      updateFilters({[filter['id']]: [...currentIds, itemId]})
    }
  }

  //<Minus/>
  return (

    <div id="Filters" className={active? "active": "inactive"}>
      <h1>{config.title} <span>({nMatches} Matches)</span></h1>
      <div>
      
      {config.filterSections.map((filter) => (
        <div key={filter.title}>
          
          {filter.type=="bubble" && 
            <ExpandableBubbles
              title={filter.title}
              aside={filter.warning || ""}
              items={filter.filters}
              clickAction={(itemId) => {bubbleSelect(itemId, filter)}}
              expandable={filter.expandable || false}
              subtitle={filter.subtitle}
            />
          }
          {filter.type=="checkbox" &&
            <div>
              <h2>{filter.title}</h2>
              <p>{filter.subtitle}</p>
              {filter.filters.map(f => (
                <div>
                  <input type="checkbox" id={f.id} name={f.label} value={f.id}></input>
                  <label> {f.label}</label>
                </div>
              ))}
            </div>
          }
        </div>)
      )}
      </div>
    </div>
  )
}

export default Filters;

/*
[
        {
          label: "Teacher/Student",
          id:"teacher_student",
          descrip: "Because it's illegal"
        },
        {
          label: "Lesbian Bed death",
          id: "lesbian_bed_death"
        },
        {
          label: "Bury your gays",
          id: "bury_your_gays"
        },
        {
          label: "Sexual Violence",
          id: "sexual_violence"
        },
        {
          label: "Suicide",
          id: "suicide",
          descrip: ""
        },
        {
          label: "Conversion Therapy",
          id: "conversion_therapy",
          descrip: ""
        },
        {
          label: "Hate Crimes",
          id: "hate_crimes",
          descrip: ""
        },
        {
          label: "They don't end up together.",
          id: "lonely_lesbians",
          descrip: ""
        },
        {
          label: "Unaccepting Family/Disowning",
          id: "family_troubles",
          descrip: ""
        },
        {
          label: "Bi Erasure",
          id: "bi_erasure",
          descrip: ""
        },
        {
          label: "It was just a phase",
          id: "it_was_a_phase",
          descrip: ""
        }
      ]
[
        {
          label: "Black Love",
          id: "blackLove",
          descrip: "Black characters loving black characters."
        },
        {
          label: "POC Love",
          id: "pocLove",
          descrip: "POC characters loving POC characters."
        },
        {
          label: "QTIPOC",
          id: "qtipoc",
          descrip: "At least one of the main characters is POC"
        },
        {
          label: "Transgender",
          id: "transgender",
          descrip: "At least one of the main characters is trans"
        },
        {
          label: "Disability",
          id: "disability",
          descrip: "At least one of the main characters is disabled"
        },
        {
          label: "Butch",
          id: "butch",
          descrip: "At least one of the main characters is butch"
        },
        {
          label: "Bisexual",
          id: "bisexual",
          descrip: "At least one of the main characters is bisexual"
        },
        {
          label: "Polyamory",
          id: "polyamory",
          descrip: "The relationship is polyamorous"
        },
        {
          LABEL: "Jewish",
          ID: "jewish",
          DESCRIP: "At least one of the main characters is jewish"
        }
      ]
*/