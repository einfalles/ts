# write module to handle pulling history
# check if user is new or old
#

import sys
import json
import httplib2
import ts_auth as tsa
import ts_recommendations as tsr
from oauth2client import client
from flask import Flask, render_template, request, redirect, jsonify, session, url_for

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

#
# ROUTING
#
@app.route('/')
def index():
    if 'credentials' not in session:
        return redirect(url_for('login'))
    credentials = client.OAuth2Credentials.from_json(session['credentials'])
    if credentials.access_token_expired:
        return redirect(url_for('login'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        recommender = tsr.Recommender(http_auth)
        history = recommender.get_watch_history()
        print history
        sys.stdout.flush()
        return "credentials found"


@app.route('/auth')
def auth():
    oauth = tsa.OAuthSignIn.get_provider("google")
    oauth.callback()
    return redirect("/")


@app.route('/login')
def login():
    oauth = tsa.OAuthSignIn.get_provider("google")
    return redirect(oauth.authorize())
