import React from 'react';
import {useState, useEffect, useMemo} from 'react';
import {ReactComponent as Scissor} from '../../static/icons/scissor.svg';
import {ReactComponent as Trans} from '../../static/icons/trans.svg';
import {ReactComponent as Paw} from '../../static/icons/paw.svg';
import {ReactComponent as Rainbow} from '../../static/icons/rainbow.svg';
import {ReactComponent as Ace} from '../../static/icons/ace.svg';
import {ReactComponent as Bicycle} from '../../static/icons/bicycle.svg';
import {ReactComponent as Intersect} from '../../static/icons/intersect.svg';
import {ReactComponent as Polygon} from '../../static/icons/polygon.svg';
// import {ReactComponent as ReactLogo} from './logo.svg';
//import '../../App.scss';

export function getIcon(movieTypes){
  var Icon = Rainbow;

  if(movieTypes == null){
    return Icon;
  }

  // Random Selection of Icon
  let typ = movieTypes[Math.floor(Math.random() * movieTypes.length)]

  if(typ.LABEL == "Gay"){
    Icon = Paw;
  }
  if(typ.LABEL == "Lesbian"){
    Icon = Scissor;
  }
  if(typ.LABEL == "Transgender"){
    Icon = Trans;
  }
  if(typ.LABEL == "Bisexual"){
    Icon = Bicycle;
  }
  if(typ.LABEL == "Ace/Aro"){
    Icon = Ace;
  }
  if(typ.LABEL == "Intersex"){
    Icon = Intersect;
  }
  if(typ.LABEL == "Polyamory"){
    Icon = Polygon;
  }
  return Icon;
}

const maxRating = 5;

