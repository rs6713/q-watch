import React from "react";


export function Icon({name, label, className, style}){
  try{
    if(label === undefined){
      label='';
    }
    //const svgIcon = require(`../../static/icons/${name}.svg`);
    const svgIcon = `http://storage.googleapis.com/qwatch-69-static/media/icons/${name}.svg`;

    // const Icon = require(`../../static/icons/${name}.svg`).default
    // return <Icon />

    if(!svgIcon){
      return <></>
    }

    return  <img src={svgIcon} title={label} className={className} style={style}/>
    return svgIcon.default
    return <svg>
        <use xlinkHref={`../../static/icons/${name}.svg`} className={className} fill="currentColor" stroke="currentColor"></use>
    </svg>
    return <svg xmlns={svgIcon} className={className} fill="currentColor" stroke="currentColor"/>
  }catch (error) {
    return <></>
  }
}

function Image(name, caption){
  const url = 'http://storage.googleapis.com/qwatch-69-static/media/movie-pictures';

  try {
    
    return <img src={`${url}/${name}`} alt={caption} key={name}/>
    
    // return <div style={{backgroundImage: image}} className={classname} alt={caption}/>
  } catch (error) {

    return <img src={`${url}/default_pride.png`} alt={caption}  key={'default_pride'}/>
  }


  //const url = '../../static/movie-pictures';
  try {
    

    // Import image on demand
    const image = require(`${url}/${name}`);

    // If the image doesn't exist. return null
    if (!image){
      const default_image = require(`${url}/default_pride.png`);
      return <img src={default_image} alt={caption} key={image}/>
    }
    return <img src={image} alt={caption} key={image}/>
    

    // return <div style={{backgroundImage: image}} className={classname} alt={caption}/>
  } catch (error) {
    console.log(`Image with name "${name}" does not exist`);
    
    const default_image = require(`${url}/default_pride.png`);
    return <img src={default_image} alt={caption}  key={default_image}/>
  }
};

export default Image;