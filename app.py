# handle does user already exist issue
# something wrong with time
# ignore time for now...move on to ensuring successfulbumps
# but before enable spotify login
# instead of asking for input just go straight to home
# when creating yt credentials you need to use accesscredentials object
# search up how people turn spotify playlists into youtube playlists
# see all the playlists you've made
# change your avatar and name

import pytz
import json
import sys
import pprint
import random
import datetime
<<<<<<< HEAD
import time
import moment
import ts_authentication as tsa
import ts_recommendation as tsr
=======

import ts_auth as tsa
import ts_recommendations as tsr
>>>>>>> parent of d2f02c1... the next step is to break out each of the spotify functions into separate apis and then get each screen to call each api.
import ts_models as tsm
import ts_utils as tsu
from flask import Flask, request, session, redirect, render_template,jsonify

app = Flask(__name__, static_url_path='')
app.config['DEBUG'] = True
app.secret_key = 'duylamduylam'
<<<<<<< HEAD
=======
app.config['OAUTH_CREDENTIALS'] = {
    'google':{
        'id':'423012525826-42ued2niiiecpuvrehd445n83kt16ano.apps.googleusercontent.com',
        'secret':'e2oBEpfgl3HVwU94UjFolXL8'
    }
}
# app.config['PROFILE'] = True
# app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 604800
raygun = raygunprovider.RaygunSender("aR9aPioLxr1y42IN3HqSnw==")
>>>>>>> parent of d2f02c1... the next step is to break out each of the spotify functions into separate apis and then get each screen to call each api.

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 604800

<<<<<<< HEAD
=======
#
# ROUTING
#
@app.route('/loaderio-c54d3912e32128c85bd19987caf3561e')
def loaderio():
    return send_file('/js/loaderio-c54d3912e32128c85bd19987caf3561e.txt', attachment_filename='loaderio-c54d3912e32128c85bd19987caf3561e.txt')
>>>>>>> parent of d2f02c1... the next step is to break out each of the spotify functions into separate apis and then get each screen to call each api.

@app.route('/')
def index():
    # session.pop('user')
    if 'user' in session:
        user = tsm.get_full_user(session['user']['id'])
        session['user'] = user

        d = datetime.datetime.now(pytz.utc)
        print("Lost login before CHECK {0}".format(session['user']['lost_login']))
        session['user']['lost_login'] = d
        if (d - session['user']['lost_login']) > datetime.timedelta(minutes=1):
            session['user']['lost_login'] = d
            print("Lost login before New Song {0}".format(session['user']['lost_login']))
            return render_template('new_song.html',user_id=session['user']['id'])
        else:
            session['user']['lost_login'] = d
            user_transport = session['user']
            return render_template('home.html')
    else:
        return render_template('index.html')
@app.route('/playlists')
def view_playlists():
    playlists = tsm.get_all_playlists(uid=session['user']['id'])
    pprint.pprint(playlists)
    return render_template('playlists.html',user=playlists)

@app.route('/one')
def view_generate_one():
    user_transport = session['user']
    return render_template('generate_one.html',user=user_transport)

@app.route('/generate/two/<user_id>/<user_song>/<other_id>/<other_song>')
def view_generate_two(user_id,user_song,other_id,other_song):
    user_transport = session['user']
    user_transport['bump'] = {
        'fr': user_id,
        'to': other_id,
        'songs': [user_song,other_song]
    }
    print(user_transport['bump']['songs'])
    return render_template('generate_two.html',user=user_transport)


@app.route('/auth/yt/login')
def auth_yt_login():
    oauth = tsa.OAuthSignIn.get_provider("google")
    return redirect(oauth.authorize())

<<<<<<< HEAD
@app.route('/auth/yt/authenticate')
def auth_yt_authenticate():
    avatars = ['http://24.media.tumblr.com/Jjkybd3nSaqkbdxdY4fYtymI_500.jpg','http://25.media.tumblr.com/tumblr_m1287x1hpN1qjahcpo1_500.jpg','http://25.media.tumblr.com/tumblr_lu6ch9jMg51r4xjo2o1_1280.jpg']
    avatar = random.choice(avatars)
    # try:
    d = datetime.datetime.now(pytz.utc)
    session['user'] = {'lost_login':d}
    oauth = tsa.OAuthSignIn.get_provider("google")
    credentials = oauth.callback()
    json_credentials = json.loads(credentials.to_json())
    pprint.pprint(json_credentials)
    user = tsm.get_user(service_username=json_credentials['id_token']['email'])
    if user == None:
        new_user = tsm.User(json_credentials['id_token']['given_name'],json_credentials['token_expiry'], avatar, d)
        tsm.db.session.add(new_user)
        tsm.db.session.flush()
        new_user_service = tsm.UserService(new_user.id,'youtube',json_credentials['id_token']['email'],json_credentials['access_token'],json_credentials['refresh_token'])
        tsm.db.session.add(new_user_service)
        tsm.db.session.commit()
        session['user'] = {'id':new_user.id}
        return redirect('/new/step1')
    else:
        return redirect('/')
    # except:
    #     e = sys.exc_info()
    #     print("NO {0}".format(e))
    #     return "BIG PROBLEM BUD"

