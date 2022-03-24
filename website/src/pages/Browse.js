import React, { Component } from 'react';
import {Link} from 'react-router-dom';
import Footer from './components/Footer';
import Rating from './components/Rating';
import Filters from './components/Filters';
import {ReactComponent as Caret} from '../static/icons/caret.svg'
import {ReactComponent as Filter} from '../static/icons/filter.svg'

var movies = [
  {
    id: 1,
    title: "But I'm a Cheerleader",
    year: "1999",
    rating: 4.5,
    bio: "A popart, lesbian classic, an all-american cheerleader must attend conversion therapy.",
    screenshot: 'movie-pictures/but-im-a-cheerleader-001.webp',
    category: ["Comedy", "Cult Classic", "Romance"]
  },
  {
    id: 2,
    title: "Blue is the warmest color",
    year: "2013",
    rating: 3.5,
    bio: "If the male gaze were a love scene.",
    screenshot: '/movie-pictures/blue-is-the-warmest-color-000.jpg',
    category: ["Drama", "Romance"]
  },
  {
    id: 3,
    title: "Desert Hearts",
    year: "1985",
    rating: 4.7,
    bio: "Who knew it could be so wet in the desert.",
    screenshot: '/movie-pictures/desert-hearts-000.jpg',
    category: ["Drama", "Romance", "Cult Classic"]
  },
  {
    id: 4,
    title: "Imagine me and you",
    year: "2007",
    rating: 4.5,
    bio: "A woman meets the gaze of a florist, there's just one problem, she's already walking down the aisle.",
    screenshot: 'movie-pictures/imagine-me-and-you-000.jpg',
    category: ["Comedy", "Romance", "Cult Classic"]
  },
  {
    id: 5,
    title: "Rafiki",
    year: "2018",
    rating: 4.8,
    bio: "Against the backdrop and LGBT rights in Kenya, two girls love.",
    screenshot: 'movie-pictures/rafiki-000.jpg',
    category: ["Drama", "Romance"]
  },
  {
    id: 6,
    title: "D.E.B.S",
    year: "2004",
    rating: 4.8,
    bio: "The one who is best at lying, lies best to themselves.",
    screenshot: "movie-pictures/debs-000.png",
    category: ["Cult Classic", "Comedy", "Romance"]
  },
  {
    id: 7,
    title: "Lost and Delirious",
    year: "2001",
    rating: 2.7,
    bio: "The girls boarding school dream.",
    screenshot: "/movie-pictures/lost-and-delirious-000.jpg",
    category: ["Drama"]
  },
  {
    id: 7,
    title: "Ammonite",
    year: "2021",
    rating: 4.7,
    bio: "An overlooked Geologist discovers there is more to life than fossils. (pussy)",
    screenshot: "/movie-pictures/ammonite-000.jpg",
    category: ["Drama", "Period-Piece", "Romance"]
  }
]
const SORT = {
  "Most Popular": ("views", -1),
  "Least Popular": ("views", 1),
  "Highest Rating": ("rating", -1),
  "Lowest Rating": ("rating", 1),
  "Most Recent Release": ("year", -1),
  "Least Recent Release": ("year", 1)
}