function RatingBar({rating, mouseEnterFn, mouseLeaveFn, clickFn, mouseOverFn, rotated, Icon}){

  if(rating == null && clickFn == null){
    return <div className={'defaultVote'}>
      {[...Array(maxRating)].map((_, idx) => {
        return <div key={idx}>
          <Icon style={{fill: 'lightgrey'}} />
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
      return <div key={idx} onMouseOver={() => {mouseOverFn(idx+1)}}><Icon style={{visibility: 'hidden'}} /></div>
    }
    if (Math.ceil(rating) == (1+idx)){
      let clippath = !rotated ? 'inset(0 '+ (1 - rating + Math.floor(rating))*100 + '% 0 0)' : 'inset('+ (1 - rating + Math.floor(rating))*100 + '% 0 0 0)';
      if (rating == Math.floor(rating)){
        clippath = 'inset(0 0 0 0)'
      }

      return <div key={idx} onMouseOver={() => {mouseOverFn(idx + 1)}}><Icon style={{clipPath: clippath}} /></div>
    }
    return <div key={idx} onMouseOver={() => {mouseOverFn(idx + 1)}}><Icon /></div>
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

  // var currentRating = (
  //   <div aria-label={"Your current rating is: " + (rating)} onMouseLeave={mouseLeaveFn} onMouseEnter={mouseEnterFn} onClick={clickFn} style={s}>
  //   {[...Array(maxRating)].map((_, idx) => <div onMouseOver={() => mouseOverFn(idx + 1)} key={idx}>
  //       <Icon key={idx} style={{visibility: rating > idx ? 'visible':'hidden'}} />
  //     </div>)
  //   }
  // </div>
  // );

function RatingDisplay({id, rating, numRating, movieTypes, votable}){
  /*
    id - movie id
    rating - (number) avg rating
    rotated - whether rating is rotated
    movieTypes - List associated movie lgbtqia+ categories
    votable - whetehr we allow votes.
  */
  const [active, setActive] = useState(false);
  // Local user's vote
  const [vote, setVote] = useState(
    parseInt(localStorage.getItem(`movie_rating_${id}_value`)) || null
  );
  // Creates hover effect for newVote (proposed pre-click)
  const [newVote, updateNewVote] = useState(null);

  

  const Icon = useMemo(() => {
    return getIcon(movieTypes)
  }, [])

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

  //TODO: Check local stored variables in session - set vote
  //TODO: When place vote, update/insert vote in db. Store vote locally on success

  function setNewVote(v){
    if(votable){
      updateNewVote(v)
    }
  }

  var rotateClass = '';
  if([Bicycle].indexOf(Icon) != -1){
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
          rating={rating}
        />
        <div className='description'>
          <span><b>Audience Rating</b><br/>{rating? rating.toFixed(2) : '-'} out of {maxRating}
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

  //   // Conditional creation of currentvote infront of existing rating
  // var yourVote = <></>;
  // if(vote !== null || active){
  //   yourVote = <div className={classname} aria-label={"Your current rating is: " + (active? newVote : vote)}>
  //     {[...Array(maxRating)].map((_, idx) => <div onMouseOver={() => {setNewVote(idx + 1)}} key={idx}>
  //         <Icon key={idx} style={{visibility: (active? newVote : vote) > idx ? 'visible':'hidden'}} />
  //       </div>)
  //     }
  //   </div>
  // }

  // //   <div className='user rating' onMouseLeave={()=>{setActive(false)}} onMouseEnter={()=>{setActive(true)}} onClick={() => {updateRating(newVote)}}>
  // //   {/* Your current active vote, made vote */}
  // //   {yourVote}
  // //   {/* When there is no vote made*/}
  // //   {createDefaultVote(Icon)}
  // // </div>

// function Rating({id, rating, rotated, movieTypes, votable}){
//   /*
//     id - movie id
//     rating - (number) avg rating
//     rotated - whether rating is rotated
//     movieTypes - List associated movie lgbtqia+ categories
//     votable - whetehr we allow votes.
//   */
//   const [active, setActive] = useState(false);
//   // Local user's vote
//   const [vote, setVote] = useState(
//     localStorage.getItem(`movie_rating_${id}_value`) || null
//   );
//   // Creates hover effect for newVote (proposed pre-click)
//   const [newVote, updateNewVote] = useState(null);

//   const maxRating = 5;

//   const Icon = useMemo(() => {
//     return getIcon(movieTypes)
//   }, [])

//   function updateRating(rating){

//     fetch('/api/movie/rating', {
//       method: 'POST',
//       headers: {
//         'Accept': 'application/json',
//         'Content-Type': 'application/json',
//         'cache-control': 'no-store',
//       },
//       body: JSON.stringify({
//         "movie_id": id,
//         "rating": rating,
//         "movie_rating_id": localStorage.getItem(`movie_rating_${id}_id`) || -1
//       })
//     }).then(res => res.json()).then(data => {
//       localStorage.setItem(`movie_rating_${id}_id`, data["movie_rating_id"])
//       localStorage.setItem(`movie_rating_${id}_value`, rating)
//       setVote(rating);
//     })
    
//   }


//   //TODO: Check local stored variables in session - set vote
//   //TODO: When place vote, update/insert vote in db. Store vote locally on success

//   function setNewVote(v){
//     if(votable){
//       updateNewVote(v)
//     }
//   }

//   var rotateClass = '';
//   if([Bicycle].indexOf(Icon) != -1){
//     rotateClass = ' norotate';
//   }
  

//   var classname = "yourvote";
//   if((!active && vote < rating) || (active && newVote < rating) || !rating){
//     classname += " front";
//   }

//     // Conditional creation of currentvote infront of existing rating
//   var yourVote = <></>;
//   if(vote !== null || active){
//     yourVote = <div className={classname} aria-label={"Your current rating is: " + (active? newVote : vote)}>
//       {[...Array(maxRating)].map((_, idx) => <div onMouseOver={() => {setNewVote(idx + 1)}} key={idx}>
//           <Icon key={idx} style={{visibility: (active? newVote : vote) > idx ? 'visible':'hidden'}} />
//         </div>)
//       }
//     </div>
//   }


//   return (
//     <div className={"rating" + rotateClass} onMouseLeave={()=>{setActive(false)}} onMouseEnter={()=>{setActive(true)}} onClick={() => {updateRating(newVote)}}>
//       {yourVote}
//       {!rating && votable && <div>
//           {[...Array(maxRating)].map((_, idx) => {
//             return <div key={idx} onMouseOver={() => {setNewVote(idx+1)}}><Icon style={{fill: 'lightgrey'}} /></div>
//           })
//         }
//         </div>
//       }
//       { rating > 0 &&
//       <div aria-label={"The current rating is: " + rating} >
      
//       {[...Array(maxRating)].map((_, idx) => {
//         if (Math.ceil(rating) < (1+idx)){
//           return <div key={idx} onMouseOver={() => {setNewVote(idx+1)}}><Icon style={{visibility: 'hidden'}} /></div>
//         }
//         if (Math.ceil(rating) == (1+idx)){
//           if(rotated ){ //|| ([Bicycle].indexOf(Icon) != -1)
//             return <div key={idx} onMouseOver={() => {setNewVote(idx + 1)}}><Icon style={{clipPath: 'inset(0 '+ (rating - Math.floor(rating))*100 + '% 0 0)'}} /></div>
//           }else{
//             return <div key={idx} onMouseOver={() => {setNewVote(idx + 1)}}><Icon style={{clipPath: 'inset(0 0 '+ (rating - Math.floor(rating))*100 + '% 0)'}} /></div>
//           }
//         }
//         return <div key={idx} onMouseOver={() => {setNewVote(idx + 1)}}><Icon /></div>
//       }
//       )}
//     </div>
// }
//   </div>
//   )

// }

// class Rating extends Component {
//   constructor(props){
//     super(props)
//     this.state = {
//       active: false,
//       voted: false,
//     }
//   }

//   componentDidMount(){
//     // TODO: Get whether person voted before
//   }

//   currentVote(idx){
//     if( (idx+1) != this.state.currentVote){
//       this.setState({
//         currentVote: idx+1,
//         voted: 0
//       })
//     }
//   }

//   makeVote(){
//     if(this.state.currentVote != this.state.voted){
//       this.setState({
//         voted: this.state.currentVote
//       })
//     }
//   }
//   setMode(active){
//     this.setState({
//       active: active
//     })
//   }

//   render(){

//     var max_score = 5;

//     var icon = Scissor;
//     if(props.movieType == "")

//     return (
//       <div className="rating" onMouseLeave={()=>{this.setMode(false)}} onMouseEnter={()=>{this.setMode(true)}} onClick={()=>{this.makeVote()}}>
//         {(this.state.voted || this.state.active) && <div className={(!this.state.active && this.state.voted < this.props.score) || (this.state.active && this.state.currentVote < this.props.score)? "yourvote front": "yourvote"}>
//           {[...Array(max_score )].map((_, idx) => <div onMouseOver={() => {this.currentVote(idx)}}>
//             <Scissor key={idx} style={{visibility: (this.state.active? this.state.currentVote : this.state.voted) > idx ? 'visible':'hidden'}} />
            
//           </div>)}
//         </div>}
//         <div aria-label={"The current rating is: " + this.props.score} >
//           {[...Array(max_score)].map((_, idx) => {
//             if (Math.ceil(this.props.score) < (1+idx)){
//               return <div key={idx} onMouseOver={() => {this.currentVote(idx)}}><Scissor style={{visibility: 'hidden'}} /></div>
//             }
//             if (Math.ceil(this.props.score) == (1+idx)){
//               if(this.props.rotated){
//                 return <div key={idx} onMouseOver={() => {this.currentVote(idx)}}><Scissor style={{clipPath: 'inset(0 '+ (this.props.score - Math.floor(this.props.score))*100 + '% 0 0)'}} /></div>
//               }else{
//                 return <div key={idx} onMouseOver={() => {this.currentVote(idx)}}><Scissor style={{clipPath: 'inset(0 0 '+ (this.props.score - Math.floor(this.props.score))*100 + '% 0)'}} /></div>
//               }
//             }
//             return <div key={idx} onMouseOver={() => {this.currentVote(idx)}}><Scissor /></div>
//           }
//           )}
//         </div>
//       </div>
//     )
//   }
// }
export default Rating
export {RatingDisplay}