@app.route('/auth/sp/login')
def auth_sp_login():
    oauth = tsa.OAuthSignIn.get_provider("spotify")
    return redirect(oauth.authorize())

@app.route('/auth/sp/authenticate')
def auth_sp_authenticate():
    avatars = ['http://24.media.tumblr.com/Jjkybd3nSaqkbdxdY4fYtymI_500.jpg','http://25.media.tumblr.com/tumblr_m1287x1hpN1qjahcpo1_500.jpg','http://25.media.tumblr.com/tumblr_lu6ch9jMg51r4xjo2o1_1280.jpg']
    avatar = random.choice(avatars)
    # try:
    d = datetime.datetime.now(pytz.utc)
    session['user'] = {'lost_login':d}
    oauth = tsa.OAuthSignIn.get_provider("spotify")
    oauth.callback()

    user_email = oauth.results['spotify_user_id']
    user_refresh_token = oauth.results['refresh_token']
    user_refresh_expiration = oauth.results['expires_at']
    user_access_token = oauth.results['access_token']
    user_name = oauth.results['name']
    user_spid_but_actually_its_their_email = oauth.results['email']

    user = tsm.get_user(service_username=user_email)
    if user == None:
        new_user = tsm.User(user_name,datetime.datetime.fromtimestamp(user_refresh_expiration), avatar, d)
        tsm.db.session.add(new_user)
        tsm.db.session.flush()
        new_user_service = tsm.UserService(new_user.id,'spotify',user_email,user_access_token,user_refresh_token)
        tsm.db.session.add(new_user_service)
        tsm.db.session.commit()
        session['user'] = {'id':new_user.id}
        return redirect('/new/step1')
    else:
        return redirect('/')

    if user == None:
        user = tsm.User(user_name,user_email,'/images/female/0.png')
        tsm.db.session.add(user)
        tsm.db.session.flush()
        session['credentials']['id_token']['ts_uid'] = user.id
        tsm.db.session.commit()
    else:
        session['credentials']['id_token']['ts_uid'] = user['id']


=======
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
>>>>>>> parent of d2f02c1... the next step is to break out each of the spotify functions into separate apis and then get each screen to call each api.

@app.route('/new/step1')
def view_new_one():
    return render_template('new_song.html',user_id=session['user']['id'])

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ #
# API
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ #
@app.route('/ts/api/user/history', methods=['POST'])
def api_user_history():
    user_id = request.json['user_id']
    spotify_id = request.json['spotify_id']
    d = datetime.datetime.now(pytz.utc)
    new_history = tsm.History(user_id,spotify_id,d)
    tsm.db.session.add(new_history)
    tsm.db.session.commit()
    return jsonify({'status':'ok','data':spotify_id})

@app.route('/ts/api/user/bump', methods=['POST'])
def api_user_bump():
    sender = request.json['fr']
    recipient = request.json['to']
    time.sleep(2)
    created_at = moment.utcnow().datetime
    delta = datetime.timedelta(minutes=1)
    limit = created_at - delta
    winner = False
    match = tsm.db.session.query(tsm.db.exists().where(
        tsm.db.and_(
            tsm.Bump.created_at >= limit,
            tsm.Bump.fr == recipient,
            tsm.Bump.too == sender
        )
    )).scalar()
    # try:
    if match == True:
        print('true!')
        winner = True
    bump = tsm.Bump(fr=sender,too=recipient,created_at=created_at.isoformat())
    tsm.db.session.add(bump)
    tsm.db.session.commit()
    tsm.db.session.close()
    return jsonify({'status':'ok','data':{'step':1,'winner':winner}})

    # except:
        # print('MAJOR ERROR AT BUMP: {0}'.format(sys.exc_info()[0]))
        # raygun.send_exception(exc_info=sys.exc_info())
        # return jsonify({'status':'fail','error':'error'})
    return jsonify({'status':'ok','data':'spotify_id'})

