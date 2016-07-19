import sys
import json
import httplib2
import ts_auth as tsa
import ts_recommendations as tsr
import ts_models as tsm
import bump
import gevent
import time
import pprint

from multiprocessing import Process
from oauth2client import client
from flask_sse import sse
from flask import Flask, render_template, request, redirect, jsonify, session, url_for,flash
from oauth2client.client import OAuth2Credentials
from oauth2client.contrib import multistore_file as oams
from flask.ext.login import login_user, logout_user, current_user, login_required,LoginManager
from flask.ext.login import LoginManager

import pyrebase
from geopy.distance import vincenty

#
import spotipy
import spotipy.oauth2 as oauth
import csv
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

SP_TOKEN = oauth.SpotifyClientCredentials(client_id='4f8c3338b0b443a8895358db33763c6f',client_secret='76cf6ff10bb041dbb0b11a3e7dd89fe1')
SP = spotipy.Spotify(auth=SP_TOKEN.get_access_token())
GLOBAL_REC_ID = []
#


pb_config = {"apiKey":"AIzaSyBKX1xmfY8JuhIbgOxhO2APg6f4VcCZWXI","authDomain":"luminous-inferno-9831.firebaseapp.com","databaseURL":"https://luminous-inferno-9831.firebaseio.com","storageBucket":"luminous-inferno-9831.appspot.com"}
fb = pyrebase.initialize_app(pb_config)
fbdb = fb.database()
#
# CONSTANTS
#
app = Flask(__name__)
app.debug = True
app.secret_key = 'duylamduylam'
app.config['OAUTH_CREDENTIALS'] = {
    'google':{
        'id':'423012525826-42ued2niiiecpuvrehd445n83kt16ano.apps.googleusercontent.com',
        'secret':'e2oBEpfgl3HVwU94UjFolXL8'
    }
}
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
@app.route('/')
def index():
    # https://developers.google.com/api-client-library/python/auth/web-app#example
    if 'credentials' in session:
        user = tsm.get_user(email=session['credentials']['id_token']['email'])
        return render_template('home.html',user_name=user.name,user_email=user.email,user_id=user.id)
    if 'credentials' not in session:
        return render_template('index.html')

@app.route('/auth')
def auth():
    oauth = tsa.OAuthSignIn.get_provider("google")
    cb_credentials = oauth.callback()
    user_info = json.loads(cb_credentials.to_json())
    session['credentials'] = user_info
    user = tsm.get_user(email=user_info['id_token']['email'])
    store = oams.get_credential_storage(filename='multi.json',client_id=user_info['id_token']['email'],user_agent='app',scope=['https://www.googleapis.com/auth/youtube','https://www.googleapis.com/auth/userinfo.profile'])
    store.put(cb_credentials)
    login_user(user, remember=True)
    if user:
        return redirect('/')
    else:
        new_user = tsm.User(user_info['id_token']['name'],user_info['id_token']['email'])
        tsm.db.session.add(new_user)
        tsm.db.session.commit()
        return redirect("/")

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
    # this is where you view songs of a playlist
    songs = tsm.get_playlist_songs(pl_id=pl_id)
    return render_template('playlist_songs.html', songs=songs)


@app.route('/loading/search', methods=['GET','POST'])
def load_search():
    if request.method == "POST":
        answer = algo_search(request)
        print("YOOOOO")
        if answer:
            return jsonify({'status':'ok'})
        else:
            return jsonify(error=404, text=str("nonono")), 404
    if request.method == "GET":
        user = tsm.get_user(email=session['credentials']['id_token']['email'])
        return render_template('search.html',user_id=user.id)

@app.route('/loading/matched', methods=['GET','POST'])
def match():
    channel = str(session['credentials']['id_token']['email'])
    data = {}
    if request.method == "POST":
        return jsonify({'status':'ok'})
    if request.method == "GET":
        return render_template('matched.html',channel=channel,data=json.dumps(session['matches']))


@app.route('/loading/generation', methods=['GET','POST'])
def generation():
    print("page: generation")
    data = json.loads(session.get('matches',None))
    if request.method == "POST":
        user_one_history = csv_to_array(data['uone_email'])
        user_two_history = csv_to_array(data['utwo_email'])
        tunesmash = generate_recommendations(user_one_history,user_two_history,60)
        youtube = get_authenticated_service(data['uone_email'])
        tunesmash = add_audio_features(tunesmash)
        tunesmash = bell_sort(tunesmash)
        tunesmash = remove_ids(tunesmash)

        playlist_id = generate_yt_playlist(youtube,tunesmash,data)
        populate_playlist(youtube,tunesmash,playlist_id)
        return jsonify({'status':'ok'})
    # this is where the recommendation algorithm is implemented
    else:
        return render_template('generation.html')

@app.route('/algorithm/generation', methods=['POST'])
def algo_generation():
    print(request.form)
    return jsonify({'status':'ok','playlist_id':2})

# @app.route('/algorithm/search', methods=['POST'])
def algo_search(request):
    print("start: search algo for: " + session['credentials']['id_token']['email'])
    sys.stdout.flush()
    data = {}
    t_init = int(request.form['time'])
    origin = (float(request.form['lat']),float(request.form['lon']))
    t_minus = t_init-10000
    t_plus = t_init+10000
    t_results = fbdb.child('bumps').order_by_child('time').start_at(t_minus).end_at(t_plus).get()
    for r in t_results.each():
        location = (r.val()['lat'],r.val()['lon'])
        distance = vincenty(origin,location).ft
        if distance < 500:
            half_life = (t_init + r.val()['time'])/2
            # data = {'half':half_life,'uone': request.form,'uone_email':request.form['email'],'utwo':r.val(),'utwo_email':r.val()['email']}
            data = {'half':half_life,'uone_email':request.form['email'],'utwo_email':r.val()['email']}
            if request.form['email'] != r.val()['email']:
                fbdb.child('matches').push(data)
                session['matches'] = json.dumps(data)
        else:
            return True
    session['matches'] = "dick"
    print("end: search algo for "+ session['credentials']['id_token']['email'])
    sys.stdout.flush()
    return True

if __name__ == "__main__":
    app.run()
