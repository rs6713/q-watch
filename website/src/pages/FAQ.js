import React, {useState} from 'react';

import MainMenu from './components/MainMenu';
import Footer from './components/Footer';
import {ReactComponent as Plus} from '../static/icons/plus.svg'
import {ReactComponent as Minus} from '../static/icons/minus.svg'


const question_answers = [
  [
    'What is the goal of this project?',
    (<div>The goals of this project are twofold:<ul>
      <li>to create an easy, searchable way to help LGBTQIA+ people find movies representative of their identities and lived experiences</li><li>to analyse the data we've collected in this process, to do a comprehensive analysis of the state of Queer Cinema.</li></ul>
      </div>)
  ],
  [
    'What kinds of media does this Archive Contain?',
    (<div><b>This archive is for LGBTQIA+ movies, short films and stand-alone episodes of television. </b><br/>We'd never abandon you San Junipero! our Sci-Fi section wouldn't be the same without you.</div>)
  ],
  [
    'Why don\'t you have LGBTQIA+ TV Shows?',
    (<div>That sounds like a lot of work ...</div>)
  ],
  [
    'My company wants to sponsor your amazing project, you entrepeneurial fellows you..',
    (<div>Omggg bestie stawp ... <b>Please email us at qwatchbusiness69@gmail.com</b>, because apparently you can't pay your server bills in hugs, good vibes and <i>**checks list**</i> the desire to be the change you want to see in the world.</div>)
  ],
  [
    'Why do you have so few Gay Male movies compared to what\'s out there?',
    (<div>We made the decision to prioritize LGBTQIA+ movies in all other categories for several reasons:<br/><ol>
      <li>Gay Cis Men, are typically the "best served" in the media space (a game of empty victories we know), with the greatest number of movies, making achieving representative coverage more of a challenge.</li><li> Building on that, ultimately the greatest goal of this project is to help people who struggle to find themselves onscreen, do just that, so we prioritized those groups who felt this pain most acutely. Honestly there are like 3 aro/ace movies, it took us barely an hour.</li></ol></div>)
  ],
  [
    'Why don\'t you have [insert movie name here]?',
    (<div>We are constantly adding new movies to the archive but even with semi-automation it takes  ~10-20 minutes to add a new movie, so please be patient with us. <br/><b>Send us your suggestions at qwatchbusiness69@gmail.com</b>, and we can prioritise them.</div>)
  ],
  [
    'How did you compile this Queer Archive?',
    (<div>We used a combination of web scraping (for quotes, DOB's, movie summaries, box office figures), manual data entry (for identities, representations, tropes/triggers) and automated google image searches with manual image description labelling. <br/><br/>For those that care, we built the databases using Microsoft SQL Server, the data entry UI in tkinter, server in Flask and FrontEnd in React. <br/><i>Yes, we regret our decisions too, dont't @ us.</i></div>)
  ],
  [
    'Heyyyy, [movie x] doesn\'t have any trans people in it, but it is under Transgender??',
    (<div>The beauty of manual data entry is that we can add labels/information we frankly never want AI to touch. A drawback is humans are fallible, and apparently we can't fire ourselves. <br/> <b>Please email us at qwatchbusiness69@gmail.com</b>, we can make these kinds of corrections in seconds and are happy to do so. <br/>We've endeavoured to do our due diligence, but we count on our community to help us fill in gaps #nopressure</div>)
  ],
  [
    'I dislike part of this site or have a bug to report',
    (<div>We welcome feedback, this is the <b>BETA</b> release after all. Preferred terminology is constantly changing, and we're certain there are many places our data and website can be improved.<br/><br/> <b>Please email us at qwatchbusiness69@gmail.com</b>, but please be aware it may not be possible to satisfy all members of our community's preferences.</div>)
  ],
  [
    'I have a great idea for a new feature..',
    (<div>And they say Steve Jobs is dead.. in all seriousness, <b>please email us at qwatchbusiness69@gmail.com</b>, we truly value all your inputs.<br/> We may even be open to collaboration in the future, however the 90's stranger danger scare hit us pretttty harrrrdd so our anxiety promises you nothing </div>)
  ],
  [
    'What\'s Next?',
    (<div><b>MORE MOVIES!!</b> That's our top priority right now. We want to get to at least 1000 movies by the end of year. <i>(The trick is not specifying whichh year)</i> <br/><br/>We cannot effectively evaluate the state of Queer Cinema and how it's changing over time without comprehensive movie coverage.<br/> Not to mention our primary function, of creating a searchable archive has meant we're prioritizing the addition of movies representing further marginallized communities, skewing our datasets to say the least, in these early stages.</div>)
  ],
  [
    'Isn\'t qwatchbusiness69@gmail.com a little unprofessional?',
    (<div>All the professional emails were taken. We blame capitalism and two factor authentication.</div>)
  ]
]

function DropDown({title, contents}){

  const [active, setActive] = useState(false);

  return (
    <div className='dropdown' onClick={()=>{setActive(!active)}} key={title}>

      <h3>
        <span>{title}</span>
        {active && <Minus title="" aria-label={"Click to hide answer"} />}
        {!active && <Plus title="" aria-label={"Click to see answer"}/>}
      </h3>
      <div className={active ? 'active': ''}>
        {contents}
      </div>
    </div>
  )
}

function FAQ(){

  return (
    <div className='page' id='faq'>
      <MainMenu/>
      <h2 className='bubbletext'>Frequently Asked Questions</h2>
      <h3>
        <span className='explainer'>
          Ya nosey parkers
          <span><b>Matthew Parker</b>, who was Archbishop of Canterbury (1559-75), had rather a reputation for prying into the affairs of others. He therefore acquired the nickname 'Nosey Parker'.</span> 
        </span>
      </h3>
      <div>
        {question_answers.map((qa, _) => <DropDown title={qa[0]} contents={qa[1]} key={qa[0]}/>)}
      </div>
      <Footer />
    </div>
  )

}

export default FAQ