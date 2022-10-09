import { useEffect, useState } from 'react';
import Image from './components/Image';
import {Link} from 'react-router-dom';
import Search from '../pages/components/Search';
import '../App.scss'

const PHRASES = [
  "**I will go down with this ship.... (screams in Dido)**",
  "Come for the lesbians. Stay for the lesbians.",
]

function Main(){
  const [movieGif, setMovieGif] = useState(null);

  //Data Fetching Called once at mount/dismount
  useEffect(() => {
    fetch(`/api/gif/random`, {
      method: 'GET',
      headers: {
        'cache-control': 'no-store',
      }
    }).then(res => res.json()).then(data => {
      setMovieGif(data);
    })
  }, []);

  var backgroundDiv = <div className="background"></div>
  if(movieGif !== null){
    backgroundDiv = <div className="background image">
      {Image(movieGif.FILENAME, movieGif.CAPTION)}
    </div>
  }
  

  return (
    <div id="Main" className="page">
      <div id="TitlePage">
        {backgroundDiv}
        <div id="Title" >
          <h1>Q-WATCH</h1>
          <Search placeholder="Query Queer Watches" />
        </div>
        {movieGif !== null && 
          <div id="MovieInfo">
            <Link to={"/movies/" + movieGif.MOVIE_ID} >
              <h3>{movieGif.TITLE}</h3>
              <h3>{movieGif.YEAR}</h3>
            </Link>
          </div>
        }
      </div>
    </div>
  )
}

// class Main extends Component {
//   constructor(props){
//     super(props)
//     this.state={

//     }
//   }

//   loadBackground(){
//     //TODO: Get images from server side
//     var movies = [
//       {
//         "gif": 'debs-000.gif',
//         "year": 2004,
//         "title": "D.E.B.S",
//         "id": 5
//       },
//       {
//         "gif": 'desert-hearts-000.gif',
//         "year": 1986,
//         "title": "Desert Hearts",
//         "id": 5
//       },
//       {
//         "gif": 'i-cant-think-straight-000.webp',
//         "year": 2009,
//         "title": "I can't think straight",
//         "id": 5
//       },
//       {
//         "gif": 'rafiki-000.gif',
//         "year": 2018,
//         "title": "Rafiki",
//         "id": 5
//       },
//       {
//         "gif": 'ammonite-000.gif',
//         "year": 2021,
//         "title": "Ammonite",
//         "id": 8
//       },
//     ]
//     var randIndex = Math.floor(Math.random()*movies.length);
//     this.setState({
//       movie: movies[randIndex]
//     })
//   }

//   componentWillMount(){
//     this.loadBackground()
//   }
  
//   render () {
//     //'url(../static/' + this.state.backgroundgif + ')'
//     return (

//     )
//   }
// }

export default Main