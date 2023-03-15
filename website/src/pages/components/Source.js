import React, {useState, useEffect} from 'react';
import {ReactComponent as ThumbDown} from '../../static/icons/thumbdown.svg';
import {ReactComponent as ThumbUp} from '../../static/icons/thumbup.svg';

// const source = {
//   img: "/sources/netflix.png",
//   subtype: "UK",
//   votes: 46,
//   url: "netflix.com"
// }

function Source({source}){

  const [votes, setVotes] = useState(0);
  const [voted, setVoted] = useState(
    localStorage.getItem(`movie_source_${source.ID}_vote_value`) || 0
  );

  console.log('source vote: ', localStorage.getItem(`movie_source_${source.ID}_vote_id`), ' ', localStorage.getItem(`movie_source_${source.ID}_vote_value`), ' voted: ', voted)

    useEffect(()=>{
      let personal_vote_id = localStorage.getItem(`movie_source_${source.ID}_vote_id`)
      let non_user_votes = source.VOTES.filter(
        v=> v.ID != personal_vote_id
      )
      if(non_user_votes.length){
        
        // existing vote
        setVotes(
          non_user_votes.map(v=>v.VOTE).reduce((a, b) => a + b) + voted
        )

      }else{
        setVotes(voted)
      }

    }, [voted])

    function updateVoted(v){

      fetch('/api/source/vote', {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'cache-control': 'no-store',
        },
        body: JSON.stringify({
          "movie_source_id": source.ID,
          "vote": v,
          "movie_source_vote_id": localStorage.getItem(`movie_source_${source.ID}_vote_id`) || -1
        })//this.state.filterCriteria
      }).then(res => res.json()).then(data => {
        localStorage.setItem(`movie_source_${source.ID}_vote_id`, data["movie_source_vote_id"])
        localStorage.setItem(`movie_source_${source.ID}_vote_value`, v)
        setVoted(v);
      })
      
    }

    return (
      <div className="source">
        <img src={'/sources/' + source.IMAGE} aria-label={"Movie can be found at " + source.URL + (source.REGION? " (" + source.REGION + ")" : "" )}/>
        <span id="votes" aria-label={"Current Votes for this Source: "+ votes}>{votes}</span>
        <span id="region">{source.REGION}</span>
        <span id="voter" className={voted !== 0 ? "active": ""}>
          <span className={voted==-1 ? "active": ""}><ThumbDown title="Downvote this source." aria-label="Downvote this source." onClick={()=>{updateVoted(voted == -1 ? 0 : -1)}} /></span>
          <span className={voted==1 ? "active": ""}><ThumbUp title="Upvote this source." aria-label="Upvote this source." onClick={() => {updateVoted(voted == 1? 0: 1)}} /></span>
        </span>
      </div>
    )
}

// class Source extends Component {
//   constructor(props){
//     super(props)
//     this.state = {
    
//     }
//   }
  

//   componentDidMount(){
//     // TODO get source  - by id
//     // How to determine if user has already voted?
//     this.setState({
//       img: source.img,
//       subtype: source.subtype,
//       votes: source.votes,
//       url: source.url,
//       voted: undefined
//     })
//   }

//   vote(val){
//     if (this.state.voted !== val){
//       this.setState({
//         voted: val,
//         votes: this.state.votes + val * (this.state.voted===undefined ? 1 : 2)
//       })
//     }
//     if (this.state.voted === val){
//       this.setState({
//         voted: undefined,
//         votes: this.state.votes - val
//       })
//     }
//   }

//   render(){
//     return (
//       <div className="source">
//         <img src={this.state.img} aria-label={"Movie can be found at " + this.state.url + (this.state.subtype? " (" + this.state.subtype + ")" : "" )}/>
//         <span id="votes" aria-label={"Current Votes for this Source: "+this.state.votes}>{this.state.votes}</span>
//         <span id="voter" className={this.state.voted !== undefined ? "active": ""}>
//           <span className={this.state.voted==-1 ? "active": ""}><ThumbDown title="Downvote this source." aria-label="Downvote this source." onClick={()=>{this.vote(-1)}} /></span>
//           <span className={this.state.voted==1 ? "active": ""}><ThumbUp title="Upvote this source." aria-label="Upvote this source." onClick={()=>{this.vote(1)}} /></span>
//         </span>
//       </div>
//     )
//   }
// }

export default Source