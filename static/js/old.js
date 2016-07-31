// START
var GLOBAL_LAT = 0;
var GLOBAL_LON = 0;
var GLOBAL_EMAIL = "{{user_email}}";
var GLOBAL_UID = {{user_id}};
var GLOBAL_NAME = "{{user_name}}";
var GLOBAL_TIME = 0;
var config = {
  apiKey: "AIzaSyBKX1xmfY8JuhIbgOxhO2APg6f4VcCZWXI",
  authDomain: "luminous-inferno-9831.firebaseapp.com",
  databaseURL: "https://luminous-inferno-9831.firebaseio.com",
  storageBucket: "luminous-inferno-9831.appspot.com",
};
firebase.initializeApp(config);
var bumpsRef = firebase.database().ref('bumps/');
var timeLimit = "this value should be the current time minus 5 minutes";
var options = {
  enableHighAccuracy: true,
  timeout: 5000,
  maximumAge: 0
};
if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(success, failure, options);
} else {
  alert("We need your location");
}
function success(position) {
  GLOBAL_LAT = position.coords.latitude;
  GLOBAL_LON = position.coords.longitude;
  console.log("achieved position");
  console.log(GLOBAL_LAT + " / " + GLOBAL_LON)
}
function failure(err){
  console.warn('ERROR(' + err.code + '): ' + err.message);
}


bumpsRef.orderByChild("time").startAt(1468707770420).on('child_added', function(data) {
  bumps = data.val();
  console.log(bumps);
  if (bumps['to']['email'] == GLOBAL_EMAIL) {
    postData = {
      'uone':bumps['to'],
      'utwo':bumps['from']
    }
    // clear html and move user to "match found"
    // then clear html and move user to "generating playlist"
    // $.ajax({
    //   url: '/algorithm/generation',
    //   data: postData,
    //   type: 'POST',
    //   success: function(response) {
    //     location.href = '/playlist/'+response.playlist_id.toString();
    //   },
    //   error: function(error) {
    //     alert('something broke');
    //   }
    // });
  }
});
function writeNewPost(data) {
  var updates = {};
  var bumpPostKey = firebase.database().ref().child('bumps').push().key;
  updates['/bumps/' + bumpPostKey] = data;
  return firebase.database().ref().update(updates);
}

$(document).ready(function(){

  $("a").on('click',function(event){
    event.preventDefault();
    var d = new Date();
    var diss = $(this);
    GLOBAL_TIME = d.getTime();
    GLOBAL_TO_EMAIL = diss.attr('data-email');
    GLOBAL_TO_ID = parseInt(diss.attr('data-id'));

    var postData = {
      "from": {'id': GLOBAL_UID,'email':GLOBAL_EMAIL},
      "to": {'id':GLOBAL_TO_ID,'email':GLOBAL_TO_EMAIL},
      "lat": GLOBAL_LAT,
      "lon": GLOBAL_LON,
      "time": GLOBAL_TIME
    };
    firePost = writeNewPost(postData).then(function(){
      // alert('this is when we would clear the html');
      var dddata = {
        'uone':{'id':7,'email':'dlamnguyen@gmail.com'},
        'utwo':{'id':8,'email':'eat@rad.kitchen'},
        'time': GLOBAL_TIME,
        'location': 'yup'
      }
      $.ajax({
        url: '/algorithm/generation',
        data: JSON.stringify(dddata),
        contentType:"application/json",
        // issue here.....
        type: 'POST',
        success: function(response) {
          // algorithm must generate playlist, then insert playlist into table so we can call it later
          // after success we will navigate user to /playlist/playlist_id
          location.href = '/playlist/'+response.payload.toString();
        },
        error: function(error) {
          // alert("NO");
          console.log(error)
          alert('something broke');
        }
      });
    });
  });
});
// END
var config = {
  apiKey: "AIzaSyBKX1xmfY8JuhIbgOxhO2APg6f4VcCZWXI",
  authDomain: "luminous-inferno-9831.firebaseapp.com",
  databaseURL: "https://luminous-inferno-9831.firebaseio.com",
  storageBucket: "luminous-inferno-9831.appspot.com",
};
firebase.initializeApp(config);
var commentsRef = firebase.database().ref('matches/');
commentsRef.endAt().limit(1).on('child_added', function(data) {
  console.log("child added?");
  var uone_name = data['uone_name'];
  var utwo_name = data['utwo_name'];
  if (GLOBAL_NAME !=""){
    if (GLOBAL_NAME == utwo_name || GLOBAL_NAME == uone_name){
      alert("GOTTA CATCH THEM ALL");
    }
  }
});

function writeNewPost(uid,email, name, lat,lon,time) {
  var updates = {};
  var postData = {
    uid: uid,
    email: email,
    name: name,
    lat: lat,
    lon: lon,
    time: time
  };
  var bumpPostKey = firebase.database().ref().child('bumps').push().key;
  updates['/bumps/' + bumpPostKey] = postData;
  return firebase.database().ref().update(updates);
}
