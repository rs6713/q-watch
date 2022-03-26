import React from 'react';
import ExpandableBubbles from './ExpandableBubbles'
import {ReactComponent as Minus} from '../../static/icons/minus.svg'

function Filters(props){
  //<Minus/>
  return (

    <div id="Filters">
      <div>
      <h1>{props.config.title}</h1>
      {props.config.filterSections.map((filter) => (
        <div>
          
          {filter.type=="bubble" && 
            <ExpandableBubbles 
              title={filter.title}
              aside={filter.warning || ""}
              items={filter.filters.map(f=> f.label)}
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