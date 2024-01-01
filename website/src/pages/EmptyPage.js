import React, {useState} from 'react';

import MainMenu from './components/MainMenu';
import Footer from './components/Footer';
import lost1 from '../static/images/lost/lost-broad.gif';
import lost2 from '../static/images/lost/lost-louise.gif';
import lost3 from '../static/images/lost/lost-lost.gif';
import lost4 from '../static/images/lost/lost-travolta.gif';
import lost5 from '../static/images/lost/lost-llama.gif';
import Alert from './components/Alert';

function EmptyPage(){

  const gifs = [
    lost1, lost2, lost3, lost4, lost5
  ]
  const lostgif = gifs[parseInt(Math.random() * gifs.length)];

  return (
    <div className='page' id='empty'>
      <MainMenu/>
      <div id='main'>
        <Alert header='Whoops!' subtitle="You appear to be lost, my dear..."/>
        <img src = {lostgif} />
      </div>
      <Footer />
    </div>
  )

}

export default EmptyPage