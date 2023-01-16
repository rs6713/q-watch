import React from 'react';
import {ReactComponent as Logo} from '../../static/website/logo.svg';
// import {ReactComponent as ReactLogo} from './logo.svg';
//import '../../App.scss';
import Coffee from './Coffee'

const Footer = () => {
  return (
    <div className="footer">
      <Logo />
      <span>&copy; 2023 Q-Watch</span>
      <Coffee/>
    </div>
  )
}

export default Footer;