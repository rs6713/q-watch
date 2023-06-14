import React, {useState, useEffect} from 'react';
import {ReactComponent as ThumbDown} from '../../static/icons/thumbdown.svg';
import {ReactComponent as ThumbUp} from '../../static/icons/thumbup.svg';
import Lgbt from '../../static/images/lgbt-flag.png'
import Button from './Button';

import {ReactComponent as Caret} from '../../static/icons/direction.svg'
import {ReactComponent as Neutral} from '../../static/icons/neutral.svg'

function Delta({number}){
  if(number == 0){
    return <span className='deltaSymbol'><Neutral /></span>
  }
  if(number < 0){
    return <span className='deltaSymbol negative'><Caret/></span>
  }
  return <span className='deltaSymbol positive'><Caret/></span>
}

function Source({source}){

  const [votes, setVotes] = useState(0);
  const [voted, setVoted] = useState(
    localStorage.getItem(`movie_source_${source.ID}_vote_value`) || 0
  );

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

    function getPrice(){
      if(source.MEMBERSHIP_INCLUDED){
        return 'Membership Included'
      }
      if(source.COST == 0){
        return 'Free'
      }
      return '£' + source.COST
    }

    return (
      <div className="source">
        <img src={'/sources/' + source.IMAGE} aria-label={"Movie can be found at " + source.URL + (source.REGION? " (" + source.REGION + ")" : "" )}/>
        <div className='description'>
          <h2>
            {source.LABEL}{source.REGION && ' ('+source.REGION + ')'}
            {source.LGBT_RUN && <span className='explainer'>
              <img src={Lgbt} alt='This OnDemand Streaming Service is LGBT run!'/>
              <span>This OnDemand Streaming Service is LGBT run!</span>
            </span>}

          </h2>
          <div>
            <div className='price'>
              <span>Price</span><br/>
              <span>{getPrice()}</span>
            </div>
            {source.URL && <a target='_blank' href={source.URL}><Button onClick={()=>{}} text='Link' /></a>}
            <div className='source_voting'>
              <span id="votes" aria-label={"Current Votes for this Source: "+ votes}>{votes?  <span><Delta number={Math.abs(votes)} />{votes}</span> : 'No Votes'}</span>
              <span id="voter" className={voted !== 0 ? "active": ""}>
                <span className={voted==-1 ? "active": ""}><ThumbDown title="Downvote this source." aria-label="Downvote this source." onClick={()=>{updateVoted(voted == -1 ? 0 : -1)}} /></span>
                <span className={voted==1 ? "active": ""}><ThumbUp title="Upvote this source." aria-label="Upvote this source." onClick={() => {updateVoted(voted == 1? 0: 1)}} /></span>
              </span>
            </div>
          </div>
        </div>
      </div>
    )
}



export default Source