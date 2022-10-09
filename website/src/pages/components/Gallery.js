import Image from './Image';


function Gallery({images}){
  return <div className="Gallery">
    {images.map((img)=>(
      Image(img.FILENAME, img.CAPTION)
    ))}
  </div>
}

export default Gallery;