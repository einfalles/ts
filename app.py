import json
import httplib2
import gevent
import time
import pprint
import jsonify
import datetime
import pyrebase
import ts_auth as tsa
import ts_recommendations as tsr
import ts_models as tsm
import moment
import sys

from raygun4py import raygunprovider
from threading import Thread
from oauth2client import client
from flask_sse import sse
from flask import Flask, render_template, request, redirect, jsonify, session, url_for,send_file
from oauth2client.client import OAuth2Credentials
from oauth2client.contrib import multistore_file as oams
# from werkzeug.contrib.profiler import ProfilerMiddleware


#
# CONSTANTS
#

app = Flask(__name__, static_url_path='')
app.debug = True
raygun = raygunprovider.RaygunSender("aR9aPioLxr1y42IN3HqSnw==")

app.config['REFRESH_LIMIT'] = 15

app.secret_key = 'duylamduylam'
app.config['OAUTH_CREDENTIALS'] = {
    'google':{
        'id':'423012525826-42ued2niiiecpuvrehd445n83kt16ano.apps.googleusercontent.com',
        'secret':'e2oBEpfgl3HVwU94UjFolXL8'
    }
}
# app.config['PROFILE'] = True
# app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 604800
config = {
  "apiKey": "AIzaSyBKX1xmfY8JuhIbgOxhO2APg6f4VcCZWXI",
  "authDomain": "luminous-inferno-9831.firebaseapp.com",
  "databaseURL": "https://luminous-inferno-9831.firebaseio.com",
  "storageBucket": "luminous-inferno-9831.appspot.com",
};
firebase = pyrebase.initialize_app(config)
fdb = firebase.database()


#
# ROUTING
#
@app.route('/loaderio-c54d3912e32128c85bd19987caf3561e')
def loaderio():
    return send_file('/js/loaderio-c54d3912e32128c85bd19987caf3561e.txt', attachment_filename='loaderio-c54d3912e32128c85bd19987caf3561e.txt')

@app.route('/hardcode')
def pagi():
    return render_template('hardcode.html')

@app.route('/')
def index():
    # https://developers.google.com/api-client-library/python/auth/web-app#example
    if 'credentials' not in session:
        return render_template('index.html')

    if 'credentials' in session:
        user = tsm.get_user(email=session['credentials']['id_token']['email'])

        tsm.db.session.close()
        session['credentials']['id_token']['ts_uid'] = user.id
        session['credentials']['id_token']['avatar'] = user.avatar
        session.permanent = True

        store = oams.get_credential_storage(filename='multi.json',client_id=user.email,user_agent='app',scope=['https://www.googleapis.com/auth/userinfo.profile','https://www.googleapis.com/auth/youtube'])
        credentials = store.get()

        if (credentials.token_expiry - datetime.datetime.utcnow()) < datetime.timedelta(minutes=app.config['REFRESH_LIMIT']):
            credentials.refresh(httplib2.Http())
        if credentials.invalid == True:
            return redirect('/login')
        # if user is new then history run
        # if user hasn't signed in a day then thread history run
        # history_run(uid=user.id,uemail=user.email)
        # thr = Thread(target=history_run,args=[user.id,user.email])
        # thr.start()
        return render_template('home.html',user_name=user.name,user_email=user.email,user_id=user.id)

def history_run(uid=None,uemail=None):
    history = tsr.get_watch_history(user=uemail)
    if history != None:
        song = tsm.Song.query.filter_by(sp_uri=history[3]).first()
    else:
        song = None
    if song == None:
        song = tsm.Song(sp_uri=history[3],track=history[1],artist=history[0],yt_uri=history[2])
        tsm.db.session.add(song)
        tsm.db.session.flush()
    t = moment.utcnow().datetime.isoformat()
    h = tsm.History(uid=uid,sid=song.s_id,created_at=t)
    tsm.db.session.add(h)
    tsm.db.session.commit()
    tsm.db.session.close()

# sign in
@app.route('/auth')
def auth():
    oauth = tsa.OAuthSignIn.get_provider("google")
    credentials = oauth.callback()
    session['credentials'] = json.loads(credentials.to_json())
    user_email = session['credentials']['id_token']['email']
    user_name = session['credentials']['id_token']['name']
    session['credentials']['id_token']['new'] = False
    store = oams.get_credential_storage(filename='multi.json',client_id=user_email,user_agent='app',scope=['https://www.googleapis.com/auth/userinfo.profile','https://www.googleapis.com/auth/youtube'])
    store.put(credentials)

    user = tsm.get_user(email=user_email)
    if user == None:
        session['credentials']['id_token']['new'] = True
        user = tsm.User(user_name,user_email,'http://thecatapi.com/api/images/get?format=src&amp;type=gif')
        tsm.db.session.add(user)
        tsm.db.session.commit()
        # return redirect('/setup')
    session.permanent = True
    return redirect("/")

