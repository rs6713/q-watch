import React from 'react';
import {useState, useEffect, useMemo} from 'react';
// import {ReactComponent as Scissor} from '../../static/icons/scissor.svg';
// import {ReactComponent as Trans} from '../../static/icons/trans.svg';
// import {ReactComponent as Paw} from '../../static/icons/paw.svg';
// import {ReactComponent as Rainbow} from '../../static/icons/rainbow.svg';
// import {ReactComponent as Ace} from '../../static/icons/ace.svg';
// import {ReactComponent as Bicycle} from '../../static/icons/bicycle.svg';
// import {ReactComponent as Intersect} from '../../static/icons/intersect.svg';
// import {ReactComponent as Polygon} from '../../static/icons/polygon.svg';
import {Icon} from './Image'

export function getIcon(movieTypes){
  /* Get correct Icon representative of Movie Type */
  var typIcon = 'rainbow';
  var typLabel = 'LGBTQIA+';

  function getTypeIcon(typ){
    // Random Selection of Icon
    
    switch(typ.LABEL) {
      case "Gay": return 'paw';
      case "Lesbian": return 'scissor';
      case "Transgender": return 'trans';
      case "Bisexual": return 'bicycle';
      case "Ace/Aro": return 'ace';
      case "Intersex": return 'intersect';
      case "Polyamory": return 'polygon';
      default: return 'rainbow';
    }
  }
  if(movieTypes !== null && movieTypes.length > 0){
    let typ = movieTypes[Math.floor(Math.random() * movieTypes.length)]
    typIcon = getTypeIcon(typ)
    typLabel = typ.LABEL
  }
  return <Icon label={typLabel} name={typIcon}/>
}

function getTypeIcon(icon, style){
  return <Icon label={icon.props.label} name={icon.props.name} style={style} />
}

const maxRating = 5;

function RatingBar({rating, mouseEnterFn, mouseLeaveFn, clickFn, mouseOverFn, rotated, Icon}){

  

  if(rating == null && clickFn == null){
    return <div className={'defaultVote'}>
      {[...Array(maxRating)].map((_, idx) => {
        return <div key={idx}>
            {getTypeIcon(Icon, {fill: 'lightgrey', filter: 'invert(96%) sepia(3%) saturate(83%) hue-rotate(194deg) brightness(111%) contrast(65%)'})}
        </div>
      })
    }
    </div>
  }

  let interactive = clickFn != null;
  let style = interactive ? {'cursor': 'pointer'} : {};

  clickFn = clickFn || (() => {});
  mouseEnterFn = mouseEnterFn || (() => {});
  mouseLeaveFn = mouseLeaveFn || (() => {});
  mouseOverFn = mouseOverFn || ((a) => {});

  return (<div aria-label={"The current rating is: " + rating} onMouseLeave={mouseLeaveFn} onMouseEnter={mouseEnterFn} onClick={clickFn} style={style}>
  {[...Array(maxRating)].map((_, idx) => {
    if (Math.ceil(rating) < (1+idx)){
      return <div key={idx} onMouseOver={() => {mouseOverFn(idx+1)}}>
        {getTypeIcon(Icon, {visibility: 'hidden'})}
      </div>
    }
    if (Math.ceil(rating) == (1+idx)){
      let clippath = !rotated ? 'inset(0 '+ (1 - rating + Math.floor(rating))*100 + '% 0 0)' : 'inset('+ (1 - rating + Math.floor(rating))*100 + '% 0 0 0)';
      if (rating == Math.floor(rating)){
        clippath = 'inset(0 0 0 0)'
      }

      return <div key={idx} onMouseOver={() => {mouseOverFn(idx + 1)}}>
        {getTypeIcon(Icon, {clipPath: clippath})}
      </div>
    }
    return <div key={idx} onMouseOver={() => {mouseOverFn(idx + 1)}}>{getTypeIcon(Icon)}</div>
    }
    )}
  </div>)
}

function Rating({rating, Icon, clickFn, mouseEnterFn, mouseLeaveFn, mouseOverFn, rotated, noDefault}){

  noDefault = noDefault || false;

  var currentRating = <RatingBar 
    rating={rating}
    clickFn={clickFn}
    mouseEnterFn={mouseEnterFn}
    mouseLeaveFn={mouseLeaveFn}
    mouseOverFn={mouseOverFn}
    rotated={rotated}
    Icon={Icon}
  />
  var backgroundRating = noDefault? <></> : <RatingBar
    Icon={Icon}
    rotated={rotated}
  />

  return (
    <div className='rating'>
      {/* Your current active vote, made vote */}
      {currentRating}
      {/* When there is no vote made*/}
      {backgroundRating}
    </div>
  )
}

function RatingDisplay({id, rating, numRating, movieTypes, votable}){
  /*
    id - movie id
    rating - (number) avg rating
    rotated - whether rating is rotated
    movieTypes - List associated movie lgbtqia+ categories
    votable - whetehr we allow votes.
  */
  const Icon = useMemo(() => {
    return getIcon(movieTypes)

  }, [])
  const originalVote = useMemo(() => {
    return parseInt(localStorage.getItem(`movie_rating_${id}_value`)) || null
  }, [rating])

  const [active, setActive] = useState(false);

  // Local user's vote
  const [vote, setVote] = useState(originalVote);

  // Creates hover effect for newVote (proposed pre-click)
  const [newVote, updateNewVote] = useState(null);

  const totalRating = vote === originalVote ? rating : (rating * numRating + vote - (originalVote || 0)) / (numRating + (originalVote === null ? 1: 0));

  function updateRating(rating){

    fetch('/api/movie/rating', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'cache-control': 'no-store',
      },
      body: JSON.stringify({
        "movie_id": id,
        "rating": rating,
        "movie_rating_id": localStorage.getItem(`movie_rating_${id}_id`) || -1
      })
    }).then(res => res.json()).then(data => {
      localStorage.setItem(`movie_rating_${id}_id`, data["movie_rating_id"])
      localStorage.setItem(`movie_rating_${id}_value`, rating)
      setVote(rating);
    })
    
  }

  function setNewVote(v){
    if(votable){
      updateNewVote(v)
    }
  }

  var rotateClass = '';
  if(Icon.props.name == 'bicycle'){
    rotateClass = ' norotate';
  }
  

  return (
    <div className={"ratingContainer" + rotateClass} >
      <div >
        <Rating
          Icon={Icon}
          mouseEnterFn={()=>{setActive(true)}}
          mouseLeaveFn={()=>{setActive(false)}}
          clickFn={() => {updateRating(newVote)}}
          mouseOverFn={setNewVote}
          rotated={false}
          rating={active? newVote : vote}
        />
        <div className='description'>
          <b>Your Rating</b><br/>{vote? vote : '-'} out of {maxRating}
        </div>
      </div>
      <div>
        <Rating
          Icon={Icon}
          rotated={false}
          rating={totalRating}
        />
        <div className='description'>
          <span><b>Audience Rating</b><br/>{totalRating? totalRating.toFixed(2) : '-'} out of {maxRating}
          </span>
        </div>
      </div>
      <div>
        <div>
          {numRating} Queer Rating{numRating > 1? 's':''}
        </div>
      </div>
    </div>
  )

}

export default Rating
export {RatingDisplay}