import React, { Component, useState, useEffect } from 'react';
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
import {ReactComponent as Minus} from '../../static/icons/minus.svg'

function MainMenu(){

  const [cls, setCls] = useState('');
  const [sideMenuActive, setSideMenuActive] = useState(false);


  useEffect(() => {

    // Get the navbar
    var navbar = document.getElementById("MainMenu");

    // Get the offset position of the navbar
    var sticky = navbar.offsetTop;
    function scroll(){

      if (window.pageYOffset >= sticky) {
        setCls('sticky')
      } else {
        setCls('');
      }
    }
    window.addEventListener('scroll', scroll);

    return  () => window.removeEventListener('scroll', scroll);
  }, []);

  let leftNav = <nav>
    <Link to={"/browse"} className={"link" + (useLocation().pathname == "/browse"? ' active' : ' inactive')}>
      <span>Browse</span>
    </Link>
    <Link to={"/rankings"} className={"link" + (useLocation().pathname == "/rankings"? ' active' : ' inactive')}>
      <span>Rankings</span>
    </Link>
    <div>
      <span>Data</span>
      <div className='dropdown'>
        <div><Link to={"/data/overview"} className={"link" + (useLocation().pathname == "/data/overview"? ' active' : ' inactive')}>
          Overview
        </Link></div>
        <div><Link to={"/data/country"} className={"link" + (useLocation().pathname == "/data/country"? ' active' : ' inactive')}>
          By Country
        </Link></div>
      </div>
    </div>
  </nav>

  let rightNav = <nav>
    <Link to={"/faq"} className={"link" + (useLocation().pathname == "/faq"? ' active' : ' inactive')}>
      <span>FAQ</span>
    </Link>
    {/* <Link to={"/disclaimers"} className={"link" + (useLocation().pathname == "/disclaimers"? ' active' : ' inactive')}>
      <span>Disclaimers</span>
    </Link> */}
    <div>
      <span>Disclaimers</span>
      <div className='dropdown'>
        <div><Link to={"/disclaimers/recognition"} className={"link" + (useLocation().pathname == "/disclaimers/recognition"? ' active' : ' inactive')}>
          Shout Outs
        </Link></div>
        <div><Link to={"/disclaimers/labels"} className={"link" + (useLocation().pathname == "/disclaimers/labels"? ' active' : ' inactive')}>
          Our Labels
        </Link></div>
        <div><Link to={"/disclaimers/limitations"} className={"link" + (useLocation().pathname == "/disclaimers/limitations"? ' active' : ' inactive')}>
          Our Limits
        </Link></div>
        <div><Link to={"/disclaimers/goals"} className={"link" + (useLocation().pathname == "/disclaimers/goals"? ' active' : ' inactive')}>
          Our Goals
        </Link></div>
      </div>
    </div>
  </nav>

  return (
    <div id='MainMenu' className={cls}>
      {leftNav}
      <Hamburger onClick={()=>{setSideMenuActive(true)}}/>
      <Link to={"/"} className='logo'>
          <Logo title=""/>
      </Link>
      {rightNav}
      <div className={'sideMenu' + (sideMenuActive ? ' active': '')}>
        <Minus onClick={()=>{setSideMenuActive(false)}}/>
        {leftNav}
        {rightNav}
      </div>
    </div>
  )

}

export default MainMenu