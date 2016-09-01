import spotipy
import spotipy.oauth2 as oauth
import httplib2
import pprint
import re
import requests
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.contrib import multistore_file as oams
from datetime import datetime, timedelta
from apiclient.http import BatchHttpRequest

CLIENT_SECRETS_FILE = "client_secrets.json"
MISSING_CLIENT_SECRETS_MESSAGE ="NO NO NO NO"
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_API_KEY = "AIzaSyD8kls0eIplOLZ1B-Arf8_wlfQSnJkBFmg"


# ~~~~~~~~~~~~~~~~~
#
# Step 1
#
# ~~~~~~~~~~~~~~~~~
def youtube_credentials(user_email):
    store = oams.get_credential_storage(filename='multi.json',client_id=user_email,user_agent='app',scope=['https://www.googleapis.com/auth/userinfo.profile','https://www.googleapis.com/auth/youtube'])
    credentials = store.get()
    if credentials is None or credentials.invalid:
        credentials.refresh(httplib2.Http())
    return credentials

def youtube_client(credentials):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))
    return youtube

def spotify_client():
    sp_token = oauth.SpotifyClientCredentials(client_id='4f8c3338b0b443a8895358db33763c6f',client_secret='76cf6ff10bb041dbb0b11a3e7dd89fe1')
    return spotipy.Spotify(auth=sp_token.get_access_token())

def youtube_client_cli(email):
    CLIENT_SECRETS_FILE = "client_secrets.json"
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SCOPE,message=MISSING_CLIENT_SECRETS_MESSAGE)
    flow.params['access_type'] = 'offline'
    store = oams.get_credential_storage(filename='multi.json',client_id=email,user_agent='app',scope=['https://www.googleapis.com/auth/youtube','https://www.googleapis.com/auth/userinfo.profile'])
    credentials = store.get()
    if credentials is None or credentials.invalid == True:
        credentials = run_flow(flow, store)
    store.put(credentials)
    return credentials

# ~~~~~~~~~~~~~~~~~
#
# Step 2
#
# ~~~~~~~~~~~~~~~~~

def playlist_history_id(youtube=None):
    channels_response = youtube.channels().list(mine=True,part="contentDetails").execute()
    for channel in channels_response["items"]:
        hid = channel["contentDetails"]["relatedPlaylists"]["watchHistory"]
    return hid

def is_history_updated(credentials=None, youtube=None,user_email=None,etag=None,hid=None):
    token = credentials.access_token
    resource = "/playlists"
    base = "https://www.googleapis.com/youtube/v3"
    params = "?part=snippet&key={0}&access_token={1}&id={2}".format(YOUTUBE_API_KEY,token,hid)
    url = base  + resource + params
    r = requests.get(url)
    r = r.json()
    r = r['items'][0]['etag']
    go = True
    if r == etag:
        go = False
    data = {
        'refresh': go,
        'etag': r
    }
    return data

def latest_song(user_email=None,hid=None,youtube=None,spotify=None):
    # playlistitems_list_request = youtube.playlistItems().list_next(playlistitems_list_request, playlistitems_list_response)

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
        if len(s[i]) >= 2:
            results = spotify.search(q='artist:'+s[i][0] + ' AND ' + 'track:'+s[i][1], type='track')
        else:
            results = spotify.search(q=s[i][0], type='track')
        if len(results['tracks']['items'])>0:
            data = {
                'sp_uri':results['tracks']['items'][0]['id'],
                'track': results['tracks']['items'][0]['name'],
                'artist': results['tracks']['items'][0]['artists'][0]['name'],
                'yt_uri': history_ids[i]
            }
            return data
    return None

# ~~~~~~~~~~~~~~~~~
#
# Step 3
#
# ~~~~~~~~~~~~~~~~~
def recommendations(seed_one, seed_two,limit,spotify):
    recommendations = []
    unireq = {}
    seeds = [seed_one,seed_two]
    results = spotify.recommendations(seed_tracks=seeds,max_popularity=limit,limit=60)
    results = results['tracks']

    for song in results:
        if song['artists'][0]['name'] in unireq:
            pass
        else:
            unireq[song['artists'][0]['name']] = 'artist'
            recommendations.append([song['name'],song['artists'][0]['name'],song['id']])

    if len(recommendations) > 12:
        recommendations = recommendations[0:12]

    return recommendations

# ~~~~~~~~~~~~~~~~~
#
# Step 5
#
# ~~~~~~~~~~~~~~~~~
def insert_playlist(youtube,uone,utwo,t):
    playlist = youtube.playlists().insert(
        part="snippet,status",
        body=dict(
            snippet=dict(
                title="Created with {0} on {1}".format(utwo,t),
                description="Tunesmash"
            ),
            status=dict(
                privacyStatus="public"
            )
        )
    ).execute()
    return playlist["id"]

def insert_playlist_videos(youtube, recommendations, playlist_id):
    videos = []
    count = 0
    # could use rest api...couldcut this down....
    for song in recommendations:
        query = song[0] + " " + song[1]
        ytsr = youtube.search().list(part='snippet',q=query,type='video')
        results = ytsr.execute()

        if len(results['items'])>0:
            count = count + 1
            videos.append(results['items'][0]['id']['videoId'])
            add_video_request = youtube.playlistItems().insert(
                part="snippet",
                body={
                        'snippet': {
                          'playlistId': playlist_id,
                          'resourceId': {
                                  'kind': 'youtube#video',
                              'videoId': results['items'][0]['id']['videoId']
                            }
                        }
                }
            ).execute()
    return videos

# ~~~~~~~~~~~~~~~~~
#
# HELPER FUNCTIONS
#
# ~~~~~~~~~~~~~~~~~
def _sort_bell(recommendations):
    recommendations.sort(key = lambda row: row[1])
    a = recommendations[0::2]
    b = recommendations[1::2]
    b.reverse()
    bell = a + b
    return bell

def _wave_sort(recommendations):
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

def _remove_metric_tempo(recommendations):
    [i.pop(3) for i in recommendations]
    return recommendations

def _audio_features(recommendations, spotify):
    spuri = []
    tempos = []
    spuri = [i[2] for i in recommendations]
    results = spotify.audio_features(tracks=spuri)
    tempos = [i['tempo'] for i in results]
    [recommendations[i].append(tempos[i]) for i in range(len(tempos))]
    return recommendations
