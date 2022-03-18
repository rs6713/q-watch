import React from 'react';
import {ReactComponent as Logo} from '../../static/website/logo.svg';
// import {ReactComponent as ReactLogo} from './logo.svg';
//import '../../App.scss';

const Footer = () => {
  return (
    <div className="footer">
      <Logo />
      <span>&copy; 2022 Becks Simpson</span>
    </div>
  )
}

export default Footer;