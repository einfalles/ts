# -*- coding: utf-8 -*-
"""

ts_auth.py
~~~~~~~~~~~

description
~~~~~~~~~~~
This file creates the flow to get Google stuff.

metadata
~~~~~~~~
author: dn@rad.kitchen
date of creation: July 4, 2016
date of last edit:

Copyright (c) Rad Kitchen Inc. All rights reserved.

"""


import httplib2
import os
import sys
import csv
from flask import Flask, render_template, request, redirect, jsonify, session, url_for,current_app
from oauth2client.contrib.flask_util import UserOAuth2
from oauth2client.client import OAuth2WebServerFlow
from oauth2client import client
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

CLIENT_SECRETS_FILE = "client_secrets.json"
MISSING_CLIENT_SECRETS_MESSAGE = "Oh, no. Try looking at %s" % os.path.abspath(os.path.join(os.path.dirname(__file__), CLIENT_SECRETS_FILE))
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"



class OAuthSignIn(object):
    providers = None
    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('auth', provider=self.provider_name,
                       _external=True)
    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers={}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]

class GoogleSignIn(OAuthSignIn):
    def __init__(self):
        super(GoogleSignIn, self).__init__('google')
        self.flow = OAuth2WebServerFlow(client_id=self.consumer_id,client_secret=self.consumer_secret,scope='https://www.googleapis.com/auth/youtube',redirect_uri='http://localhost:5000/auth')

    def authorize(self):
        return self.flow.step1_get_authorize_url()

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        code = request.args.get('code')
        credentials = self.flow.step2_exchange(code)
        session['credentials'] = credentials.to_json()
        return session['credentials']

# Authorize the request and store authorization credentials.
def get_authenticated_service(user):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READONLY_SCOPE,message=MISSING_CLIENT_SECRETS_MESSAGE)
    storage = Storage("%s-oauth2.json" % user)
    credentials = storage.get()
    if credentials is None or credentials.invalid:
      credentials = run_flow(flow, storage,args)
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))
    return youtube

def get_watch_history(youtube):
    retrieved_history = []
    channels_response = youtube.channels().list(mine=True,part="contentDetails").execute()
    for channel in channels_response["items"]:
        uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["watchHistory"]
    playlistitems_list_request = youtube.playlistItems().list(playlistId=uploads_list_id,part="snippet",maxResults=50)
    count = 0
    while count < 2:
        playlistitems_list_response = playlistitems_list_request.execute()
        for playlist_item in playlistitems_list_response["items"]:
          video_id = playlist_item["snippet"]["resourceId"]["videoId"]
          video_req = youtube.videos().list(part="snippet",id=video_id)
          video_res = video_req.execute()
          for video_item in video_res["items"]:
              video_cat_id = video_item["snippet"]["categoryId"]
              if video_cat_id == '10':
                  video_title = video_item["snippet"]["title"]
                  history_temp = str(video_title.encode('utf8')).rsplit('-',1)
                  if len(history_temp) > 1:
                      retrieved_history.append(str(video_title).rsplit('-',1))
                  else:
                      print history_temp
        playlistitems_list_request = youtube.playlistItems().list_next(playlistitems_list_request, playlistitems_list_response)
        count = count + 1
    return retrieved_history
