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
var d = new Date()
var chat = firebase.database().ref('/chat');
var vistor = {'uid':"{{user_id}}",'email':"{{user_email}}",'name':"{{user_name}}",'time':d.getTime(),'location':000}
var vistorRef = chat.push(vistor);
vistorRef.onDisconnect().remove();

function writeNewPost(data) {
  var updates = {};
  var bumpPostKey = firebase.database().ref().child('bumps').push().key;
  updates['/bumps/' + bumpPostKey] = data;
  return firebase.database().ref().update(updates);
}

$(document).on('ready',function(){
  count = 0;
  chat.on('child_added',function (snapshot){
    $('ul').append('<li id="'+ snapshot.key+'">'+'<a class="clickbait" data-email="'+ snapshot.val()['email']+'" data-id="'+snapshot.val()['uid'] +'"'+'>'+snapshot.val()['name']+'</a></li>');
    // $('.clickbait').on('click',yo);
    count = count + 1;
    console.log(count);
  });
  chat.on('child_removed', function (snapshot) {
    setTimeout(function(){
      $('#' + snapshot.key).remove(); 
    },300000);
  });
  $('ul').on('click', 'li a.clickbait', function(event) {
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
      location.href = '/loading/match/to/'+GLOBAL_TO_ID;
    });
  });
});