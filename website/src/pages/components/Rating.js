import {useState} from 'react';
import {ReactComponent as Scissor} from '../../static/icons/scissor.svg';
import {ReactComponent as Trans} from '../../static/icons/trans.svg';
import {ReactComponent as Paw} from '../../static/icons/paw.svg';
import {ReactComponent as Rainbow} from '../../static/icons/rainbow.svg';
// import {ReactComponent as ReactLogo} from './logo.svg';
//import '../../App.scss';

export function getIcon(movieTypes){
  var Icon = Rainbow;
  // Selection of Icon
  for(let typ of movieTypes){
    if(typ.LABEL == "Lesbian"){
      Icon = Scissor;
    }
    if(typ.LABEL == "Transgender"){
      Icon = Trans;
    }
    if(typ.LABEL == "Gay"){
      Icon = Paw;
    }
  }
  return Icon;
}

function Rating({id, rating, rotated, movieTypes}){
  const [active, setActive] = useState(false);
  const [vote, setVote] = useState(null);
  const [newVote, setNewVote] = useState(null);

  const maxRating = 5;

  //TODO: Check local stored variables in session - set vote
  //TODO: When place vote, update/insert vote in db. Store vote locally on success


  var Icon = getIcon(movieTypes);


  var classname = "yourvote";
  if((!active && vote < rating) || (active && newVote < rating)){
    classname += " front";
  }

    // Conditional creation of currentvote infront of existing rating
  var content = <></>;
  if(vote !== null || active){
    content = <div className={classname}>
      {[...Array(maxRating)].map((_, idx) => <div onMouseOver={() => {setNewVote(idx)}}>
          <Icon key={idx} style={{visibility: (active? newVote : rating !== null) > idx ? 'visible':'hidden'}} />
          
        </div>)
      }
    </div>
  }


  return (
    <div className="rating" onMouseLeave={()=>{setActive(false)}} onMouseEnter={()=>{setActive(true)}} onClick={()=>{setVote(newVote)}}>
      {content}
      <div aria-label={"The current rating is: " + rating} >
      {[...Array(maxRating)].map((_, idx) => {
        if (Math.ceil(rating) < (1+idx)){
          return <div key={idx} onMouseOver={() => {setNewVote(idx+1)}}><Icon style={{visibility: 'hidden'}} /></div>
        }
        if (Math.ceil(rating) == (1+idx)){
          if(rotated){
            return <div key={idx} onMouseOver={() => {setNewVote(idx + 1)}}><Icon style={{clipPath: 'inset(0 '+ (rating - Math.floor(rating))*100 + '% 0 0)'}} /></div>
          }else{
            return <div key={idx} onMouseOver={() => {setNewVote(idx + 1)}}><Icon style={{clipPath: 'inset(0 0 '+ (rating - Math.floor(rating))*100 + '% 0)'}} /></div>
          }
        }
        return <div key={idx} onMouseOver={() => {setNewVote(idx + 1)}}><Icon /></div>
      }
      )}
    </div>
  </div>
  )

}

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