import React from 'react';
import {useEffect, useState} from 'react';
import ExpandableBubbles from './ExpandableBubbles'
import {ReactComponent as Minus} from '../../static/icons/minus.svg'
import BubbleFilter from './Filters/BubbleFilter';
import SliderFilter from './Filters/SliderFilter';
import DropDownFilter from './Filters/DropdownFilter'
import Loader from './Loader'
import {ReactComponent as Exit} from '../../static/icons/no.svg'

const _ = require("lodash"); 

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
      filters:null,
      switchType: 'include'
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
      filters: null,
      switchType:'include',
      
    },
    {
      title: "Tropes / Trigger Warnings",
      id: "TROPE_TRIGGERS",
      expandable: true,
      warning: "IMPLIED SPOILERS",
      subtitle: "Early mainstream, queer media was messy at best. Select the tropes you wish to avoid.",
      type: "bubble",
      filters:null,
      switchType:'exclude'
    },
    // {
    //   title: "Movie Qualities",
    //   type: 'subfilters',
    //   filters: [
        {
          title: "Age Range",
          id: "AGE",
          dataLabel: 'AGES',
          type: "bubble",
          filters: null, 
          switchType: 'include'
        },
        {
          title: "Intensity",
          id: "INTENSITY",
          dataLabel: 'INTENSITYS',
          type: "slider",
          filters: null,
          onMessage: "I'm a person.... A person with needs",
          offMessage: 'No more than this please. (Think of the children!)'
        },
        {
          title: "Rating",
          id: "AVG_RATING",
          type: "rangeslider",
          filters: _.range(1, 6, 1).map((i) => ({'ID': i})),
          onMessage: "I'd like to 'Ask! The! Audience!'",
          offMessage: "I'm a Garbage boi, nomnom, thankyou for the tasty trash, my favouriteee."
          //range: [0, 210],
          //step: 10,
          //filters: null
        },
        {
          title: "Runtime",
          id: "RUNTIME",
          type: "rangeslider",
          filters: _.range(0, 121, 15).map((i) => ({'ID': i})),
          onMessage: 'Come on... I need time to cuddle',
          offMessage: "What does Sarah Paulson and my attention have in common? I'll never hold them...",
          //turnOffAble: true
          //range: [0, 210],
          //step: 10,
          //filters: null
        },
        {
          title: "Language",
          id: "LANGUAGE",
          dataLabel: 'LANGUAGES',
          type: "dropdown",
          filters: null,
          placeholder: 'Select the Primary Language Characters Speak'
        },
        {
          title: "Country",
          id: "COUNTRY",
          dataLabel: 'COUNTRYS',
          filters: null,
          type: 'dropdown',
          placeholder: 'Select the Primary Country of the Movie'
        },
        {
          title: "Tags",
          id: "TAGS",
          expandable: true,
          warning: "For those particulaarr cravings",
          subtitle: null,
          type: "bubble",
          filters:null,
          switchType:'include'
        },
    //   ]
    // },


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

function Filters({active, nMatches, updateFilters, filters, setActive}){
  /*
  list --> list to filter
  action --> to call with list

  */
  //const [config, setConfig] = useState(null)
  const [labels, setLabels] = useState(null);
  console.log('Received filters: ', filters)
  useEffect(() => {
    fetch('/api/movie/labels').then(res => res.json()).then(data => {
      console.log('Calling api movie labels', Object.keys(data))
      setLabels(data);
    });
  }, []);

  function createActiveFilters(label_id, filter_id){
    let temp_filter = labels[label_id].sort((a, b) => a.ID - b.ID)
    console.log('Temp filter: ', label_id, filters[filter_id], temp_filter)
    var f_ids = [];
    if(filters[filter_id]){
      if(['number', 'string'].indexOf(typeof filters[filter_id])!== -1){
        f_ids = [filters[filter_id]]
      }else if(Array.isArray(filters[filter_id])){
        f_ids = filters[filter_id]
      }else{
        f_ids = filters[filter_id]['VALUE']
      }
      temp_filter = temp_filter.map(f => {
        if(f_ids.indexOf(f.ID) !== -1){
          return {...f, 'active': true}
        }
        return f
      })
    }
    return temp_filter
  }

  function getFilterLabel(filter){
    return Object.keys(filter).indexOf('dataLabel') === -1? filter['id'] : filter['dataLabel']
  }

  let config = null;
  if(labels){
    let temp_config = {...baseConfig, 'filterSections': []}

    for(let section of baseConfig['filterSections']){

      let sectionLabel = getFilterLabel(section)
      if(sectionLabel !== null && Object.keys(labels).indexOf(sectionLabel)!= -1){
        temp_config['filterSections'].push(
          {
            ...section,
            'filters': createActiveFilters(sectionLabel, section['id'])
          }
        )
      }else if(section['type'] === 'subfilters'){
        let filter_section = {...section, 'filters': []}
        
        for(let filter of section['filters']){
          let filterLabel = getFilterLabel(filter);

          // If is slider subfilter with options in data
          if(['slider', 'bubble', 'dropdown'].indexOf(filter['type'])!== -1 && Object.keys(labels).indexOf(filterLabel)!==-1){
            console.log('Sorting ' + filter['type'])
            filter_section['filters'].push(
              {...filter, 'filters': createActiveFilters(filterLabel, filter['id'])}
            )
          }else{
            filter_section['filters'].push(filter)
          }
        }
        temp_config['filterSections'].push(filter_section)
      }else{
        temp_config['filterSections'].push(section)
      }
    }
    
    config = temp_config;
  }

  function generateFilter(filter){
    
    return <div key={filter.title}>
      {filter.type === "bubble" && <BubbleFilter updateFilters={updateFilters} filter={filter}/>}

      {filter.type === "checkbox" &&
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
      { ["slider", "rangeslider"].indexOf(filter.type) !== -1 && filter.filters !== null && <SliderFilter updateFilters={updateFilters} filter={filter} filters={filters} randomIdx={parseInt(Math.random() * 100000)} />}

      {filter.type === 'dropdown' && <DropDownFilter updateFilters={updateFilters} filter={filter} filters={filters}/>}
      {
        filter.type === 'subfilters' && 
          <div className='filterSection'>
            <h2>{filter.title}</h2>
            {filter.filters.map(generateFilter)}
          </div>
      }
    </div>
  }

  if(config === null){
    return (
      <div id="Filters" className={active? "active": "inactive"}>
        
        <h1>{baseConfig.title}</h1>
        <Loader isLoading={true}/>
      </div>
    )
  }


  //<Minus/>
  return (

    <div id="Filters" className={active? "active": "inactive"}>
      
      <h1>
        {config.title}
        <span>({nMatches} Matches)</span>
        <Exit onClick={()=> {setActive(!active)}} />
      </h1>
      <div>
        {config.filterSections.map(generateFilter)}
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