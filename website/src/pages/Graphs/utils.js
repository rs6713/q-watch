import {interpolateRainbow, interpolateWarm} from 'd3-scale-chromatic';
import * as d3 from 'd3';
var resizeGraph = (setGraphDimensions) => {

  return () => {
  var throttled = false;
  // https://bencentra.com/code/2015/02/27/optimizing-window-resize.html
  function handleResize() {

    if (!throttled) {
      console.log('resize')
      let graphContainer = document.getElementsByClassName('Graph')[0];
      let graphStyle = getComputedStyle(graphContainer);
      var paddingX = parseFloat(graphStyle.paddingLeft) + parseFloat(graphStyle.paddingRight);
      var paddingY = parseFloat(graphStyle.paddingTop) + parseFloat(graphStyle.paddingBottom);

      setGraphDimensions({
        height: graphContainer.clientHeight - paddingY,
        width: graphContainer.clientWidth - paddingX
      })

      // we're throttled!
      throttled = true;
      // set a timeout to un-throttle
      setTimeout(function() {
        throttled = false;
      }, 250);
    }
  }
  window.addEventListener('resize', handleResize)
  handleResize();

  return _ => {
    window.removeEventListener('resize', handleResize)
  }
}
}

function getColorScale(keys){
  let lenKeys = keys.length
  let cs = [];
  for (let i = 0; i< lenKeys; i++){
    cs.push(interpolateWarm(i/lenKeys))
  }
  return d3.scaleOrdinal()
  .domain(keys)
  .range(cs)

}
export {
  getColorScale
}

export default resizeGraph