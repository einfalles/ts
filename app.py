# keep google oauth
# change where songs are getting stored zongz -> songs etc
#
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

@app.route('/')
def index():
    t0 = time.time()
    if 'credentials' not in session:
        t1 = time.time() - t0
        return render_template('index.html',execution_time=t1)

    if 'credentials' in session:
        user = tsm.get_user(uid=session['credentials']['id_token']['ts_uid'])
        t1 = time.time() - t0
        t2 = time.time()
        store = oams.get_credential_storage(filename='multi.json',client_id=user['email'],user_agent='app',scope=['https://www.googleapis.com/auth/userinfo.profile','https://www.googleapis.com/auth/youtube'])
        credentials = store.get()
        t3 = time.time() - t2
        if (credentials.token_expiry - datetime.datetime.utcnow()) < datetime.timedelta(minutes=app.config['REFRESH_LIMIT']):
            credentials.refresh(httplib2.Http())
        if credentials.invalid == True:
            return redirect('/login')

        if 'etag' in session['credentials']['id_token']:
            etag = session['credentials']['id_token']['etag']
        else:
            etag = None
        try:
            t4 = time.time()
            youtube = tsr.get_authenticated_service(user['email'])
            hid = tsr.get_history_id(youtube)
            t5 = time.time() - t4
            t6 = time.time()
            go_no = tsr.is_history_new(youtube,user['email'],etag=etag,hid=hid)
            session['credentials']['id_token']['etag'] = go_no['etag']
        except:
            print('MAJOR ERROR')
            raygun.send_exception(exc_info=sys.exc_info())
        session['credentials']['id_token']['ts_uid'] = user['id']
        session['credentials']['id_token']['avatar'] = user['avatar']
        session.permanent = True
        t7 = time.time() - t6
        return render_template('home.html',refresh=go_no['refresh'],hid=hid,user_name=user['name'],user_email=user['email'],user_id=user['id'], execution_time={1:t1,2:t3,3:t5,4:t7})

# *************************
# sign in
# *************************
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

# *************************
# manage playlists
# *************************
@app.route('/users/<int:user_id>/playlists', methods=['GET'])
def view_playlists(user_id):
    t0 = time.time()
    return render_template('playlists_one.html',execution_time=time.time()-t0,user_id=user_id)

@app.route('/users/<int:user_id>/playlists/<int:playlist_id>/<url>/<name>', methods=['GET'])
def view_playlist_songs(user_id,playlist_id,url,name):
    t0 = time.time()
    return render_template('playlists_two.html',execution_time=time.time()-t0,pid=playlist_id,name=name,url=url)

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

@app.route('/ts/api/users/<int:user_id>/update', methods=['POST'])
def avatar_update(user_id):
    print(request.form)
    field = request.json['update']
    data = request.json['data']
    tsm.User.query.filter(tsm.User.id==user_id).update({field:data})
    tsm.db.session.commit()
    session['credentials']['id_token'][field] = data
    tsm.db.session.close()
    return jsonify({'status':'ok'})

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
    return render_template('generate_three_1.html',user_id=user_id,user_email=user['email'],user_avatar=user['avatar'],status=status,other_email=other['email'],other_id=other['id'],other_name=other['name'])


@app.route('/fcm', methods=['GET'])
def fcm():
    return render_template('fcm.html')


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
    if match == True:
        fdbdata = {
            'recipient':fr,
            'message': 'match found',
            'winner': True,
            'created_at': created_at.isoformat(),
            'step': 1
        }
        fdb.child("notification").push(fdbdata)
        fdbdata = {
            'recipient': to,
            'message': 'match found',
            'winner': False,
            'created_at': created_at.isoformat(),
            'step': 1
        }
        fdb.child("notification").push(fdbdata)
    try:
        bump = tsm.Bump(fr=fr,too=to,created_at=created_at.isoformat())
        tsm.db.session.add(bump)
        tsm.db.session.commit()
        return jsonify({'status':'ok','data':{'first':request.json['first'],'second':request.json['second'],'me':request.json['fr']}})
    except:
        print('MAJOR ERROR AT BUMP: {0}'.format(sys.exc_info()[0]))
        raygun.send_exception(exc_info=sys.exc_info())
        return jsonify({'status':'fail','error':'error'})



