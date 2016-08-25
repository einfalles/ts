import spotipy
import spotipy.oauth2 as oauth
import csv
import time
import httplib2
import sys
import time
import re
import requests
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.contrib import multistore_file as oams
from datetime import datetime, timedelta

CLIENT_SECRETS_FILE = "client_secrets.json"
MISSING_CLIENT_SECRETS_MESSAGE ="NO NO NO NO"
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_API_KEY = "AIzaSyD8kls0eIplOLZ1B-Arf8_wlfQSnJkBFmg"

sp_token = oauth.SpotifyClientCredentials(client_id='4f8c3338b0b443a8895358db33763c6f',client_secret='76cf6ff10bb041dbb0b11a3e7dd89fe1')
SP = spotipy.Spotify(auth=sp_token.get_access_token())
sp = SP

def get_history_id(youtube=None):
    channels_response = youtube.channels().list(mine=True,part="contentDetails").execute()
    for channel in channels_response["items"]:
        hid = channel["contentDetails"]["relatedPlaylists"]["watchHistory"]
    return hid

def is_history_new(youtube=None,user_email=None,etag=None,hid=None):
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    YOUTUBE_API_KEY = "AIzaSyD8kls0eIplOLZ1B-Arf8_wlfQSnJkBFmg"
    store = oams.get_credential_storage(filename='multi.json',client_id=user_email,user_agent='app',scope=['https://www.googleapis.com/auth/userinfo.profile','https://www.googleapis.com/auth/youtube'])
    creds = store.get()
    if creds is None or creds.invalid:
        creds.refresh(httplib2.Http())
    token = creds.access_token
    resource = "/playlists"
    base = "https://www.googleapis.com/youtube/v3"
    params = "?part=snippet&key={0}&access_token={1}&id={2}".format(YOUTUBE_API_KEY,token,hid)
    url = base  + resource + params
    r = requests.get(url)
    r = r.json()
    r = r['items'][0]['etag']
    print('this is etag from tsr')
    print(r)
    go = True

    if r == etag:
        go = False
    data = {
        'refresh': go,
        'etag': r
    }
    return data

def get_latest_song(user_email=None,hid=None,youtube=None):
    history_request = youtube.playlistItems().list(playlistId=hid,part="snippet",maxResults=50)
    history_response = history_request.execute()
    history_ids = [i['snippet']['resourceId']['videoId'] for i in history_response['items']]
    bulk_history_ids = ','.join(history_ids)
    videos_request = youtube.videos().list(part='snippet',id=bulk_history_ids,fields='etag,items(etag,fileDetails(durationMs,fileName),id,kind,snippet(categoryId,title)),nextPageToken')
    videos_response = videos_request.execute()
    untested_songs = [i['snippet']['title'] for i in videos_response['items'] if i['snippet']['categoryId']=='10']
    s = []
    for i in range(len(untested_songs)):
         a = re.sub('\s?\(.+\)\s?','',untested_songs[i])
         b = re.sub('\s?\[.+\]\s?','',a)
         c = re.sub('\s?official lyric video\s?','',b,flags=re.IGNORECASE)
         d = re.split('\s?-\s?',c)
         s.append(d)
    for i in range(len(s)):
        print('Jigga is at: {0}'.format(i))
        try:
            results = SP.search(q='artist:'+s[i][0] + ' AND ' + 'track:'+s[i][1], type='track')
            if len(results['tracks']['items'])>0:
                data = {
                    'sp_uri':results['tracks']['items'][0]['id'],
                    'track': results['tracks']['items'][0]['name'],
                    'artist': results['tracks']['items'][0]['artists'][0]['name'],
                    'yt_uri': history_ids[i]
                }
                return data
        except spotipy.SpotifyException as err:
            print('$$$ MEGA EXCEPTION: SPOTIFY SEARCH $$$')
            print(err)
    return None

def get_watch_history(user):
    youtube = get_authenticated_service(user)
    channels_response = youtube.channels().list(mine=True,part="contentDetails").execute()
    for channel in channels_response["items"]:
        uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["watchHistory"]
# is there an etag?
# etags will be useful so we can watch for changes...at least that's what it's meant for..
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

    while len(recommendations)<2:
        for song in results:
            track = song['artists'][0]['name'] + " " + song['album']['name'] + " " + song['name']
            if song['artists'][0]['name'] in unireq:
                pass
            else:
                unireq[song['artists'][0]['name']] = 'artist'
                recommendations.append([song['name'],song['artists'][0]['name'],song['id']])
            if len(recommendations) == 12:
                return recommendations

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
    [i.pop(3) for i in recommendations]
    return recommendations

def add_audio_features(recommendations):
    print('**** add audio features ****')
    spuri = []
    tempos = []
    spuri = [i[2] for i in recommendations]
    results = SP.audio_features(tracks=spuri)
    tempos = [i['tempo'] for i in results]
    [recommendations[i].append(tempos[i]) for i in range(len(tempos))]
    return recommendations

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
                privacyStatus="private"
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
#

# takes about 10 seconds

# takes about 10 seconds

# implement async to make this appear faster???
def populate_playlist(yt, recommendations, playlist_id):
    videos = []
    print("******* populating playlist *********")
    count = 0
    for song in recommendations:
        query = song[0] + " " + song[1]
        ytsr = yt.search().list(part='snippet',q=query,type='video')
        results = ytsr.execute()

        if len(results['items'])>0:
            count = count + 1
            print(count)
            videos.append(results['items'][0]['id']['videoId'])
            add_video_request = yt.playlistItems().insert(
                part="snippet",
                body={
                        'snippet': {
                          'playlistId': playlist_id,
                          'resourceId': {
                                  'kind': 'youtube#video',
                              'videoId': results['items'][0]['id']['videoId']
                            }
                        #'position': 0
                        }
                }
            ).execute()
    return videos

def test_populate(yt, recommendations, playlist_id):
    videos = []
    print("******* populating playlist *********")
    count = 0
    for song in recommendations:
        query = song[0] + " " + song[1]
        ytsr = yt.search().list(part='snippet',q=query,type='video')
        results = ytsr.execute()

        if len(results['items'])>0:
            count = count + 1
            print(count)
            videos.append(results['items'][0]['id']['videoId'])
            # add_video_request = yt.playlistItems().insert(
            #     part="snippet",
            #     body={
            #             'snippet': {
            #               'playlistId': playlist_id,
            #               'resourceId': {
            #                       'kind': 'youtube#video',
            #                   'videoId': results['items'][0]['id']['videoId']
            #                 }
            #             #'position': 0
            #             }
            #     }
            # ).execute()
    return videos

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
