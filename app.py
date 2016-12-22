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
import time
import moment
from dateutil.parser import parse
import ts_authentication as tsa
import ts_recommendation as tsr
import ts_models as tsm
import ts_utils as tsu
from flask import Flask, request, session, redirect, render_template,jsonify

app = Flask(__name__, static_url_path='')
app.config['DEBUG'] = True
app.secret_key = 'duylamduylam'

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 604800


@app.route('/')
def index():
    session.permanent = True
    pprint.pprint(session)
    # session.pop('user')
    if 'user' in session:
        user = tsm.get_full_user(session['user']['id'])
        session['user'] = user

        d = datetime.datetime.now(pytz.utc)
        session['user']['lost_login'] = d
        if (d - session['user']['lost_login']) > datetime.timedelta(minutes=1):
            session['user']['lost_login'] = d
            tsm.db.session.close()
            return render_template('new_song.html',user_id=session['user']['id'])
        else:
            session['user']['lost_login'] = d
            user_transport = session['user']
            tsm.db.session.close()
            return render_template('home.html')
    else:
        return render_template('index.html')

@app.route('/playlists')
def view_playlists():
    playlists = tsm.get_all_playlists(uid=session['user']['id'])
    tsm.db.session.close()
    return render_template('playlists.html',user=playlists)

@app.route('/playlists/<playlist_id>')
def view_delete_playlists(playlist_id):
    user_name = session['user']['name']
    return render_template('playlist_delete.html',playlist_id=playlist_id,user_name=user_name)

@app.route('/playlists/<playlist_id>/delete/confirmed')
def view_delete_playlist_forever(playlist_id):
    tsm.Playlist.query.filter(tsm.Playlist.id == playlist_id).delete()
    tsm.db.session.commit()
    tsm.db.session.close()
    return redirect('/')


@app.route('/logout')
def view_logout():
    print(session)
    if 'user' in session:
        session.pop('user')
    return redirect('/')

@app.route('/delete')
def view_delete():
    user_transport = session['user']
    if 'lost_login' in user_transport:
        user_transport.pop('lost_login')
    if 'token_expiry' in user_transport:
        user_transport.pop('token_expiry')
    return render_template('delete.html',user=user_transport)

@app.route('/delete/confirmed')
def view_delete_forever():
    # DELETE API
    user_id = session['user']['id']
    tsm.UserService.query.filter(tsm.UserService.user_id == user_id).delete()
    tsm.History.query.filter(tsm.History.user_id == user_id).delete()
    tsm.Playlist.query.filter(tsm.Playlist.sender == user_id).delete()
    tsm.User.query.filter(tsm.User.id==user_id).update({'name':'DEACTIVATED ACCOUNT'})
    tsm.db.session.commit()
    session.pop('user')
    return redirect('/')


@app.route('/account')
def view_account():
    user_transport = session['user']
    if 'lost_login' in user_transport:
        user_transport.pop('lost_login')
    if 'token_expiry' in user_transport:
        user_transport.pop('token_expiry')
    return render_template('profile.html',user=user_transport)

@app.route('/account/name')
def view_account_name():
    user_transport = session['user']
    if 'lost_login' in user_transport:
        user_transport.pop('lost_login')
    if 'token_expiry' in user_transport:
        user_transport.pop('token_expiry')
    return render_template('profile_name.html',user=user_transport)

@app.route('/account/avatar', methods=['GET'])
def view_profile_avatar():
    user_transport = session['user']
    if 'lost_login' in user_transport:
        user_transport.pop('lost_login')
    if 'token_expiry' in user_transport:
        user_transport.pop('token_expiry')
    return render_template('profile_avatar_gender.html',user=user_transport)

@app.route('/account/avatar/<gender>', methods=['GET'])
def view_profile_avatar_gender(gender):
    f  = list(range(0,20))
    colors = ["252,104,230","252,104,104","17,123,201","129,201,252","252,163,162"]
    k = []
    for i in f:
        k.append((i,random.choice(colors)))
    user_transport = session['user']
    if 'lost_login' in user_transport:
        user_transport.pop('lost_login')
    if 'token_expiry' in user_transport:
        user_transport.pop('token_expiry')
    return render_template('profile_avatar_gender_pictures.html',user=user_transport,gender=gender,f=k)


@app.route('/one')
def view_generate_one():
    user_transport = session['user']
    return render_template('generate_one.html',user=user_transport)

@app.route('/generate/two/<user_id>/<user_song>/<other_id>/<other_song>/<name>')
def view_generate_two(user_id,user_song,other_id,other_song,name):
    name = name.split(' ')
    name = name[0]
    user_transport = session['user']
    user_transport['bump'] = {
        'fr': user_id,
        'to': other_id,
        'songs': [user_song,other_song]
    }
    return render_template('generate_two.html',user=user_transport,name=name)

