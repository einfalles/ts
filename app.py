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

import ts_auth as tsa
import ts_recommendations as tsr
import ts_models as tsm
import ts_messaging as message

from raygun4py import raygunprovider
from flask import Flask, render_template, request, redirect, jsonify, session, url_for,send_file
from oauth2client.contrib import multistore_file as oams
# from werkzeug.contrib.profiler import ProfilerMiddleware


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
    },
    'spotify': {
        'id':'4f8c3338b0b443a8895358db33763c6f',
        'secret':'76cf6ff10bb041dbb0b11a3e7dd89fe1'
    }
}
# app.config['PROFILE'] = True
# app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 604800
raygun = raygunprovider.RaygunSender("aR9aPioLxr1y42IN3HqSnw==")


#
# ROUTING
#

@app.route('/loaderio-c54d3912e32128c85bd19987caf3561e')
def loaderio():
    return send_file('/js/loaderio-c54d3912e32128c85bd19987caf3561e.txt', attachment_filename='loaderio-c54d3912e32128c85bd19987caf3561e.txt')

@app.route('/')
def index():
    t0 = time.time()

    if 'credentials' not in session:
        t1 = time.time() - t0
        return render_template('index.html',execution_time=t1)
    user = {
        'id': session['credentials']['id_token']['ts_uid'],
        'name': session['credentials']['id_token']['name'],
        'avatar': session['credentials']['id_token']['avatar'],
        'email': session['credentials']['id_token']['email']
    }
    pprint.pprint(user)
    # user = tsm.get_user(uid=session['credentials']['id_token']['ts_uid'])
    # user = tsm.psyco_get_user(user_id=session['credentials']['id_token']['ts_uid'])
    # user = tsm.sqlalchemy_raw_get_user(user_id=session['credentials']['id_token']['ts_uid'])
    t1 = time.time() - t0

    t2 = time.time()
    credentials = tsr.youtube_credentials(user['email'])
    session.permanent = True
    if (credentials.token_expiry - datetime.datetime.utcnow()) < datetime.timedelta(minutes=app.config['REFRESH_LIMIT']):
        credentials.refresh(httplib2.Http())
    if credentials.invalid == True:
        return redirect('/login')
    t3 = time.time() - t2

    try:
        if 'etag' in session['credentials']['id_token']:
            etag = session['credentials']['id_token']['etag']
        else:
            etag = None

        t4 = time.time()
        youtube = tsr.youtube_client(credentials)
        hid = tsr.playlist_history_id(youtube)
        t5 = time.time() - t4

        t6 = time.time()
        go_no = tsr.is_history_updated(credentials=credentials,youtube=youtube,user_email=user['email'],etag=etag,hid=hid)
        session['credentials']['id_token']['etag'] = go_no['etag']
        t7 = time.time() - t6

        tsm.db.session.close()
        return render_template('home.html',refresh=go_no['refresh'],hid=hid,user_name=user['name'],user_email=user['email'],user_id=user['id'], execution_time={1:t1,2:t3,3:t5,4:t7})
    except:
        print('MAJOR ERROR')
        raygun.send_exception(exc_info=sys.exc_info())
        return jsonify({'status':'fail'})

# *************************
# sign in
# *************************
@app.route('/auth')
def auth():
    try:
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
            user = tsm.User(user_name,user_email,'/images/female/0.png')
            tsm.db.session.add(user)
            tsm.db.session.flush()
            session['credentials']['id_token']['ts_uid'] = user.id
            session['credentials']['id_token']['name'] = user.name
            session['credentials']['id_token']['avatar'] = user.avatar
            tsm.db.session.commit()
        else:
            session['credentials']['id_token']['name'] = user['name']
            session['credentials']['id_token']['avatar'] = user['avatar']
            session['credentials']['id_token']['ts_uid'] = user['id']
        session.permanent = True
        tsm.db.session.close()
    except:
        print('MAJOR ERROR AT BUMP: {0}'.format(sys.exc_info()[0]))
        raygun.send_exception(exc_info=sys.exc_info())
        return "Something broke. Sorry :( Try again soon."
    return redirect("/")

