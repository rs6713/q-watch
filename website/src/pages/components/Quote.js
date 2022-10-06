

function Quote({quote}){
  if(quote === null || quote === undefined || quote.length === 0){
    return <></>
  }

  return (
    <div id="quote">
      {quote}
    </div>
  )
}

export default Quote