@app.route('/auth/yt/login')
def auth_yt_login():
    oauth = tsa.OAuthSignIn.get_provider("google")
    return redirect(oauth.authorize())

@app.route('/auth/yt/authenticate')
def auth_yt_authenticate():

    genders = random.choice(['female','male'])
    avatars = random.choice(list(range(0,20)))
    avatar = "/images/{0}/{1}.png".format(genders,avatars)
    d = datetime.datetime.now(pytz.utc)
    # try:

    oauth = tsa.OAuthSignIn.get_provider("google")
    credentials = oauth.callback()
    json_credentials = json.loads(credentials.to_json())
    user = tsm.does_user_exist(service_username=json_credentials['id_token']['email'])
    current_user = 'user' in session
    print(json_credentials['id_token']['email'])
    if user == None and current_user == False:
        print('CURRENT USER OUT AND DOES NOT HAVE THIS SERVICE')
        new_user = tsm.User(json_credentials['id_token']['given_name'],json_credentials['token_expiry'], avatar, d)
        tsm.db.session.add(new_user)
        tsm.db.session.flush()
        new_user_service = tsm.UserService(new_user.id,'youtube',json_credentials['id_token']['email'],json_credentials['access_token'],json_credentials['refresh_token'])
        tsm.db.session.add(new_user_service)
        tsm.db.session.commit()
        session['user'] = {'id':new_user.id}
        print('NEW USER {0}'.format(new_user.id))
        tsm.db.session.close()
        return redirect('/new/step1')
    elif user == None and current_user == True:
        print('CURRENT USER IN AND DOES NOT HAVE THIS SERVICE')
        new_user_service = tsm.UserService(session['user']['id'],'youtube',json_credentials['id_token']['email'],json_credentials['access_token'],json_credentials['refresh_token'])
        tsm.db.session.add(new_user_service)
        tsm.db.session.commit()
        tsm.db.session.close()
        return redirect('/')
    elif user != None and current_user == False:
        print('CURRENT USER OUT AND DOES HAVE THIS SERVICE')
        session['user'] = {'lost_login':d,'id':user}
        print('THIS IS USER {0}'.format(user))
        print(session)
        print("*********************************************")
        tsm.db.session.close()
        return redirect('/')
    elif user != None and current_user == True:
        print('CURRENT USER IN AND DOES HAVE THIS SERVICE')
        # this must then mean you are signing in from another account or you're clicking add youtube
        current_user_id = session['user']['id']
        if (int(user) == int(current_user_id)):
            tsm.db.session.close()
            return redirect('/')
        else:
            smallest_id = min(int(user),int(current_user_id))
            largest_id = max(int(user),int(current_user_id))
            session['user']['id'] = smallest_id
            bumps = tsm.Bump.query.filter(tsm.Bump.fr == largest_id).all()
            for i in bumps:
                i.fr = smallest_id
            histories = tsm.History.query.filter(tsm.History.user_id == largest_id).all()
            for j in histories:
                j.user_id = smallest_id
            playlists = tsm.Playlist.query.filter(tsm.Playlist.sender == largest_id).all()
            for k in playlists:
                k.sender = smallest_id
            user_services = tsm.UserService.query.filter(tsm.UserService.user_id == largest_id).all()
            for l in user_services:
                l.user_id = smallest_id
            old_user = tsm.User.query.filter(tsm.User.id == largest_id).first()
            old_user.avatar = '/images/merged.jpg'
            tsm.db.session.commit()
            tsm.db.session.close()
            return redirect('/')
        # what is the user id
        # what is the current users id
        # if they match then the person just clicked the add youtube button. so redirect them
        # if they do not match then this is a collision
        # take the earliest user id (smallest id) to use as the defacto
        # find all rows in playlists, history, bumps, and user services and update to the smallest id
        # set session user id as this smallest id
        # update larger id with some bullshit so we know it's a booty ass account
        print('user exists and is logged in')

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
    genders = random.choice(['female','male'])
    avatars = random.choice(list(range(0,20)))
    avatar = "/images/{0}/{1}.png".format(genders,avatars)
    pprint.pprint("WHAT")
    # pprint.pprint('this is the user {0}'.format(session['user']))
    # try:

    d = datetime.datetime.now(pytz.utc)
    oauth = tsa.OAuthSignIn.get_provider("spotify")
    oauth.callback()

    user_email = oauth.results['spotify_user_id']
    user_refresh_token = oauth.results['refresh_token']
    user_refresh_expiration = oauth.results['expires_at']
    user_access_token = oauth.results['access_token']
    user_name = oauth.results['name']
    user_spid_but_actually_its_their_email = oauth.results['email']

    user = tsm.does_user_exist(service_username=user_email)
    current_user = 'user' in session

    if user == None and current_user == False:
        print('CURRENT USER OUT AND DOES NOT HAVE THIS SERVICE')
        new_user = tsm.User(user_name,datetime.datetime.fromtimestamp(user_refresh_expiration), avatar, d)
        tsm.db.session.add(new_user)
        tsm.db.session.flush()
        new_user_service = tsm.UserService(new_user.id,'spotify',user_email,user_access_token,user_refresh_token)
        tsm.db.session.add(new_user_service)
        tsm.db.session.commit()
        session['user'] = {'id':new_user.id}
        tsm.db.session.close()
        return redirect('/new/step1')
    elif user == None and current_user == True:
        print('CURRENT USER IN AND DOES NOT HAVE THIS SERVICE')
        print("**********************")
        new_user_service = tsm.UserService(session['user']['id'],'spotify',user_email,user_access_token,user_refresh_token)
        tsm.db.session.add(new_user_service)
        tsm.db.session.commit()
        tsm.db.session.close()
        return redirect('/')

    elif user != None and current_user == False:
        print('CURRENT USER OUT AND DOES HAVE THIS SERVICE')
        session['user'] = {'lost_login':d,'id':user}
        tsm.db.session.close()
        return redirect('/')
    elif user != None and current_user == True:
        print('CURRENT USER IN AND DOES HAVE THIS SERVICE')
        # this must then mean you are signing in from another account or you're clicking add youtube
        current_user_id = session['user']['id']
        if (int(user) == int(current_user_id)):
            tsm.db.session.close()
            return redirect('/')
        else:
            smallest_id = min(int(user),int(current_user_id))
            largest_id = max(int(user),int(current_user_id))
            session['user']['id'] = smallest_id
            bumps = tsm.Bump.query.filter(tsm.Bump.fr == largest_id).all()
            for i in bumps:
                i.fr = smallest_id
            histories = tsm.History.query.filter(tsm.History.user_id == largest_id).all()
            for j in histories:
                j.user_id = smallest_id
            playlists = tsm.Playlist.query.filter(tsm.Playlist.sender == largest_id).all()
            for k in playlists:
                k.sender = smallest_id
            user_services = tsm.UserService.query.filter(tsm.UserService.user_id == largest_id).all()
            for l in user_services:
                l.user_id = smallest_id
            old_user = tsm.User.query.filter(tsm.User.id == largest_id).first()
            old_user.avatar = '/images/merged.jpg'
            tsm.db.session.commit()
            tsm.db.session.close()
            return redirect('/')
        # what is the user id
        # what is the current users id
        # if they match then the person just clicked the add youtube button. so redirect them
        # if they do not match then this is a collision
        # take the earliest user id (smallest id) to use as the defacto
        # find all rows in playlists, history, bumps, and user services and update to the smallest id
        # set session user id as this smallest id
        # update larger id with some bullshit so we know it's a booty ass account
        print('user exists and is logged in')



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
    created_at = datetime.datetime.now(pytz.utc)
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
    sender_commit_playlist = tsm.Playlist(sender=sender['id'],recipient=recipient['id'],created_at=datetime.datetime.now(pytz.utc),url=sender_playlist)
    recipient_commit_playlist = tsm.Playlist(sender=recipient['id'],recipient=sender['id'],created_at=datetime.datetime.now(pytz.utc),url=recipient_playlist)
    tsm.db.session.add(sender_commit_playlist)
    tsm.db.session.add(recipient_commit_playlist)
    tsm.db.session.commit()
    tsm.db.session.close()
    return jsonify({'status':'ok','sender_playlist':sender_playlist,'recipient_playlist':recipient_playlist})

@app.route('/ts/api/user/playlists', methods=['POST'])
def api_manage_playlist():
    user_id = request.json['user_id']
    playlists = tsm.get_all_playlists(uid=user_id)
    tsm.db.session.close()
    return jsonify({'status':'ok','data':playlists})

@app.route('/ts/api/user/update', methods=['POST'])
def avatar_update():
    field = request.json['update']
    data = request.json['data']
    user_id = request.json['user_id']
    tsm.User.query.filter(tsm.User.id==user_id).update({field:data})
    tsm.db.session.commit()
    tsm.db.session.close()
    return jsonify({'status':'ok'})

if __name__ == "__main__":
    app.run(debug = True)
