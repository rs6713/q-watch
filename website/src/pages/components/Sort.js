
const SORT = {
  "Most Popular": ("NUM_RATING", -1),
  "Least Popular": ("NUM_RATING", 1),
  "Highest Rating": ["AVG_RATING", -1],
  "Lowest Rating": ["AVG_RATING", 1],
  "Most Recent Release": ["YEAR", -1],
  "Least Recent Release": ["YEAR", 1],
}

function Sort({updateSort}){
  return (
    <div id="Sort">
      <div>Sort <Caret/></div>
      <ul id="SortOptions">
        {Object.keys(SORT).map(key => (
          <li key={key} className={sort === key ? 'active' : ''} onClick={()=>{updateSort({"sort": SORT[key]})}}>{key}</li>
        ))}
      </ul>
    </div>
  )
}
