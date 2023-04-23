
var formatRuntime = function(runtime){
  var hours = Math.floor(runtime / (60));
  var minutes = Math.floor( runtime % (60));
  if(hours === 0){
    return String(minutes) + "min";
  }

  return (String(hours) + "hr " + String(minutes) + "min");
}

export {formatRuntime};
