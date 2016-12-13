import json
import jsonify
import httplib2
import gevent
import moment
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
    print('YOYOYOYOYO ****************************')

    user = {
        'id': session['credentials']['id_token']['ts_uid'],
        'name': session['credentials']['id_token']['name'],
        'avatar': session['credentials']['id_token']['avatar'],
        'email': session['credentials']['id_token']['email'],
        'access_token': session['credentials']['id_token']['access_token'],
        'refresh_token':session['credentials']['id_token']['refresh_token'],
        'expires_at':session['credentials']['id_token']['expires_at'],
        'songs': session['credentials']['id_token']['songs']
    }

    # if (user['expires_at'] - datetime.datetime.utcnow()) < datetime.timedelta(minutes=15):

    # if (credentials.token_expiry - datetime.datetime.utcnow()) < datetime.timedelta(minutes=15):
    #     credentials.refresh(httplib2.Http())

    return render_template('sphome.html',user=user)


@app.route('/sp/logout')
def view_logout():
    session.pop('credentials', None)
    return redirect('/')

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
            'expires_at':'',
            'refresh_token':'',
            'email':'',
            'ts_uid':'',
            'name':'',
            'avatar':'',
            'new':False,
            'songs':[]
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

    session['credentials']['id_token']['email'] = user_email
    session['credentials']['id_token']['expires_at'] = user_refresh_expiration
    session['credentials']['id_token']['access_token'] = user_access_token
    session['credentials']['id_token']['refresh_token'] = user_refresh_token
    session['credentials']['id_token']['name'] = user_name
    session['credentials']['id_token']['avatar'] = '/images/female/0.png'
    sp = tsr.sp_user_client(session['credentials']['id_token']['access_token'])
    top_tracks_ids = tsr.sp_get_user_top_tracks(sp)
    session['credentials']['id_token']['songs'] = top_tracks_ids
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
@app.route('/generate/one', methods=['GET'])
def generate_one():
    user = {
        'id': session['credentials']['id_token']['ts_uid'],
        'name': session['credentials']['id_token']['name'],
        'avatar': session['credentials']['id_token']['avatar'],
        'email': session['credentials']['id_token']['email'],
        'accesss_token': session['credentials']['id_token']['access_token'],
        'refresh_token':session['credentials']['id_token']['refresh_token'],
        'expires_at':session['credentials']['id_token']['expires_at'],
        'songs': session['credentials']['id_token']['songs']
    }
    return render_template('sp_generate_one.html',user=user)

@app.route('/generate/two/<int:user_id>/<user_song>/<int:other_id>/<other_song>')
def generate_two(user_id,user_song,other_id,other_song):
    print("user {0} // user song {1} // other id {2} // other song {3}".format(user_id,user_song,other_id,other_song))
    return render_template('sp_generate_two.html',user_id=user_id,user_song=user_song,other_id=other_id,other_song=other_song)

@app.route('/generate/three/<int:user_id>/<status>/<user_song>/<other_song>/<int:other_id>')
def generate_three(user_id,status,user_song,other_song,other_id):
    user = session['credentials']['id_token']
    other = tsm.get_user(uid=other_id)
    return render_template('sp_generate_three.html',user_song=user_song,other_song=other_song,user_id=user_id,user_name=user['name'],user_email=user['email'],user_avatar=user['avatar'],status=status,other_email=other['email'],other_id=other['id'],other_name=other['name'])



# $$$$$$$$$$$$$$$$$$$$$$$$ # # $$$$$$$$$$$$$$$$$$$$$$$$ # # $$$$$$$$$$$$$$$$$$ #
#       RESTFUL API        # #       RESTFUL API        # #    RESTFUL API     #
# $$$$$$$$$$$$$$$$$$$$$$$$ # # $$$$$$$$$$$$$$$$$$$$$$$$ # # $$$$$$$$$$$$$$$$$$ #

# this end point logs a message from a user. then it checks if someone has sent
# a message to the user
@app.route('/ts/api/generate/bump', methods=['POST'])
def generate_bump():
    fr = request.json['fr']
    to = request.json['to']
    time.sleep(2)
    created_at = moment.utcnow().datetime
    delta = datetime.timedelta(minutes=1)
    limit = created_at - delta
    match = tsm.db.session.query(tsm.db.exists().where(
        tsm.db.and_(
            tsm.Bump.created_at >= limit,
            tsm.Bump.fr == to,
            tsm.Bump.too == fr
        )
    )).scalar()

    try:
        if match == True:
            message.fb_notification(fr,'matched',created_at.isoformat(),{'step': 1,'winner': True})
            message.fb_notification(to,'matched',created_at.isoformat(),{'step': 1,'winner': False})
        bump = tsm.Bump(fr=fr,too=to,created_at=created_at.isoformat())
        tsm.db.session.add(bump)
        tsm.db.session.commit()
        tsm.db.session.close()
        return jsonify({'status':'ok'})

    except:
        print('MAJOR ERROR AT BUMP: {0}'.format(sys.exc_info()[0]))
        raygun.send_exception(exc_info=sys.exc_info())
        return jsonify({'status':'fail','error':'error'})

# this endpoint receives a request by the user and creates the recommendations
@app.route('/ts/api/generate/recommendation', methods=['POST'])
def create_recommendation():
    note = 'Route: Recommendation'
    t = moment.utcnow().datetime.isoformat()
    location = 'JAMAICA'
    uone = request.json['uone']
    utwo = request.json['utwo']
    print("YOOOO RECCS")
    print(uone)
    songs = [uone['song'],utwo['song']]

    oauth = tsa.OAuthSignIn.get_provider("spotify")
    new_token = oauth.refresh(refresh_token=session['credentials']['id_token']['refresh_token'])

    session['credentials']['id_token']['expires_at'] = new_token['expires_at']
    session['credentials']['id_token']['access_token'] = new_token['access_token']

    sp = tsr.sp_user_client(session['credentials']['id_token']['access_token'])
    playlist_songs = tsr.sp_get_user_recommendations(sp,songs)
    playlist = tsr.sp_create_user_playlist(sp,session['credentials']['id_token']['email'],playlist_songs,uone['name'],utwo['name'])

    # message.fb_notification(recipient=uone['id'],message=note,created_at=1,custom={'step':1})
    # message.fb_notification(recipient=utwo['id'],message=note,created_at=1,custom={'step':1})
    # try:
    #     histories = tsm.zzzistory(uone['id'],utwo['id'])
    #     spotify = tsr.spotify_client()
    #     tunesmash = tsr.recommendations(histories[uone['id']]['sp_uri'],histories[utwo['id']]['sp_uri'],50,spotify)
    #     tunesmash = tsr._audio_features(tunesmash,spotify)
    #     tunesmash = tsr._sort_bell(tunesmash)
    #     tunesmash = tsr._remove_metric_tempo(tunesmash)
    # except:
    #     print('MAJOR ERROR: {0}'.format(sys.exc_info()[0]))
    #     raygun.send_exception(exc_info=sys.exc_info())
    #     return jsonify({'status':'fail','execution_times':{1:s1}})
    #
    message.fb_notification(recipient=uone['id'],message=note,created_at=2,custom={'step':2,'playlist_url':playlist['external_urls']['spotify']})
    message.fb_notification(recipient=utwo['id'],message=note,created_at=2,custom={'step':2,'playlist_url':playlist['external_urls']['spotify']})
    # tsm.db.session.close()
    return jsonify({'status':'ok','data':playlist['external_urls']['spotify']})


if __name__ == "__main__":
    app.run(debug = True)
