import spotipy
import spotipy.oauth2 as oauth
import csv
import time
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
import httplib2
import sys
from oauth2client.contrib import multistore_file as oams

SP_TOKEN = oauth.SpotifyClientCredentials(client_id='4f8c3338b0b443a8895358db33763c6f',client_secret='76cf6ff10bb041dbb0b11a3e7dd89fe1')
SP = spotipy.Spotify(auth=SP_TOKEN.get_access_token())
GLOBAL_REC_ID = []

CLIENT_SECRETS_FILE = "client_secrets.json"
MISSING_CLIENT_SECRETS_MESSAGE ="NO NO NO NO"
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
# youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))

class Recommender():
    def __init__(self,credentials):
        self.youtube = build(YOUTUBE_API_SERVICE_NAME,YOUTUBE_API_VERSION,http=credentials)

    def get_watch_history(self):
        count = 0
        watch_history = []
        channels_response = self.youtube.channels().list(mine=True,part="contentDetails").execute()
        for channel in channels_response["items"]:
            uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["watchHistory"]

        playlistitems_list_request = self.youtube.playlistItems().list(playlistId=uploads_list_id,part="snippet",maxResults=50)

        while len(watch_history) < 5:
            playlistitems_list_response = playlistitems_list_request.execute()
            for playlist_item in playlistitems_list_response["items"]:
                video_id = playlist_item["snippet"]["resourceId"]["videoId"]
                video_req = self.youtube.videos().list(part="snippet",id=video_id)
                video_res = video_req.execute()
                for video_item in video_res["items"]:
                    video_cat_id = video_item["snippet"]["categoryId"]
                    if video_cat_id == '10':
                        video_title = video_item["snippet"]["title"]
                        history_temp = video_title.encode('utf8').rsplit('-',1)
                        if len(history_temp) > 1:
                            watch_history.append(history_temp)
                        else:
                            print(history_temp)
            playlistitems_list_request = self.youtube.playlistItems().list_next(playlistitems_list_request, playlistitems_list_response)
            count = count + 1
        return watch_history


def csv_to_array(user):
    filename = str(user)+'_history.csv'
    with open(filename, 'rU') as f:
        reader = csv.reader(f)
        your_list= list(reader)
    return your_list

def generate_recommendations(seed_one, seed_two,limit):
    recommendations = []
    seeds = [seed_one[1][2],seed_two[1][2]]
    print("********** generating recommendations *********")
    unireq = {}
    results = SP.recommendations(seed_tracks=seeds,max_popularity=limit,limit=60)
    results = results['tracks']
    while len(recommendations)<20:
        for song in results:
            artist = song['artists'][0]['name'].encode('utf-8')
            album = song['album']['name'].encode('utf-8')
            title = song['name'].encode('utf-8')
            track = artist + " " + album + " " + title
            print(song)
            if unireq.has_key(artist):
                pass
            else:
                unireq[artist] = 'artist'
                recommendations.append(track)
                GLOBAL_REC_ID.append(song['id'].encode('utf-8'))
    if len(recommendations)>20:
        recommendations = recommendations[0:20]
    return recommendations

def bell_sort(recommendations):
    print("********** sorting recommendations: bell curve *********")
    recommendations.sort(key = lambda row: row[1])
    a = recommendations[0::2]
    b = recommendations[1::2]
    b.reverse()
    bell = a + b
    for i in bell:
        print(i)
    return bell

def wave_sort(recommendations):
    print("********** sorting recommendations: wave *********")
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
    print("********** removing extra data **********")
    ar = []
    for i in recommendations:
        ar.append(i[0])
    return ar

def clean_temp(results):
    recommendations = []
    for song in results:
        artist = song['artists'][0]['name'].encode('utf-8')
        album = song['album']['name'].encode('utf-8')
        title = song['name'].encode('utf-8')
        track = artist + " " + album + " " + title
        recommendations.append(track)
    return recommendations

def generate_yt_playlist(yt,recommendations,uone,utwo):
    playlist = yt.playlists().insert(
        part="snippet,status",
        body=dict(
            snippet=dict(
              title=str(time.time())+" * " + uone  + " and " + utwo,
              description="Tunesmash"
            ),
            status=dict(
              privacyStatus="public"
            )
        )
    ).execute()

    return playlist["id"]
    print("You now have a playlist you'll love.")

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
def add_audio_features(recommendations):
    print("********** adding audio features *********")
    af = []
    sr = []
    results = SP.audio_features(tracks=GLOBAL_REC_ID)
    for i in results:
        af.append(i['tempo'])
    for i,song in enumerate(recommendations):
        sr.append([recommendations[i],af[i]])
    for i in sr:
        print(i)
    return sr

def populate_playlist(yt, recommendations, playlist_id):
    videos = []
    for song in recommendations:
        try:
            yt_request = yt.search().list(part="snippet",q=song,type="video")
            results = yt_request.execute()
            if len(results['items'])>0:
                videos.append(results['items'][0]['id']['videoId'].encode('utf-8'))
            else:
                print("someshit")
            # yt_request = yt.search().list_next(yt_request, results)
        except HttpError(e):
            print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
            pass
    for video in videos:
        add_video_to_playlist(yt,video,playlist_id)

def get_authenticated_service(user):
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    store = oams.get_credential_storage(filename='multi.json',client_id=user,user_agent='app',scope=['https://www.googleapis.com/auth/youtube','https://www.googleapis.com/auth/userinfo.profile'])
    creds = store.get()
    if creds is None or creds.invalid:
        return "tits"
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=creds.authorize(httplib2.Http()))
    return youtube

def run_generation(uone_email=None, utwo_email=None,popularity_limit=60):
    uone_history = csv_to_array(uone_email)
    utwo_history = csv_to_array(utwo_email)
    tunesmash = generate_recommendations(uone_history,utwo_history,popularity_limit)
    tunesmash = add_audio_features(tunesmash)
    tunesmash = bell_sort(tunesmash)
    tunesmash = remove_ids(tunesmash)
    youtube = get_authenticated_service(uone_email)
    playlist_id = generate_yt_playlist(yt=youtube,recommendations=tunesmash,uone=uone_email,utwo=utwo_email)
    populate_playlist(youtube,tunesmash,playlist_id)
    return playlist_id
