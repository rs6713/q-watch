import React, { Component } from 'react';
import {ReactComponent as Logo} from '../../static/website/logo.svg';
import {Link, useLocation} from 'react-router-dom';
import {ReactComponent as Grid} from '../../static/icons/grid.svg'
import {ReactComponent as World} from '../../static/icons/world2.svg'
import {ReactComponent as Rank} from '../../static/icons/rank.svg'
import {ReactComponent as Time} from '../../static/icons/time.svg'
import {ReactComponent as Hamburger} from '../../static/icons/menu.svg'

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
          <Link to={"/visualizations/overtime"} className="link">
            <div>
              <Time title="" />
              <span>Over Time</span>
            </div>
          </Link>
          <Link to={"/visualizations/bycountry"} className="link">
            <div>
              <World title="" />
              <span>By Country</span>
            </div>
          </Link>
        </div>
      </div>
    )

}

export default Menu