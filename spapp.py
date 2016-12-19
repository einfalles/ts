import json
import jsonify
import httplib2
import gevent
import sys
import time
import pprint
import datetime
import builtins
import spotipy

import ts_auth as tsa
import ts_recommendations as tsr
import ts_models as tsm
import ts_messaging as message
from raygun4py import raygunprovider
from flask import Flask, render_template, request, redirect, jsonify, session, url_for,send_file


app = Flask(__name__, static_url_path='')
app.debug = True
app.config['REFRESH_LIMIT'] = 15

app.secret_key = 'duylamduylam'
app.config['OAUTH_CREDENTIALS'] = {
    'google':{
        'id':'423012525826-42ued2niiiecpuvrehd445n83kt16ano.apps.googleusercontent.com',
        'secret':'e2oBEpfgl3HVwU94UjFolXL8'
    },
    'spotify': {
        'id':'4f8c3338b0b443a8895358db33763c6f',
        'secret':'76cf6ff10bb041dbb0b11a3e7dd89fe1'
    }
}
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 604800
raygun = raygunprovider.RaygunSender("aR9aPioLxr1y42IN3HqSnw==")


#
# ROUTING
#

@app.route('/')
def index():
    if 'credentials' not in session:
        return render_template('index.html')

    user = {
        'id': session['credentials']['id_token']['ts_uid'],
        'name': session['credentials']['id_token']['name'],
        'avatar': session['credentials']['id_token']['avatar'],
        'email': session['credentials']['id_token']['email']
    }

    return render_template('sphome.html',user=user,user_id=user['id'])



# ******************************************************************* #
#                              sign in                                #
# ******************************************************************* #
@app.route('/sp/login')
def spotify_login():
    oauth = tsa.OAuthSignIn.get_provider("spotify")
    url = oauth.authorize()
    return redirect(url)

@app.route('/sp/auth')
def spotify_auth():
    session['credentials'] = {
        'id_token': {
            'access_token':'',
            'refresh_token':'',
            'email':'',
            'ts_uid':'',
            'name':'',
            'avatar':'',
            'new':False
            }
    }
    oauth = tsa.OAuthSignIn.get_provider("spotify")
    oauth.callback()
    user_email = oauth.results['spotify_user_id']
    user_refresh_token = oauth.results['refresh_token']
    user_refresh_expiration = oauth.results['expires_at']
    user_access_token = oauth.results['access_token']
    user_name = oauth.results['name']
    user_spid_but_actually_its_their_email = oauth.results['email']

    user = tsm.get_user(email=user_email)

    if user == None:
        user = tsm.User(user_name,user_email,'/images/female/0.png')
        tsm.db.session.add(user)
        tsm.db.session.flush()
        session['credentials']['id_token']['ts_uid'] = user.id
        tsm.db.session.commit()
    else:
        session['credentials']['id_token']['ts_uid'] = user['id']

    session['credentials']['id_token']['email'] = user['email']
    session['credentials']['id_token']['access_token'] = user_access_token
    session['credentials']['id_token']['refresh_token'] = user_refresh_token
    session['credentials']['id_token']['name'] = user['name']
    session['credentials']['id_token']['avatar'] = user['avatar']

    tsm.db.session.close()

    return redirect('/')


# ******************************************************************* #
#                          manage playlists                           #
# ******************************************************************* #
#
# USE COOKIES
#
@app.route('/users/<int:user_id>/playlists', methods=['GET'])
def view_playlists(user_id):
    return render_template('playlists_all.html',user_id=user_id)

@app.route('/users/<int:user_id>/playlists/<int:playlist_id>/<url>/<name>', methods=['GET'])
def view_playlist_songs(user_id,playlist_id,url,name):
    return render_template('playlist_details.html',pid=playlist_id,user_id=user_id,name=name,url=url)

# ******************************************************************* #
#                          manage account                             #
# ******************************************************************* #
@app.route('/users/<int:user_id>/profile', methods=['GET'])
def view_profile(user_id):
    return render_template('profile.html',user_avatar=session['credentials']['id_token']['avatar'],user_name=session['credentials']['id_token']['name'],user_id=user_id)

@app.route('/users/<int:user_id>/profile/account', methods=['GET'])
def view_profile_name(user_id):
    return render_template('profile_name.html',user_id=user_id)

@app.route('/users/<int:user_id>/profile/avatar', methods=['GET'])
def view_profile_avatar(user_id):
    return render_template('profile_avatars.html',user_id=user_id)

@app.route('/users/<int:user_id>/profile/avatar/<gender>', methods=['GET'])
def view_profile_avatar_gender(user_id,gender):
    f  = list(range(0,20))
    return render_template('profile_avatar_gender.html',user_id=user_id,gender=gender,f=f)

# ******************************************************************* #
#                          make a playlist                            #
# ******************************************************************* #
@app.route('/generate/one/<int:user_id>', methods=['GET'])
def generate_one(user_id):
    return render_template('sp_generate_one.html',user_avatar=session['credentials']['id_token']['avatar'],user_email=session['credentials']['id_token']['email'],user_name=session['credentials']['id_token']['name'],user_id=user_id)

@app.route('/generate/two/<int:user_id>/<int:first>/<int:second>')
def generate_two(user_id,first,second):
    return render_template('sp_generate_two.html',first=first,second=second,user_id=user_id)

@app.route('/generate/three/<int:user_id>/<status>/<int:other_id>')
def generate_three(user_id,status,other_id):
    user = session['credentials']['id_token']
    other = tsm.get_user(uid=other_id)
    return render_template('sp_generate_three_1.html',user_id=user_id,user_name=user['name'],user_email=user['email'],user_avatar=user['avatar'],status=status,other_email=other['email'],other_id=other['id'],other_name=other['name'])



# $$$$$$$$$$$$$$$$$$$$$$$$ # # $$$$$$$$$$$$$$$$$$$$$$$$ # # $$$$$$$$$$$$$$$$$$ #
#       RESTFUL API        # #       RESTFUL API        # #    RESTFUL API     #
# $$$$$$$$$$$$$$$$$$$$$$$$ # # $$$$$$$$$$$$$$$$$$$$$$$$ # # $$$$$$$$$$$$$$$$$$ # 


if __name__ == "__main__":
    app.run(debug = True)