@app.route('/ts/api/user/recommendation', methods=['POST'])
def api_user_recommendation():
    seeds = request.json['songs']
    sender = request.json['fr']
    recipient = request.json['to']
    sp = tsr.spotify_client()
    # recommendation_songs = tsr.sp_get_user_recommendations(sp,seeds)
    recommendation_songs = tsr.recommendations(seeds,50,sp)
    recommendation_searches = []
    recommendation_ids = []
    for i in range(len(recommendation_songs)):
        recommendation_searches.append(recommendation_songs[i][0:2])
        recommendation_ids.append(recommendation_songs[i][2])

    print("Just generated your recommendations {0}".format(recommendation_songs))
    sender = tsm.get_full_user(uid=sender)
    recipient = tsm.get_full_user(uid=recipient)
    recipient_playlist = None
    sender_playlist = None

    if ('youtube' in recipient) and ('spotify' not in recipient):
        print('recipient has youtube')
        # OAUTH SHIT
        credentials = tsr.youtube_credentials(recipient['youtube']['access_token'],recipient['youtube']['refresh_token'],recipient['token_expiry'])
        youtube = tsr.youtube_client(credentials)
        tsu.fb_notification(recipient['id'], 'Generating songs now')
        video_ids = tsr.yt_search_songs(youtube, recommendation_searches)
        playlist_id = tsr.yt_create_playlist(youtube,sender['name'])
        tsr.yt_create_playlist_songs(youtube,playlist_id,video_ids)
        tsu.fb_notification(recipient['id'], 'Creating playlist')
        recipient_playlist = 'https://www.youtube.com/playlist?list={0}'.format(playlist_id)


    if 'spotify' in recipient:
        print('recipient has spotify')
        tsu.fb_notification(recipient['id'], 'Generating songs now')
        oauth = tsa.OAuthSignIn.get_provider("spotify")
        new_token = oauth.refresh(refresh_token=recipient['spotify']['refresh_token'])
        sp = tsr.sp_user_client(sender['spotify']['access_token'])
        playlist = tsr.sp_create_user_playlist(sp,recipient['spotify']['service_username'],recommendations_ids,recipient['name'],sender['name'])
        recipient_playlist = playlist['external_urls']['spotify']
        tsu.fb_notification(recipient['id'], 'Creating playlist')

    if ('youtube' in sender) and ('spotify' not in sender):
        print('sender has youtube')
        # OAUTH SHIT
        credentials = tsr.youtube_credentials(sender['youtube']['access_token'],sender['youtube']['refresh_token'],sender['token_expiry'])
        youtube = tsr.youtube_client(credentials)
        tsu.fb_notification(sender['id'], 'Generating songs now')
        video_ids = tsr.yt_search_songs(youtube, recommendation_searches)
        playlist_id = tsr.yt_create_playlist(youtube,recipient['name'])
        tsr.yt_create_playlist_songs(youtube,playlist_id,video_ids)
        tsu.fb_notification(sender['id'], 'Creating playlist')
        sender_playlist = 'https://www.youtube.com/playlist?list={0}'.format(playlist_id)

    if 'spotify' in sender:
        print('sender has spotify')
        tsu.fb_notification(sender['id'], 'Generating songs now')
        oauth = tsa.OAuthSignIn.get_provider("spotify")
        new_token = oauth.refresh(refresh_token=sender['spotify']['refresh_token'])
        sp = tsr.sp_user_client(sender['spotify']['access_token'])
        playlist = tsr.sp_create_user_playlist(sp,sender['spotify']['service_username'],recommendation_ids,sender['name'],recipient['name'])
        sender_playlist = playlist['external_urls']['spotify']
        tsu.fb_notification(sender['id'], 'Creating playlist')

    tsu.fb_notification(recipient['id'], 'Playlist made! Check it out.',custom={'playlist_url':recipient_playlist})
    tsu.fb_notification(sender['id'], 'Playlist made! Check it out.',custom={'playlist_url':sender_playlist})
    sender_commit_playlist = tsm.Playlist(sender=sender['id'],recipient=recipient['id'],created_at=datetime.datetime.utcnow(),url=sender_playlist)
    recipient_commit_playlist = tsm.Playlist(sender=recipient['id'],recipient=sender['id'],created_at=datetime.datetime.utcnow(),url=recipient_playlist)
    tsm.db.session.add(sender_commit_playlist)
    tsm.db.session.add(recipient_commit_playlist)
    tsm.db.session.commit()
    return jsonify({'status':'ok','sender_playlist':sender_playlist,'recipient_playlist':recipient_playlist})

@app.route('/ts/api/user/playlists', methods=['POST'])
def api_manage_playlist():
    user_id = request.json['user_id']
    playlists = tsm.get_all_playlists(uid=user_id)
    tsm.db.session.close()
    return jsonify({'status':'ok','data':playlists})


if __name__ == "__main__":
    app.run(debug = True)