@app.route('/login')
def login():
    oauth = tsa.OAuthSignIn.get_provider("google")
    return redirect(oauth.authorize())

# manage playlists
@app.route('/playlist/management/<uid>', methods=['GET','POST'])
def manage_playlist(uid):
    playlists = tsm.get_all_playlists(user_id=uid)
    tsm.db.session.close()
    return render_template('playlists.html',playlists=playlists,uid=uid)

@app.route('/playlist/<pl_id>')
def view_playlist(pl_id):
    songs = tsm.get_playlist_songs(pl_id=pl_id)
    url = tsm.get_playlist_url(pl_id=pl_id)
    user = session['credentials']['id_token']
    other = songs[0]['uone']
    if str(user['ts_uid']) == str(other.id):
        other = songs[0]['utwo'].name
    tsm.db.session.close()
    return render_template('playlist_songs.html', songs=songs,pl=url.url,other=other)

# manage account
@app.route('/profile/management/<uid>')
def profile_management(uid):
    user = tsm.get_user(uid=uid)
    tsm.db.session.close()
    return render_template('profile.html', uid=uid,user_avatar=user.avatar,user_name=user.name)

@app.route('/profile/management/name')
def profile_name():
    user = session['credentials']['id_token']
    print(user['ts_uid'])
    return render_template('profile_name.html',user_name=user['name'],uid=user['ts_uid'])

@app.route('/profile/management/avatar')
def avatar_gender():
    user = session['credentials']['id_token']
    return render_template('avatars.html')

@app.route('/profile/management/avatar/<gender>')
def avatar_selection(gender):
    f = list(range(0,20))
    user = session['credentials']['id_token']
    return render_template('avatar_selection.html',uid=user['ts_uid'],gender=gender,f=f)

@app.route('/profile/update/<edit>/<uid>', methods=['POST'])
def avatar_update(edit, uid):
    if edit == 'name':
        tsm.User.query.filter(tsm.User.id==uid).update({'name':request.json['name']})
        tsm.db.session.commit()
        session['credentials']['id_token']['name'] = request.json['name']
        tsm.db.session.close()
        return jsonify({'status':'ok'})
    if edit == 'avatar':
        tsm.User.query.filter(tsm.User.id==uid).update({'avatar':request.json['avatar']})
        tsm.db.session.commit()
        session['credentials']['id_token']['avatar'] = request.json['avatar']
        tsm.db.session.close()
        return jsonify({'status':'ok'})

# make a playlist
@app.route('/generate/one', methods=['GET','POST'])
def generate_select():
    if request.method == "POST":
        return jsonify({'status':'ok'})
    if request.method == "GET":
        user = session['credentials']['id_token']
        return render_template('generate_one.html',user_id=user['ts_uid'],user_email=user['email'],user_name=user['name'])

@app.route('/generate/two/<uid>',methods=['GET','POST'])
def generate_match(uid):
    if request.method == "POST":
        return jsonify({'status':'ok'})
    if request.method == "GET":
        user = session['credentials']['id_token']
        other = tsm.get_user(uid=uid)
        tsm.db.session.close()
        return render_template('generate_two.html',user_id=user['ts_uid'],user_email=user['email'],user_name=user['name'],to_id=other.id,to_email=other.email,to_name=other.name)


@app.route('/generate/three', methods=['POST'])
def generate_recommendation():
    # prepare data for run_generation
    print('generating recommendation',file=sys.stderr)
    time = moment.utcnow().datetime.isoformat()
    location = request.json['location']
    uone = request.json['uone']
    utwo = request.json['utwo']
    hone = tsm.get_history(uone['id'])
    htwo = tsm.get_history(utwo['id'])

    # run_generation wraps all of the steps necessary to generate recommendation
    data = tsr.run_generation(uone,utwo,hone.song.sp_uri,htwo.song.sp_uri,location,time,60)

    # create playlist model and store it in the database
    playlist = tsm.Playlist(uone['id'],utwo['id'],time,location,data['playlist_url'])
    tsm.db.session.add(playlist)
    tsm.db.session.flush()
    plid = playlist.p_id
    tsm.db.session.commit()
    songs = data['songs']
    thr = Thread(target=song_run, args=[songs,plid])
    thr.start()

    fdbdata = {
        'time':time,
        'from':uone['id'],
        'to':utwo['id'],
        'plid':plid
    }
    fdb.child("notification").push(fdbdata)
    tsm.db.session.close()
    return jsonify({'status':'ok','payload':plid})

def song_run(songs,pl):
    for s in songs:
        song = tsm.Song.query.filter_by(sp_uri=s[2]).first()
        if song == None:
            song = tsm.Song(s[2],s[0],s[1],s[3])
            tsm.db.session.add(song)
            tsm.db.session.flush()
        pl_relation = tsm.PlaylistSong(pl,song.s_id)
        tsm.db.session.add(pl_relation)
    tsm.db.session.commit()

if __name__ == "__main__":
    app.run(debug = True)