@app.route('/login')
def login():
    oauth = tsa.OAuthSignIn.get_provider("google")
    return redirect(oauth.authorize())

@app.route('/sp/auth')
def spotify_auth():
    oauth = tsa.OAuthSignIn.get_provider("spotify")
    oauth.callback()
    pprint.pprint(oauth.results)
    user_email = oauth.results['spotify_user_id']
    user_refresh_token = oauth.results['refresh_token']
    user_refresh_expiration = oauth.results['expires_at']
    user_access_token = oauth.results['access_token']
    user_name = oauth.results['name']
    user_spid_but_actually_its_their_email = oauth.results['email']
    user = tsm.get_user(email=user_email)
    session['credentials'] = {'id_token':{'email':'','ts_uid':'','name':'','avatar':'','new':False}}
    if user == None:
        session['credentials']['id_token']['new'] = True
        user = tsm.User(user_name,user_email,'/images/female/0.png')
        tsm.db.session.add(user)
        tsm.db.session.flush()
        session['credentials']['id_token']['ts_uid'] = user.id
        session['credentials']['id_token']['name'] = user.name
        session['credentials']['id_token']['avatar'] = user.avatar
        session['credentials']['id_token']['email'] = user.email
        tsm.db.session.commit()
    else:
        session['credentials']['id_token']['name'] = user['name']
        session['credentials']['id_token']['avatar'] = user['avatar']
        session['credentials']['id_token']['ts_uid'] = user['id']
        session['credentials']['id_token']['email'] = user['email']
    session.permanent = True
    tsm.db.session.close()

    return redirect("/")

@app.route('/sp/login')
def spotify_login():
    oauth = tsa.OAuthSignIn.get_provider("spotify")
    return redirect(oauth.authorize())
# *************************
# manage playlists
# *************************
@app.route('/users/<int:user_id>/playlists', methods=['GET'])
def view_playlists(user_id):
    return render_template('playlists_one.html',user_id=user_id)

@app.route('/users/<int:user_id>/playlists/<int:playlist_id>/<url>/<name>', methods=['GET'])
def view_playlist_songs(user_id,playlist_id,url,name):
    return render_template('playlists_two.html',pid=playlist_id,user_id=user_id,name=name,url=url)

# *************************
# manage account
# *************************
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

# *************************
# make a playlist
# *************************
@app.route('/generate/one/old', methods=['GET'])
def generate_select():
    return render_template('generate_one.html')

@app.route('/generate/two/<int:user_id>',methods=['GET'])
def generate_match(user_id):
    match = tsm.get_user(uid=user_id)
    return render_template('generate_two.html',match=match)

@app.route('/generate/one/<int:user_id>', methods=['GET'])
def generate_one(user_id):
    return render_template('generate_one_1.html',user_avatar=session['credentials']['id_token']['avatar'],user_email=session['credentials']['id_token']['email'],user_name=session['credentials']['id_token']['name'],user_id=user_id)

@app.route('/generate/two/<int:user_id>/<int:first>/<int:second>')
def generate_two(user_id,first,second):
    return render_template('generate_two_1.html',first=first,second=second,user_id=user_id)

@app.route('/generate/three/<int:user_id>/<status>/<int:other_id>')
def generate_three(user_id,status,other_id):
    user = session['credentials']['id_token']
    other = tsm.get_user(uid=other_id)
    return render_template('generate_three_1.html',user_id=user_id,user_name=user['name'],user_email=user['email'],user_avatar=user['avatar'],status=status,other_email=other['email'],other_id=other['id'],other_name=other['name'])


@app.route('/fcm', methods=['GET'])
def fcm():
    user = session['credentials']['id_token']
    credentials = tsr.youtube_credentials(user['email'])
    youtube = tsr.youtube_client(credentials)
    hid = tsr.playlist_history_id(youtube)
    return render_template('fcm.html',hid=hid,user_email=user['email'],user_id=user['ts_uid'])



