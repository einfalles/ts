import spotipy
import spotipy.oauth2 as oauth
import csv
import time
import httplib2
import sys
import time
import re
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.contrib import multistore_file as oams
from datetime import datetime, timedelta

CLIENT_SECRETS_FILE = "client_secrets.json"
MISSING_CLIENT_SECRETS_MESSAGE ="NO NO NO NO"
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
sp_token = oauth.SpotifyClientCredentials(client_id='4f8c3338b0b443a8895358db33763c6f',client_secret='76cf6ff10bb041dbb0b11a3e7dd89fe1')
SP = spotipy.Spotify(auth=sp_token.get_access_token())

def get_watch_history(user):
    youtube = get_authenticated_service(user)
    channels_response = youtube.channels().list(mine=True,part="contentDetails").execute()
    for channel in channels_response["items"]:
        uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["watchHistory"]

    playlistitems_list_request = youtube.playlistItems().list(playlistId=uploads_list_id,part="snippet",maxResults=50)

    playlistitems_list_response = playlistitems_list_request.execute()
    for plitem in playlistitems_list_response["items"]:
        vid = plitem["snippet"]["resourceId"]["videoId"]
        vreq = youtube.videos().list(part="snippet",id=vid)
        vres = vreq.execute()
        for vitem in vres["items"]:
            category = vitem["snippet"]["categoryId"]
            if category == '10':
                track = re.split(' - +', vitem["snippet"]["title"])
                if len(track) > 1:
                    try:
                        results = SP.search(q='artist:'+track[0] + ' AND ' + 'track:'+track[1], type='track')
                        if len(results['tracks']['items'])>0:
                            song = results['tracks']['items'][0]
                            return (track[0],track[1],vid,song['id'])
                    except spotipy.SpotifyException:
                        print(track)
                        print(spotipy.SpotifyException)
                        pass
    # playlistitems_list_request = youtube.playlistItems().list_next(playlistitems_list_request, playlistitems_list_response)
    return None

def array_to_csv(history,user_email):
    fl_name = str(user_email) +'_history.csv'
    fl = open(fl_name, 'w')
    writer = csv.writer(fl)
    writer.writerow(['artist', 'track']) #if needed
    for values in history:
        writer.writerow(values)
    fl.close()

def csv_to_array(user):
    filename = str(user)+'_history.csv'
    with open(filename, 'rU') as f:
        reader = csv.reader(f)
        your_list= list(reader)
    return your_list

def sp_add_spid(history):
    for song in history:
        try:
            artist = song[0]
            title = song[1]
            results = SP.search(q='artist:'+ artist +' AND '+'track:'+ title,type='track')
            items = results['tracks']['items']
            if len(items)>0:
                for i in items:
                    song.append(str(i['id']))
        except:
            print(song)
            history.remove(song)
    return history

def generate_recommendations(seed_one, seed_two,limit):
    recommendations = []
    unireq = {}
    seeds = [seed_one,seed_two]

    results = SP.recommendations(seed_tracks=seeds,max_popularity=limit,limit=60)
    results = results['tracks']

    while len(recommendations)<12:
        for song in results:
            track = song['artists'][0]['name'] + " " + song['album']['name'] + " " + song['name']
            if song['artists'][0]['name'] in unireq:
                pass
            else:
                unireq[song['artists'][0]['name']] = 'artist'
                recommendations.append((song['name'],song['artists'][0]['name'],song['id']))

    if len(recommendations)>12:
        recommendations = recommendations[0:12]

    return recommendations

def bell_sort(recommendations):
    recommendations.sort(key = lambda row: row[1])
    a = recommendations[0::2]
    b = recommendations[1::2]
    b.reverse()
    bell = a + b
    return bell

def wave_sort(recommendations):
    temp = []
    wave = []
    count = 0
    hist_bin = len(recommendations)/4 - 1
    for i in range(0,len(recommendations),4):
        a = recommendations[i:hist_bin+i]
        if count%2 == 0:
            a.sort(key=lambda row:row[1])
        else:
            a.sort(key=lambda row:row[1],reverse=True)
        temp.append(a)
        count = count + 1
    for i in temp:
        for j in i:
            wave.append(j)
    return wave

def remove_ids(recommendations):
    ar = []
    print('**** remove ids *****')
    for i in recommendations:
        ar.append(i[0])
    return ar

def add_audio_features(recommendations):
    print('**** add audio features ****')
    af = []
    sr = []
    song_titles = []
    song_artist = []
    song_sp_uri = []
    for i, (a,b,c) in enumerate(recommendations):
        song_titles.append(a)
        song_artist.append(b)
        song_sp_uri.append(c)
    results = SP.audio_features(tracks=song_sp_uri)
    for i in results:
        af.append(i['tempo'])
    for i,song in enumerate(recommendations):
        sr.append([recommendations[i],af[i]])
    return sr

def get_authenticated_service(user):
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    store = oams.get_credential_storage(filename='multi.json',client_id=user,user_agent='app',scope=['https://www.googleapis.com/auth/userinfo.profile','https://www.googleapis.com/auth/youtube'])
    creds = store.get()
    if creds is None or creds.invalid:
        creds.refresh(httplib2.Http())
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=creds.authorize(httplib2.Http()))
    return youtube

def generate_yt_playlist(yt,uone,utwo,t):
    playlist = yt.playlists().insert(
        part="snippet,status",
        body=dict(
            snippet=dict(
                title=str(t)+" * " + uone  + " and " + utwo,
                description="Tunesmash"
            ),
            status=dict(
                privacyStatus="public"
            )
        )
    ).execute()
    return playlist["id"]

def add_video_to_playlist(yt,videoID,playlistID):
    add_video_request = yt.playlistItems().insert(
        part="snippet",
        body={
                'snippet': {
                  'playlistId': playlistID,
                  'resourceId': {
                          'kind': 'youtube#video',
                      'videoId': videoID
                    }
                #'position': 0
                }
        }
    ).execute()


def populate_playlist(yt, recommendations, playlist_id):
    videos = []
    print("******* populating playlist *********")
    for song in recommendations:
        try:
            q = song[0] + " " + song[1]
            yt_request = yt.search().list(part="snippet",q=q,type="video")
            results = yt_request.execute()
            if len(results['items'])>0:
                videos.append(results['items'][0]['id']['videoId'])
        except HttpError as e:
            print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
            pass
    for video in videos:
        add_video_to_playlist(yt,video,playlist_id)
    for i,r in enumerate(recommendations):
        r = list(recommendations[i])
        r.append(videos[i])
        recommendations[i] = tuple(r)
    return recommendations

def run_generation(uone=None,utwo=None,hone=None,htwo=None,location=None, time=None,popularity_limit=60):
    tunesmash = generate_recommendations(hone,htwo,popularity_limit)
    tunesmash = add_audio_features(tunesmash)
    tunesmash = bell_sort(tunesmash)
    tunesmash = remove_ids(tunesmash)

    if uone['email'] == 'eat@rad.kitchen':
        youtube = get_authenticated_service(utwo['email'])
    else:
        youtube = get_authenticated_service(uone['email'])
    yt_playlist_id = generate_yt_playlist(yt=youtube,uone=uone['email'],utwo=utwo['email'],t=time)
    songs = populate_playlist(youtube,tunesmash,yt_playlist_id)
    data = {
        'playlist_url': yt_playlist_id,
        'uone':uone['email'],
        'utwo':utwo['email'],
        'time': time,
        'location': location,
        'songs': songs
    }
    return data
