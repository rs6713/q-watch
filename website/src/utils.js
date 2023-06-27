// import ISO6391 from 'iso-639-1';
import {iso6393} from 'iso-639-3'
import Iso639Type from 'iso-639-language';

const iso6391 = Iso639Type.getType(1); 
const iso6392 = Iso639Type.getType(2); 
// const iso6393 = Iso639Type.getType(3); 

var formatRuntime = function(runtime){
  var hours = Math.floor(runtime / (60));
  var minutes = Math.floor( runtime % (60));
  if(hours === 0){
    return String(minutes) + "min";
  }

  return (String(hours) + "hr " + String(minutes) + "min");
}


function formatLanguage(language){

  function getLanguage(l){

    // Bugs in dependent libraries
    if(l === 'ZXX'){
      return 'Silent'
    }
    if(l === 'JA' || l === 'JP'){
      return 'Japanese'
    }


    if(l.length == 2){
      return iso6391.getNameByCodeEnglish(l.toLowerCase())
    }
    
    let langs = iso6393.filter(o => o.iso6393 == l.toLowerCase())
    if(langs.length){
      return langs[0].name
    }
    // I might have entered the language in non-CODE format
    if(l.length > 3){
      return l
    }
    return ''
  }

  return language.split(', ').map(
    getLanguage
  ).filter(l => l.length > 0).join(', ')
}

export {formatRuntime, formatLanguage};
