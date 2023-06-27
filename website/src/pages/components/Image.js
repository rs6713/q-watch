import React from "react";


export function Icon({name, label, className}){
  try{
    if(label === undefined){
      label='';
    }
    const svgIcon = require(`../../static/icons/${name}.svg`);

    // const Icon = require(`../../static/icons/${name}.svg`).default
    // return <Icon />

    if(!svgIcon){
      return <></>
    }

    return <img src={svgIcon} title={label} className={className} />
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
  try {
    // Import image on demand
    const image = require(`../../static/movie-pictures/${name}`);

    // If the image doesn't exist. return null
    if (!image){
      const default_image = require(`../../static/movie-pictures/default_pride.png`);
      return <img src={default_image} alt={caption} key={image}/>
    }
    return <img src={image} alt={caption} key={image}/>
    

    // return <div style={{backgroundImage: image}} className={classname} alt={caption}/>
  } catch (error) {
    console.log(`Image with name "${name}" does not exist`);
    
    const default_image = require(`../../static/movie-pictures/default_pride.png`);
    return <img src={default_image} alt={caption}  key={default_image}/>
  }
};

export default Image;