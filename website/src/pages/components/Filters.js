import React from 'react';
import ExpandableBubbles from './ExpandableBubbles'
import {ReactComponent as Minus} from '../../static/icons/minus.svg'



function Filters(props){
  /*
  list --> list to filter
  action --> to call with list

  */
  //<Minus/>
  return (

    <div id="Filters" className={props.active}>
      <h1>{props.config.title} <span>({props.n_matches} Matches)</span></h1>
      <div>
      
      {props.config.filterSections.map((filter) => (
        <div >
          
          {filter.type=="bubble" && 
            <ExpandableBubbles 
              title={filter.title}
              aside={filter.warning || ""}
              items={filter.filters}
              clickAction={filter.clickAction || (()=>{}) }
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
                  <label for={f.label}> {f.label}</label>
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