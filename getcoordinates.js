var Firebase = require("firebase");
var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;

// URL to the google maps geocode API
var geocodeUrl = "https://maps.googleapis.com/maps/api/geocode/json?address=",
    key = "&region=nl&key=AIzaSyCGpwpuw7Pi3wfrGRmj51sEJ0Lsyo5rL6Q";

var database = new Firebase("https://visualmetalarchives.firebaseio.com");

// Get Coordinates
function getCoordinatesOf(location) {
  var request = new XMLHttpRequest();
  var query = "";

  if (location != undefined) {
    location = location.split('/');
    query = geocodeUrl + location[0] + key;

    // Send request
    request.open("GET", query, false);
    request.send();

    // Converts invalid json to for realsies json
    var results = JSON.stringify(eval("(" + request.responseText + ")"));
    json = JSON.parse(results);
    
    if (json.results[0] != undefined){
      return json.results[0].geometry.location;
    }
    else {
      return {lat: 0, lng: 0};
    }
  }
  else {
    return {lat: 0, lng: 0};
  }
}

// Get bands
function getBands() {
  var request = new XMLHttpRequest();

  request.open("GET", "https://visualmetalarchives.firebaseio.com/.json", false);

  request.send();

  // Converts invalid json to for realsies json
  var results = JSON.stringify(eval("(" + request.responseText + ")"));
  var bands = JSON.parse(results);

  // Get that J Son
  return bands;
}

var Coordinates = [];
var bands = getBands();

// Get the coordinates of those bands in the list of bands
for(var band in bands) {
  coordinates = getCoordinatesOf(bands[band].location);
  console.log(bands[band].name);
  Coordinates.push(coordinates);
}

// Write to Database
for(var e = 0; e < Coordinates.length; e++){
  database.child(e).update({"lat": Coordinates[e].lat, "lng": Coordinates[e].lng});
  console.log(Coordinates[e]);
}

