import sys
import json
import flask
import httplib2
from flask import Flask, render_template, request, redirect, jsonify, session, url_for
from oauth2client.contrib.flask_util import UserOAuth2
from oauth2client.client import OAuth2WebServerFlow
from oauth2client import client
from flask.ext.login import login_user, logout_user, current_user, login_required
import ts_auth as tsa
app = Flask(__name__)
app.debug = True
app.secret_key = 'duylamduylam'
app.config['OAUTH_CREDENTIALS'] = {
    'google':{
        'id':'423012525826-42ued2niiiecpuvrehd445n83kt16ano.apps.googleusercontent.com',
        'secret':'e2oBEpfgl3HVwU94UjFolXL8'
    }
}

# app.config['OAUTH_CREDENTIALS']['google']['GOOGLE_OAUTH2_CLIENT_ID'] = '423012525826-42ued2niiiecpuvrehd445n83kt16ano.apps.googleusercontent.com'
# app.config['OAUTH_CREDENTIALS']['google']['GOOGLE_OAUTH2_CLIENT_SECRET'] = 'e2oBEpfgl3HVwU94UjFolXL8'

@app.route('/')
def index():

    if 'credentials' not in session:
        return redirect(url_for('login'))
    credentials = client.OAuth2Credentials.from_json(session['credentials'])
    if credentials.access_token_expired:
        return redirect(url_for('login'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        return "credentials found"


@app.route('/auth')
def auth():
    # if not current_user.is_anonymous():
        # return redirect("/")
    oauth = tsa.OAuthSignIn.get_provider("google")
    s = oauth.callback()
    print s
    sys.stdout.flush()
    return redirect("/")


@app.route('/login')
def login():
    # if not current_user.is_anonymous():
        # return redirect("/")
    oauth = tsa.OAuthSignIn.get_provider("google")
    return redirect(oauth.authorize())











import sys
import os
import json
import flask
import httplib2
from flask import Flask, render_template, request, redirect, jsonify, session
from oauth2client.contrib.flask_util import UserOAuth2
from oauth2client.client import OAuth2WebServerFlow
from oauth2client import client


app = Flask(__name__)
app.debug = True
app.secret_key = 'duylamduylam'
# app.config['GOOGLE_OAUTH2_CLIENT_SECRETS_JSON'] = 'client_secrets.json'
app.config['GOOGLE_OAUTH2_CLIENT_ID'] = '423012525826-42ued2niiiecpuvrehd445n83kt16ano.apps.googleusercontent.com'
app.config['GOOGLE_OAUTH2_CLIENT_SECRET'] = 'e2oBEpfgl3HVwU94UjFolXL8'
oauth2 = UserOAuth2(app)
flow = OAuth2WebServerFlow(client_id=app.config['GOOGLE_OAUTH2_CLIENT_ID'],
                           client_secret=app.config['GOOGLE_OAUTH2_CLIENT_SECRET'],
                           scope='https://www.googleapis.com/auth/youtube',
                           redirect_uri='http://localhost:5000/auth')


@app.route('/')
def index():
    if 'credentials' not in session:
        return redirect(flask.url_for('login'))
    credentials = client.OAuth2Credentials.from_json(session['credentials'])
    if credentials.access_token_expired:
        return redirect(flask.url_for('login'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        return "credentials found"

@app.route('/auth')
def auth():
    code = request.args.get('code')
    credentials = flow.step2_exchange(code)
    session['credentials'] = credentials.to_json()
    return "yellow"

@app.route('/login')
def login():
    auth_uri = flow.step1_get_authorize_url()
    return redirect(auth_uri)
