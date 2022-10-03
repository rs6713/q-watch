
var formatRuntime = function(runtime){
  var hours = Math.floor(runtime / (60));
  var minutes = Math.floor( runtime % (60));

  return (String(hours) + "hr " + String(minutes) + "min");
}

export {formatRuntime};
