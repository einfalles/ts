# give every user a fake avatar
# let users choose avatar
# 8 bitify album art / youtube preview image
# write js to remove and add html to loading/search
# write rules to clean up youtube data
# separate ui from tasks even further...

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

from threading import Thread
from oauth2client import client
from flask_sse import sse
from flask import Flask, render_template, request, redirect, jsonify, session, url_for,send_file
from oauth2client.client import OAuth2Credentials
from oauth2client.contrib import multistore_file as oams
from flask_login import login_user, logout_user, current_user, login_required,LoginManager
from flask_login import LoginManager
from werkzeug.contrib.profiler import ProfilerMiddleware


#
# CONSTANTS
#

app = Flask(__name__, static_url_path='')
app.debug = True
app.config['REFRESH_LIMIT'] = 15

app.secret_key = 'duylamduylam'
app.config['OAUTH_CREDENTIALS'] = {
    'google':{
        'id':'423012525826-42ued2niiiecpuvrehd445n83kt16ano.apps.googleusercontent.com',
        'secret':'e2oBEpfgl3HVwU94UjFolXL8'
    }
}
app.config['PROFILE'] = True
app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 604800
config = {
  "apiKey": "AIzaSyBKX1xmfY8JuhIbgOxhO2APg6f4VcCZWXI",
  "authDomain": "luminous-inferno-9831.firebaseapp.com",
  "databaseURL": "https://luminous-inferno-9831.firebaseio.com",
  "storageBucket": "luminous-inferno-9831.appspot.com",
};
firebase = pyrebase.initialize_app(config)
fdb = firebase.database()
# FLASK LOGIN CONFIG
lm = LoginManager()
lm.init_app(app)
lm.login_view = "login"
lm.login_message = u"Please log in to access this page."
lm.refresh_view = "reauth"

@lm.user_loader
def load_user(email):
    return tsm.User.query.filter(email==email).first()


#
# ROUTING
#
@app.route('/loaderio-c54d3912e32128c85bd19987caf3561e')
def loaderio():
    return send_file('/js/loaderio-c54d3912e32128c85bd19987caf3561e.txt', attachment_filename='loaderio-c54d3912e32128c85bd19987caf3561e.txt')

@app.route('/')
def index():
    # https://developers.google.com/api-client-library/python/auth/web-app#example
    if 'credentials' not in session:
        return render_template('index.html')

    if 'credentials' in session:
        user = tsm.get_user(email=session['credentials']['id_token']['email'])
        session['credentials']['id_token']['ts_uid'] = user.id
        store = oams.get_credential_storage(filename='multi.json',client_id=user.email,user_agent='app',scope=['https://www.googleapis.com/auth/userinfo.profile','https://www.googleapis.com/auth/youtube'])
        credentials = store.get()

        if (credentials.token_expiry - datetime.datetime.utcnow()) < datetime.timedelta(minutes=app.config['REFRESH_LIMIT']):
            credentials.refresh(httplib2.Http())
        if credentials.invalid == True:
            return redirect('/login')

        thr = Thread(target=history_run,args=[user.id,user.email])
        thr.start()
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
    return redirect("/")

# @app.route('/setup')


@app.route('/login')
def login():
    oauth = tsa.OAuthSignIn.get_provider("google")
    return redirect(oauth.authorize())

@app.route('/playlist/management/<uid>', methods=['GET','POST'])
def manage_playlist(uid):
    playlists = tsm.get_all_playlists(user_id=uid)
    return render_template('playlists.html',playlists=playlists)

@app.route('/playlist/<pl_id>')
def view_playlist(pl_id):
    songs = tsm.get_playlist_songs(pl_id=pl_id)
    url = tsm.get_playlist_url(pl_id=pl_id)
    return render_template('playlist_songs.html', songs=songs,pl=url.url)
# 
# @app.route('/profile/management/<uid>')
# def profile_management(uid):
#     user = session['credentials']['id_token']
#     return render_template('profile.html', user_avatar=user['avatar'],user_name=user['name'])
#
# @app.route('/profile/management/name')
# def profile_name():
#     user = session['credentials']['id_token']
#     return render_template('profile_name.html',user_name=user['name'])
#
# @app.route('/profile/management/avatar')
# def avatar_gender():
#     return render_template('avatars.html')
#
# @app.route('/profile/management/avatar/<gender>')
# def avatar_selection(gender):
#     if gender == 'male':
#     if gender == 'female':
#
# @app.route('/profile/update/<edit>/<uid>', methods=['POST'])
# def avatar_update(edit, uid):
#     if edit == 'name':
#         tsm.User.query.filter_by(User.id==uid).update({'name':request.json['name']})
#         return jsonify({'status':'done'})
#     if edit == 'avatar':
#         tsm.User.query.filter_by(User.id==uid).update({'avatar':request.json['avatar']})
#         return jsonify({'status':'done'})


@app.route('/loading/search', methods=['GET','POST'])
def load_search():
    if request.method == "POST":
        return jsonify({'status':'ok'})
    if request.method == "GET":
        user = session['credentials']['id_token']
        return render_template('search.html',user_id=user['ts_uid'],user_email=user['email'],user_name=user['name'])

@app.route('/loading/match/to/<uid>',methods=['GET','POST'])
def load_match(uid):
    if request.method == "POST":
        return jsonify({'status':'ok'})
    if request.method == "GET":
        user = session['credentials']['id_token']
        other = tsm.get_user(uid=uid)
        return render_template('matched.html',user_id=user['ts_uid'],user_email=user['email'],user_name=user['name'],to_id=other.id,to_email=other.email,to_name=other.name)


@app.route('/algorithm/generation', methods=['POST'])
def algo_generation():
    time = moment.utcnow().datetime.isoformat()
    location = request.json['location']
    uone = request.json['uone']
    utwo = request.json['utwo']
    hone = tsm.get_history(uone['id'])
    htwo = tsm.get_history(utwo['id'])
    data = tsr.run_generation(uone,utwo,hone.song.sp_uri,htwo.song.sp_uri,location,time,60)
    playlist = tsm.Playlist(uone['id'],utwo['id'],time,location,data['playlist_url'])
    tsm.db.session.add(playlist)
    tsm.db.session.flush()
    plid = playlist.p_id
    songs = data['songs']
    thr = Thread(target=song_run, args=[songs,plid])
    thr.start()

    fdbdata = {
        'time':time,
        'from':uone,
        'to':utwo,
        'plid':plid
    }
    fdb.child("notification").push(fdbdata)
    tsm.db.session.commit()
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
