import pyrebase
config = {
  "apiKey": "AIzaSyBKX1xmfY8JuhIbgOxhO2APg6f4VcCZWXI",
  "authDomain": "luminous-inferno-9831.firebaseapp.com",
  "databaseURL": "https://luminous-inferno-9831.firebaseio.com",
  "storageBucket": "luminous-inferno-9831.appspot.com",
};
firebase = pyrebase.initialize_app(config)
fdb = firebase.database()


def fb_notification(recipient=None,message=None,created_at=None,custom={},step=0):
    custom['ignore'] = True
    fdbdata = {
        'recipient':recipient,
        'message': message,
        'created_at': created_at,
        'custom': custom
    }
    fdb.child("notification").push(fdbdata)
