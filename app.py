# fix access token expiration

import sys
import json
import httplib2
import ts_auth as tsa
import ts_recommendations as tsr
import ts_models as tsm
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
    print session['credentials']
    sys.stdout.flush()
    if 'credentials' not in session:
        return redirect(url_for('login'))
    else:
        credentials = client.OAuth2Credentials.from_json(session['credentials'])
        http_auth = credentials.authorize(httplib2.Http())
        return render_template('index.html', cred=credentials)

    # if credentials.access_token_expired:
    #     print "merde"
    #     sys.stdout.flush()
    #     return redirect(url_for('login'))


@app.route('/auth')
def auth():
    oauth = tsa.OAuthSignIn.get_provider("google")
    user_info = oauth.callback()
    user_info = json.loads(user_info)
    user = tsm.get_user(email=user_info['id_token']['email'])

    if user:
        print user
        sys.stdout.flush()
        return redirect("/")
    else:
        credentials = client.OAuth2Credentials.from_json(session['credentials'])
        http_auth = credentials.authorize(httplib2.Http())
        # recommender = tsr.Recommender(http_auth)
        # history = recommender.get_watch_history()
        new_user = tsm.User(user_info['id_token']['name'],user_info['id_token']['email'])
        tsm.db.session.add(new_user)
        tsm.db.session.commit()
        return redirect("/")

@app.route('/loading')
def loading():
    credentials = client.OAuth2Credentials.from_json(session['credentials'])
    http_auth = credentials.authorize(httplib2.Http())
    recommender = tsr.Recommender(http_auth)
    history = recommender.get_watch_history()
    print history
    sys.stdout.flush()
    return redirect("/")

@app.route('/login')
def login():
    oauth = tsa.OAuthSignIn.get_provider("google")
    return redirect(oauth.authorize())