const filterConfig = {
  title: "Movie Filters",
  filterSections:[
    {
      title: "By Women for Women",
      type: "checkbox",
      filters:[
        {
          label: "Female Director",
          id: "female_director",
          descrip: "The movie is directed by a woman"
        },
        {
          label: "Female Writer",
          id:"female_writer",
          descrip: "The movie is written by a woman"
        }
      ]
    },
    {
      title: "Movie Qualities",
      filters: [
        {
          label: "Age Range",
          id: "age_range",
          type: "slider",
          options: ["Coming of Age", "Young Adult", "30-60", "60+"]
        },
        {
          label: "Language",
          id: "language",
          type: "dropdown",
        },
      ]
    },
    {
      title: "Tropes / Trigger Warnings",
      expandable: true,
      warning: "IMPLIED SPOILERS",
      subtitle: "Early mainstream, queer media was messy at best. Select the tropes you wish to avoid.",
      type: "bubble",
      filters:[
        {
          label: "Teacher/Student",
          id:"teacher_student",
          descrip: "Because it's illegal"
        },
        {
          label: "Lesbian Bed death",
          id: "lesbian_bed_death"
        },
        {
          label: "Bury your gays",
          id: "bury_your_gays"
        },
        {
          label: "Sexual Violence",
          id: "sexual_violence"
        },
        {
          label: "Suicide",
          id: "suicide"
        },
        {
          label: "Conversion Therapy",
          id: "conversion_therapy"
        },
        {
          label: "Hate Crimes",
          id: "hate_crimes"
        },
        {
          label: "They don't end up together.",
          id: "lonely_lesbians"
        },
        {
          label: "Unaccepting Family/Disowning",
          id: "family_troubles"
        },
        {
          label: "Bi Erasure",
          id: "bi_erasure"
        },
        {
          label: "It was just a phase",
          id: "it_was_a_phase"
        }
      ]
    },
    {
      title: "Representation Matters",
      subtitle: "See yourself on the bigscreen. We have tried our best, but if you feel we are missing filters here, please let us know, email us at q-watch.gmail.com.",
      disclaimers: [
        "Unfortunately some options may be missing or extremely broad, due to a lack of representation in the media itself.",
        "Representation here, guarantees presence, but not good representation: see tropes/trigger warnings."
      ],
      type: "bubble",
      filters: [
        {
          label: "Black Love",
          id: "blackLove",
          descrip: "Black characters loving black characters."
        },
        {
          label: "QTIPOC",
          id: "qtipoc",
          descrip: "At least one of the main characters is POC"
        },
        {
          label: "Transgender",
          id: "transgender",
          descrip: "At least one of the main characters is trans"
        },
        {
          label: "Disability",
          id: "disability",
          descrip: "At least one of the main characters is disabled"
        },
        {
          label: "Butch",
          id: "butch",
          descrip: "At least one of the main characters is butch"
        },
        {
          label: "Bisexual",
          id: "bisexual",
          descrip: "At least one of the main characters is bisexual"
        },
        {
          label: "Polyamory",
          id: "polyamory",
          descrip: "The relationship is polyamorous"
        },
        {
          label: "Jewish",
          id: "jewish",
          descrip: "At least one of the main characters is jewish"
        }
      ]
    },
    {
      title: "Not finding what you're looking for?",
      subtitle: "Unfortunately Queer cinema (like most media) can be majority homogeneous. Allowing these options, may help you find more movies for specific demographics/story types",
      type: "checkbox",
      filters:[
        {
          label: "Queer Love can be Side Stories/Characters",
          id: "allowSideCharacters"
        },
        {
          label: "Queerness can be implied (only)",
          id: "allowImplied"
        }
      ]
    }
  ]
}



class Browse extends Component {
  constructor(props){
    super(props)
    this.state = {
      category: null,
      categories: ["All", "Romance", "Drama", "Comedy", "Sci-Fi", "Period-Piece", "Horror", "Cult Classic"],
      filterActive: false,
    }
  }

  componentDidMount(){
    this.getCategories();
  }

  getCategories(){
    this.setState({
      "categories": ["Romance", "Drama", "Comedy", "Sci-Fi", "Period-Piece", "Horror", "Cult Classic"]
    })
  }

  getMovies () {

  }

  render () {
    return (
        <div id="Browse" className="page">
          <Filters />
          <div id="ControlPanel">
            <div id="Sort">
              <div>Sort <Caret/></div>
              <ul id="SortOptions">
                {Object.keys(SORT).map(key => (
                  <li key={key} onClick={()=>{this.setState({'sort': SORT[key]})}}>{key}</li>
                ))}
              </ul>
            </div>
            <div id="Categories">
              <div className={!this.state.category? 'active': ''}  onClick={()=>{this.setState({category: null})}}>All</div>
              {this.state.categories.map(category => (
                <div className={this.state.category==category? 'active' : ''} onClick={()=>{this.setState({category:category })}} >{category}</div>
              ))}
            </div>
            <div id="FiltersToggle" onClick={()=>{this.setState({"filterActive": !this.state.filterActive})}} className={!this.state.filterActive? 'active': ''} ><Filter/>Filters</div>
          </div>
          <div id="BrowseResults">
            {movies.filter(movie=>(
                !this.state.category || movie.category.indexOf(this.state.category) != -1
              )).length==0 && <div id="alert">
                We are sorry we could find no titles matching your search criteria.
                To learn more about the state of lesbian cinema, click here.
                Otherwise, similar searches with results are:  
              </div>}

            {
              movies.filter(movie=>(
                !this.state.category || movie.category.indexOf(this.state.category) != -1
              )).map(movie => (
                <Link to={'/movies/'+movie.id}>
                  <div className="movietile">
                    <div className="screenshot" style={{backgroundImage: 'url(' + movie.screenshot + ')'}} />
                    <div className="description">
                      <h3>{movie.title}</h3>
                      <p> {movie.bio}</p>
                    </div>
                    <span>{movie.year}</span>
                    <Rating score={movie.rating} rotated={true}/ >
                  </div>
                </Link>
              ))
            }
          </div>
          <div className="spacer"/>
          <Footer />
        </div>
    )
  }
}

export default Browse