# $$$$$$$$$$$$$$$$$$$$$$$$ #
#       RESTFUL API        #
# $$$$$$$$$$$$$$$$$$$$$$$$ #

@app.route('/ts/api/users/update/history', methods=['POST'])
def update_history():
    user = {
        'email': request.json['email'],
        'id': request.json['id'],
        'hid': request.json['hid']
    }
    youtube = tsr.get_authenticated_service(user['email'])
    try:
        song = tsr.get_latest_song(user['email'],user['hid'],youtube)
        print('this is the song {0}'.format(song))
        if song is not None:
            match = tsm.db.session.query(tsm.db.exists().where(
                tsm.db.and_(
                    tsm.Zong.yt_uri == song['yt_uri'],
                )
            )).scalar()
            print('this is the match {0}'.format(match))
            if match == False:
                commit_song = tsm.Zong(sp_uri=song['sp_uri'],yt_uri=song['yt_uri'],track=song['track'],artist=song['artist'])
                print('This is a {0} for {1}. This is a {2} for {3}.'.format(type(song['sp_uri']),song['sp_uri'],type(song['yt_uri']),song['yt_uri']      ))
                tsm.db.session.add(commit_song)
            commit_history = tsm.Zistory(uid=user['id'],zurl=song['yt_uri'],created_at=moment.utcnow().datetime.isoformat())
            tsm.db.session.add(commit_history)
            tsm.db.session.commit()
            return jsonify({'status':'ok','data':{'message':'available','latest_song_sp_id':song['sp_uri']}})
        else:
            print('No music found for {0}'.format(user['email']))
            return jsonify({'status':'ok','data':{'message':'unavailable'}})
    except:
        print('MAJOR ERROR AT BUMP: {0}'.format(sys.exc_info()[0]))
        raygun.send_exception(exc_info=sys.exc_info())
        return jsonify({'status':'fail','error':'error'})


