import React, { Component, useEffect } from 'react';
import {ReactComponent as Logo} from '../../static/website/logo.svg';
import {Link, useLocation} from 'react-router-dom';
import {ReactComponent as Grid} from '../../static/icons/grid.svg'
import {ReactComponent as World} from '../../static/icons/world2.svg'
import {ReactComponent as Rank} from '../../static/icons/rank.svg'
import {ReactComponent as Time} from '../../static/icons/time.svg'
import {ReactComponent as Hamburger} from '../../static/icons/menu.svg'
import {ReactComponent as Question} from '../../static/icons/question.svg'
import {ReactComponent as Note} from '../../static/icons/note.svg'
import {ReactComponent as Graph} from '../../static/icons/graph.svg'


function Menu(){

    return (
      <div id="MenuContainer">
        <Hamburger className="hamburger" title="" aria-label="Menu" />
        <div className="sidetab"><div/> <div/></div>
        <div id="Menu">
          <Link to={"/"}>
          <Logo title=""/>
          </Link>

          <Link to={"/browse"} className={"link" + (useLocation().pathname == "/browse"? ' active' : ' inactive')}>
            <div>
              <Grid title=""/>
              <span>Browse</span>
            </div>
          </Link>
          <Link to={"/rankings"} className={"link" + (useLocation().pathname == "/rankings"? ' active' : ' inactive')}>
            <div>
            <Rank title="" />
              <span>Rankings</span>
            </div>
          </Link>
          <hr />
          <h3>The State of Queer Cinema</h3>
          <Link to={"/overview"} className={"link" + (useLocation().pathname == "/overview"? ' active' : ' inactive')}>
            <div>
              <Graph title=""/>
              <span>Overview</span>
            </div>
          </Link>
          <Link to={"/visualizations/overtime"} className={"link" + (useLocation().pathname == "/visualizations/overtime"? ' active' : ' inactive')}>
            <div>
              <Time title="" />
              <span>Over Time</span>
            </div>
          </Link>
          <Link to={"/visualizations/bycountry"} className={"link" + (useLocation().pathname == "/visualizations/bycountry"? ' active' : ' inactive')}>
            <div>
              <World title="" />
              <span>By Country</span>
            </div>
          </Link>
          {/* <div className='filler' /> */}
          <span>
          <Link to={"/faq"} className={"link" + (useLocation().pathname == "/faq"? ' active' : ' inactive')}>
            <div>
              <Question title="" />
              <span>FAQ</span>
            </div>
          </Link>
          <Link to={"/disclaimers"} className={"link" + (useLocation().pathname == "/disclaimers"? ' active' : ' inactive')}>
            <div>
              <Note title="" />
              <span>Disclaimers</span>
            </div>
          </Link>
          </span>
        </div>
        
      </div>
    )

}

export default Menu