# $$$$$$$$$$$$$$$$$$$$$$$$ #
#       RESTFUL API        #
# $$$$$$$$$$$$$$$$$$$$$$$$ #

@app.route('/ts/api/users/<int:user_id>/update', methods=['POST'])
def avatar_update(user_id):
    pprint.pprint(request.json['data'])
    # time: start
    t0 = time.time()
    field = request.json['update']
    data = request.json['data']
    tsm.User.query.filter(tsm.User.id==user_id).update({field:data})
    tsm.db.session.commit()
    session['credentials']['id_token'][field] = data
    tsm.db.session.close()

    # time: end
    t1 = time.time() - t0
    pprint.pprint('sending something back now!')
    return jsonify({'status':'ok','execution_time':t1})

# about 5 seconds
@app.route('/ts/api/generate/bump', methods=['POST'])
def generate_bump():
    fr = request.json['fr']
    to = request.json['to']
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
        return jsonify({'status':'ok','data':{'first':request.json['first'],'second':request.json['second'],'me':request.json['fr']}})
    except:
        print('MAJOR ERROR AT BUMP: {0}'.format(sys.exc_info()[0]))
        raygun.send_exception(exc_info=sys.exc_info())
        return jsonify({'status':'fail','error':'error'})

# about 5 seconds
@app.route('/ts/api/users/update/history', methods=['POST'])
def update_history():
    t0 = time.time()
    user = {
        'email': request.json['email'],
        'id': request.json['id'],
        'hid': request.json['hid']
    }
    credentials = tsr.youtube_credentials(user['email'])
    youtube = tsr.youtube_client(credentials)
    spotify = tsr.spotify_client()
    try:
        song = tsr.latest_song(user['email'],user['hid'],youtube,spotify)
        if song is not None:
            yt_match = tsm.db.session.query(tsm.db.exists().where(
                tsm.db.and_(
                    tsm.Zong.yt_uri == song['yt_uri'],
                )
            )).scalar()
            sp_match = tsm.db.session.query(tsm.db.exists().where(
                    tsm.Zong.sp_uri == song['sp_uri']
            )).scalar()

            if sp_match == True and yt_match == True:
                commit_history = tsm.Zistory(uid=user['id'],zurl=song['yt_uri'],created_at=moment.utcnow().datetime.isoformat())
                tsm.db.session.add(commit_history)

            if sp_match == False and yt_match == False:
                commit_song = tsm.Zong(sp_uri=song['sp_uri'],yt_uri=song['yt_uri'],track=song['track'],artist=song['artist'])
                tsm.db.session.add(commit_song)
                commit_history = tsm.Zistory(uid=user['id'],zurl=song['yt_uri'],created_at=moment.utcnow().datetime.isoformat())
                tsm.db.session.add(commit_history)

            if sp_match == True and yt_match == False:
                a = tsm.Zong.query.filter(tsm.Zong.sp_uri == song['sp_uri']).first()
                commit_history = tsm.Zistory(uid=user['id'],zurl=a.yt_uri,created_at=moment.utcnow().datetime.isoformat())
                tsm.db.session.add(commit_history)

            if sp_match == False and yt_match == True:
                commit_history = tsm.Zistory(uid=user['id'],zurl=song['yt_uri'],created_at=moment.utcnow().datetime.isoformat())
                tsm.db.session.add(commit_history)

            tsm.db.session.commit()
            t1 = time.time() - t0
            tsm.db.session.close()
            return jsonify({'status':'ok','data':{'message':'available','latest_song_sp_id':song['sp_uri']},'execution_time':t1})
        else:
            print('No music found for {0}'.format(user['email']))
            t1 = time.time() - t0
            tsm.db.session.close()
            return jsonify({'status':'ok','data':{'message':'unavailable'},'execution_time':t1})
    except:
        print('MAJOR ERROR AT HISTORY: {0}'.format(sys.exc_info()))
        raygun.send_exception(exc_info=sys.exc_info())
        t1 = time.time() - t0
        tsm.db.session.close()
        return jsonify({'status':'fail','error':'error','execution_time':t1})


