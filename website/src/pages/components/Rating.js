import React from 'react';
import {ReactComponent as Scissor} from '../../static/icons/scissor.svg';
// import {ReactComponent as ReactLogo} from './logo.svg';
//import '../../App.scss';

const Rating = (props) => {
  var max_score = 5;
  console.log(props)
  return (
    <div className="rating">
      <div>
        {[...Array(max_score)].map((_, idx) => {
          if (Math.ceil(props.score) < (1+idx)){
            return <Scissor style={{visibility: 'hidden'}} />
          }
          if (Math.ceil(props.score) == (1+idx)){
            if(props.rotated){
              return <Scissor style={{clipPath: 'inset(0 '+ (props.score - Math.floor(props.score))*100 + '% 0 0)'}}/>
            }else{
              return <Scissor style={{clipPath: 'inset(0 0 '+ (props.score - Math.floor(props.score))*100 + '% 0)'}}/>
            }
          }
          return <Scissor />
        }
        )}
      </div>
    </div>
  )
}

export default Rating