# Get user's information
@app.route('/ts/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    a = time.clock()
    user = tsm.get_user(uid=user_id)
    b = time.clock()
    delta = b-a
    return jsonify({'status':'ok','data':user,'execution_time':delta})

# Get a user's history
@app.route('/ts/api/users/<int:user_id>/history', methods=['GET'])
def get_user_history(user_id):
    a = time.clock()
    user = tsm.get_user(uid=user_id)
    b = time.clock()
    delta = b-a
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
@app.route('/ts/api/playlist/<int:p_id>', methods=['GET'])
def view_playlist(p_id):
    a = time.clock()
    songs = tsm.get_playlist_songs(pl_id=p_id)
    b = time.clock()
    delta = b-a
    tsm.db.session.close()
    return jsonify({'status':'ok','data':songs,'execution_time':delta})

# Create a new playlist
@app.route('/ts/api/generate/recommendation', methods=['POST'])
def create_recommendation():
    message = 'Route: Recommendation'
    t = moment.utcnow().datetime.isoformat()
    location = request.json['location']
    location = 'JAMAICA'
    uone = request.json['uone']
    utwo = request.json['utwo']

    t0 = time.time()
    # hone = tsm.get_history(uone['id'])
    # htwo = tsm.get_history(utwo['id'])
    # histories = tsm.get_faster_history(uone['id'],utwo['id'])
    histories = tsm.zzzistory(uone['id'],utwo['id'])
    s1 = time.time() - t0
    step = 1
    # fb_notification(recipient=uone['id'],message=message,created_at=s1,step=step)
    # fb_notification(recipient=utwo['id'],message=message,created_at=s1,step=step)
    # ~ 3 seconds

    t1 = time.time()
    try:
        tunesmash = tsr.generate_recommendations(histories[uone['id']]['sp_uri'],histories[utwo['id']]['sp_uri'],100)
        tunesmash = tsr.add_audio_features(tunesmash)
        tunesmash = tsr.bell_sort(tunesmash)
        tunesmash = tsr.remove_ids(tunesmash)
    except:
        print('MAJOR ERROR AT BUMP: {0}'.format(sys.exc_info()[0]))
        raygun.send_exception(exc_info=sys.exc_info())
        return jsonify({'status':'fail','execution_times':{1:s1}})
    s2 = time.time() - t1
    step = 2
    # fb_notification(recipient=uone['id'],message=message,created_at=s2,step=step)
    # fb_notification(recipient=utwo['id'],message=message,created_at=s2,step=step)
    # ~ 3 seconds


    t2 = time.time()
    try:
        youtube = tsr.get_authenticated_service(uone['email'])
        ytpid = tsr.generate_yt_playlist(yt=youtube,uone=uone['email'],utwo=utwo['email'],t=t2)
    except tsr.HttpError as err:
        e = err
        print(e.content,file=sys.stderr)
        print('MAJOR ERROR AT BUMP: {0}'.format(sys.exc_info()[0]))
        raygun.send_exception(exc_info=sys.exc_info())
        return jsonify({'status':'fail','execution_times':{1:s1,2:s2}})
    s3 = time.time() - t2
    step = 3
    # fb_notification(recipient=uone['id'],message=message,created_at=s3,step=step)
    # fb_notification(recipient=utwo['id'],message=message,created_at=s3,step=step)
    # ~ 3 seconds

    t3 = time.time()
    try:
        videos = tsr.test_populate(youtube,tunesmash,ytpid)
        [tunesmash[i].append(videos[i])  for i in range(len(videos))]
    except:
        print('MAJOR ERROR AT BUMP: {0}'.format(sys.exc_info()[0]))
        raygun.send_exception(exc_info=sys.exc_info())
        return jsonify({'status':'fail','execution_times':{1:s1,2:s2,3:s3}})
    s4 = time.time() - t3
    step = 4
    # fb_notification(recipient=uone['id'],message=message,created_at=s4,step=step)
    # fb_notification(recipient=utwo['id'],message=message,created_at=s4,step=step)
    # ~ 4 seconds

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

    t5 = time.time()
    try:
        song_run(tunesmash,ytpid)
    except:
        print('MAJOR ERROR AT BUMP: {0}'.format(sys.exc_info()[0]))
        raygun.send_exception(exc_info=sys.exc_info())
        return jsonify({'status':'fail','execution_times':{1:s1,2:s2,3:s3,4:s4,5:s5}})
    s6 = time.time() - t5

    # fdbdata = {
    #     'time':time,
    #     'from':uone['id'],
    #     'to':utwo['id'],
    #     'plid':plid
    # }
    # fdb.child("notification").push(fdbdata)
    # tsm.db.session.close()
    return jsonify({'status':'ok','data':{'playlist_url':ytpid,'playlist_id':ytpid},'execution_times':{1:s1,2:s2,3:s3,4:s4,5:s5,6:s6}})

def fb_notification(recipient=None,message=None,created_at=None,step=0):
    fdbdata = {
        'recipient':recipient,
        'message': message,
        'created_at': created_at,
        'step': step
    }
    fdb.child("notification").push(fdbdata)

def song_run(songs,pl):
    new = []
    plob = []
    for s in songs:
        try:
            match = tsm.db.session.query(tsm.db.exists().where(
                tsm.db.and_(
                    tsm.Zong.yt_uri == s[3]
                )
            )).scalar()
            if match == True:
                print('This song is already in the db {0}'.format(s[3]))
            else:
                new.append(tsm.Zong(track=s[0],artist=s[1],sp_uri=s[2],yt_uri=s[3]))
            plob.append(tsm.Pongz(pl,s[3]))
        except:
            print('$$$ MAJOR FUCKING ERROR $$$')
            raygun.send_exception(exc_info=sys.exc_info())
            tsm.db.session.rollback()
    tsm.db.session.add_all(new)
    tsm.db.session.add_all(plob)
    tsm.db.session.commit()

@app.errorhandler(Exception)
def unhandled_exception(e):
    print('Unhandled Exception: {0}'.format(e))
    raygun.send_exception(exc_info=sys.exc_info())
    return render_template('error.html',err = str(e))

# might to need make one for every exception type like typerror,integrityerror, etc
# write a class http://flask.pocoo.org/docs/0.11/patterns/apierrors/

# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('404.html'), 404
if __name__ == "__main__":
    app.run(debug = True)
