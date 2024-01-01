

function Alert({header, subtitle}){
  return <div className='alert'>
    <h2 className='bubbletext'>{header}</h2>
    <p>{subtitle}</p>
  </div>
}

export default Alert