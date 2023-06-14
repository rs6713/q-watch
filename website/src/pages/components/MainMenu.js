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

function MainMenu(){

  const [cls, setCls] = useState('');



  useEffect(() => {

    // Get the navbar
    var navbar = document.getElementById("MainMenu");

    // Get the offset position of the navbar
    var sticky = navbar.offsetTop;
    function scroll(){

      if (window.pageYOffset >= sticky) {
        setCls('sticky')
      } else {
        console.log('nostocky')
        setCls('');
      }
    }
    window.addEventListener('scroll', scroll);

    return  () => window.removeEventListener('scroll', scroll);
  }, []);

  return (
    <div id='MainMenu' className={cls}>
      <nav>
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
      <Link to={"/"} className='logo'>
          <Logo title=""/>
      </Link>
      <nav>
        <Link to={"/faq"} className={"link" + (useLocation().pathname == "/faq"? ' active' : ' inactive')}>
          <span>FAQ</span>
        </Link>
        <Link to={"/disclaimers"} className={"link" + (useLocation().pathname == "/disclaimers"? ' active' : ' inactive')}>
          <span>Disclaimers</span>
        </Link>
      </nav>
    </div>
  )

}

export default MainMenu