# Get user's information
@app.route('/ts/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    a = time.clock()
    user = tsm.get_user(uid=user_id)
    b = time.clock()
    delta = b-a
    tsm.db.session.close()
    return jsonify({'status':'ok','data':user,'execution_time':delta})

# Get a user's playlists
@app.route('/ts/api/users/<int:user_id>/playlists', methods=['GET'])
def manage_playlist(user_id):
    a = time.clock()
    playlists = tsm.get_all_playlists(uid=user_id)
    b = time.clock()
    delta = b-a
    tsm.db.session.close()
    return jsonify({'status':'ok','data':playlists,'execution_time':delta})

# Get a playlist's songs
@app.route('/ts/api/playlist/<p_id>', methods=['GET'])
def view_playlist(p_id):
    a = time.clock()
    # songs = tsm.get_playlist_songs(pl_id=p_id)
    songs = tsm.get_pongz(purl=p_id)
    b = time.clock()
    delta = b-a
    tsm.db.session.close()
    return jsonify({'status':'ok','data':songs,'execution_time':delta})

# 15 seconds
# Create a new playlist
@app.route('/ts/api/generate/recommendation', methods=['POST'])
def create_recommendation():
    pprint.pprint('{0} has made a request to generate a playlist'.format(request.json['fr']))
    note = 'Route: Recommendation'
    t = moment.utcnow().datetime.isoformat()
    location = request.json['location']
    location = 'JAMAICA'
    uone = request.json['uone']
    utwo = request.json['utwo']

    t0 = time.time()
    histories = tsm.zzzistory(uone['id'],utwo['id'])
    s1 = time.time() - t0
    step = 1
    message.fb_notification(recipient=uone['id'],message=note,created_at=s1,custom={'step':step})
    message.fb_notification(recipient=utwo['id'],message=note,created_at=s1,custom={'step':step})

    t1 = time.time()
    try:
        spotify = tsr.spotify_client()
        tunesmash = tsr.recommendations(histories[uone['id']]['sp_uri'],histories[utwo['id']]['sp_uri'],50,spotify)
        tunesmash = tsr._audio_features(tunesmash,spotify)
        tunesmash = tsr._sort_bell(tunesmash)
        tunesmash = tsr._remove_metric_tempo(tunesmash)
    except:
        print('MAJOR ERROR: {0}'.format(sys.exc_info()[0]))
        raygun.send_exception(exc_info=sys.exc_info())
        return jsonify({'status':'fail','execution_times':{1:s1}})
    s2 = time.time() - t1
    step = 2
    message.fb_notification(recipient=uone['id'],message=note,created_at=s2,custom={'step':step,'tunes':tunesmash})
    message.fb_notification(recipient=utwo['id'],message=note,created_at=s2,custom={'step':step,'tunes':tunesmash})


    t2 = time.time()
    try:
        created_at = moment.now().date

        credential_2 = tsr.youtube_credentials(utwo['email'])
        credentials = tsr.youtube_credentials(uone['email'])
        youtube = tsr.youtube_client(credentials)
        youtube_2 = tsr.youtube_client(credential_2)
        ytpid = tsr.insert_playlist(youtube=youtube,uone=uone['name'],utwo=utwo['name'],year=created_at.year,month=created_at.month,day=created_at.day,hour=created_at.hour)
        ytpid_2 = tsr.insert_playlist(youtube=youtube_2,uone=utwo['name'],utwo=uone['name'],year=created_at.year,month=created_at.month,day=created_at.day,hour=created_at.hour)
        print(ytpid_2)
    except:
        print('MAJOR ERROR: {0}'.format(sys.exc_info()[0]))
        raygun.send_exception(exc_info=sys.exc_info())
        return jsonify({'status':'fail','execution_times':{1:s1,2:s2}})
    s3 = time.time() - t2
    step = 3
    message.fb_notification(recipient=uone['id'],message=note,created_at=s3,custom={'step':step})
    message.fb_notification(recipient=utwo['id'],message=note,created_at=s3,custom={'step':step})

    # HOW CAN WE MAKE THIS STEP FASTER????
    t3 = time.time()
    try:
        videos = tsr.insert_playlist_videos(youtube,tunesmash,ytpid)
        [tunesmash[i].append(videos[i])  for i in range(len(videos))]
        print(videos)
        videos_2 = tsr.insert_playlist_videos_2(youtube_2,tunesmash,ytpid_2,videos)
    except tsr.HttpError as err:
        e = err
        str_error = e.content.decode('utf-8')
        dict_error = json.loads(str_error)
        pprint.pprint(dict_error)
        message.fb_notification(recipient=uone['id'],message='ERROR',created_at=s3,custom={'step':step})
        message.fb_notification(recipient=utwo['id'],message='ERROR',created_at=s3,custom={'step':step})
        if dict_error['error']['code'] == 401:
            return not_found()
        return jsonify({'status':'fail'})
    except:
        print('MAJOR ERROR AT BUMP: {0}'.format(sys.exc_info()[0]))
        raygun.send_exception(exc_info=sys.exc_info())
        return jsonify({'status':'fail','execution_times':{1:s1,2:s2,3:s3}})
    s4 = time.time() - t3
    step = 4
    message.fb_notification(recipient=uone['id'],message=note,created_at=s4,custom={'step':step})
    message.fb_notification(recipient=utwo['id'],message=note,created_at=s4,custom={'step':step})
    # return jsonify({'status':'ok','data':{'tunes': tunesmash,'playlist_id':ytpid},'execution_times':{1:s1,2:s2,3:s3,4:s4}})

    t4 = time.time()
    try:
        playlist = tsm.Playlist(uone['id'],utwo['id'],t,location,ytpid)
        tsm.db.session.add(playlist)
        tsm.db.session.commit()
    except:
        print('MAJOR ERROR AT BUMP: {0}'.format(sys.exc_info()[0]))
        raygun.send_exception(exc_info=sys.exc_info())
        return jsonify({'status':'fail','execution_times':{1:s1,2:s2,3:s3,4:s4}})
    s5 = time.time() - t4
    step = 5
    message.fb_notification(recipient=uone['id'],message=note,created_at=s5,custom={'step':step,'playlist_id':ytpid,'starting_video':videos[0]})
    message.fb_notification(recipient=utwo['id'],message=note,created_at=s5,custom={'step':step,'playlist_id':ytpid_2,'starting_video':videos[0]})
    # HOW CAN WE MAKE THIS STEP FASTER????
    tsm.db.session.close()
    return jsonify({'status':'ok','data':{'tunes':tunesmash,'playlist_id':ytpid,'starting_video':videos[0]},'execution_times':{1:s1,2:s2,3:s3,4:s4,5:s5}})
# 10 seconds

@app.route('/ts/api/generate/recommendation/song_run', methods=['POST'])
def store_songs():
    t5 = time.time()
    tunesmash = request.json['tunes']
    ytpid = request.json['playlist_id']
    try:
        tsm.song_run(tunesmash,ytpid)
        s6 = time.time() - t5
        tsm.db.session.close()
        return jsonify({'status':'ok'})
    except:
        print('MAJOR ERROR AT BUMP: {0}'.format(sys.exc_info()[0]))
        raygun.send_exception(exc_info=sys.exc_info())
        return jsonify({'status':'fail','execution_times':{1:s1,2:s2,3:s3,4:s4,5:s5}})


@app.errorhandler(401)
def not_found(error=None):
    message = {
            'status': 401,
            'message': 'You have not created a Youtube Channel. Step 1: Go to Youtube Step 2: Sign in with the email you are using for TuneSmash. Step 3: Click my channel on the left hand side. Step 4: fill in all your details Step 5: click create channel. Step 6: Go back to TuneSmash and refresh the app from the home page'
    }
    resp = jsonify(message)
    resp.status_code = 401
    return resp


if __name__ == "__main__":
    app.run(debug = True)
