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
