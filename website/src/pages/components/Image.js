import React from "react";

function Image(name, caption){
  try {
    // Import image on demand
    const image = require(`../../static/movie-pictures/${name}`);

    // If the image doesn't exist. return null
    if (!image){
      const default_image = require(`../../static/movie-pictures/default_pride.png`);
      return <img src={default_image} alt={caption} />
    }
    return <img src={image} alt={caption} />
    

    // return <div style={{backgroundImage: image}} className={classname} alt={caption}/>
  } catch (error) {
    console.log(`Image with name "${name}" does not exist`);
    
    const default_image = require(`../../static/movie-pictures/default_pride.png`);
    return <img src={default_image} alt={caption}  />
  }
};

export default Image;