import React from 'react';

import Footer from './components/Footer'

const question_answers = [
  [
    'What is the goal of this project?',
    'The goals of this project are twofold: to create an easy, searchable way to help LGBTQIA+ people find movies representative of their identities and lived experiences, and to analyse the  data we\'ve collected in this process, to do a comprehensive analysis of the state of Queer Cinema.'
  ],
  [
    'What kinds of media does this Archive Contain?',
    'This archive is for LGBTQIA+ movies, short films and stand-alone episodes of television. We\'d never abandon you San Junipero! our Sci-Fi section wouldn\'t be the same without you.'
  ],
  [
    'Why don\'t you have LGBTQIA+ TV Shows?',
    'That sounds like a lot of work ... Not categorizing movies though, twas barely two shakes of a lamb\'s tail, it was.'
  ],
  [
    'My company wants to sponsor your amazing project, you entrepeneurial fellows you..',
    'Omggg bestie stawp... Please email us at qwatchbusiness69@gmail.com, because apparently you can\'t pay your server bills in hugs, good vibes and **checks list** the desire to be the change you want to see in the world.'
  ],
  [
    'Why do you have so few Gay Male movies compared to what\'s out there?',
    'We made the decision to prioritize LGBTQIA+ movies in all other categories for several reasons:<br/> Firstly from a practical standpoint, we were more familiar with those movies making them easier to enter into the database. <br/>Secondly Gay Cis Men, are typically the "best served" in the media space (a game of empty victories we know), with the greatest number of movies, making achieving representative coverage more of a challenge. Building on that, ultimately the greatest goal of this project is to help people who struggle to find themselves onscreen, do just that, so we prioritized those groups who felt this pain most acutely. Honestly there are like 3 aro/ace movies, it took us barely an hour.'
  ],
  [
    'Why don\'t you have [insert movie name here]?',
    'We are constantly adding new movies to the archive; even with semi-automation it takes approximately 20-30 minutes to add a new movie so please be patient with us. Send us your suggestions at qwatchbusiness69@gmail.com, and we can prioritise them.'
  ],
  [
    'How did you compile this Queer Archive?',
    'We used a combination of web scraping (for quotes, DOB\'s, movie summaries, box office figures), manual data entry (for identities, representations, tropes/triggers) and automated google image searches with manual image description labelling. For those that care, we built the databases using Microsoft SQL Server, the data entry UI in tkinter, server in Flask and FrontEnd in React. Yes, we regret our decisions too, dont\'t @ us.'
  ],
  [
    'Heyyyy, [movie x] doesn\'t have any trans people in it, but it is under Transgender??',
    'The beauty of manual data entry is that we can add labels/information we frankly never want AI to touch. A drawback is humans are fallible, and apparently we can\'t fire ourselves. Please email us at qwatchbusiness69@gmail.com, we can make these kinds of corrections in seconds and are happy to do so. We\'ve endeavoured to do our due diligence, but we count on our community to help us fill in gaps #nopressure'
  ],
  [
    'I dislike part of this site or have a bug to report',
    'We welcome feedback, this is the BETA release after all. Preferred terminology is constantly changing, and we\'re certain their are many places our data and website can be improved. Please email us at <b>qwatchbusiness69@gmail.com</b>, but please be aware it may not be possible to satisfy all members of our community\'s preferences.'
  ],
  [
    'I have a great idea for a new feature..',
    'And they say Steve Jobs is dead.. in all seriousness, please email us at qwatchbusiness69@gmail.com, we truly value all your inputs. We may even be open to collaboration in the future, however the 90\'s stranger danger scare hit us pretttty harrrrdd so our anxiety promises you nothing <3'
  ],
  [
    'What\'s Next?',
    'MORE MOVIES!! That\'t our top priority right now. We want to get to at least 300 movies by the end of year. We cannot effectively evaluate the state of Queer Cinema and how it\'s changing over time without comprehensive movie coverage. Not to mention our primary function, of creating a searchable archive has meant we\'re prioritizing the addition of movies representing further marginallized communities, skewing our datasets to say the least, in these early stages.'
  ],
  [
    'Isn\'t qwatchbusiness69@gmail.com a little unprofessional?',
    'All the professional emails were taken. We blame capitalism and two factor authentication.'
  ]
]

function FAQ(){

  return (
    <div className='page' id='faq'>
      <h2>FAQ</h2>
      <div>
        <ul>
          {question_answers.map((qa, _) => <li>
            <h3>{qa[0]}</h3>
            <p>{qa[1]}</p>
          </li>)}
        </ul>
      </div>
      <Footer />
    </div>
  )

}

export default FAQ