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
import json
import pprint
import httplib2
import spotipy
import spotipy.oauth2 as spoauth
import requests
from flask import Flask, render_template, request, redirect, jsonify, session, url_for,current_app
from oauth2client.client import OAuth2WebServerFlow, flow_from_clientsecrets
from oauth2client.tools import run_flow

PROD_AUTH = 'http://tunesmash.herokuapp.com/auth'
APP_AUTH = 'http://app.tunesmash.org/auth'
DEV_AUTH = 'http://localhost:5000/auth'
SP_DEV_AUTH = 'http://localhost:5000/sp/auth'
SPOTIFY_INFO = {
    'id':'4f8c3338b0b443a8895358db33763c6f',
    'secret':'76cf6ff10bb041dbb0b11a3e7dd89fe1'
}

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
        return url_for('auth', provider=self.provider_name,_external=True)

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
        self.flow = OAuth2WebServerFlow(client_id=self.consumer_id,client_secret=self.consumer_secret,scope=['https://www.googleapis.com/auth/userinfo.profile','https://www.googleapis.com/auth/youtube'],redirect_uri=DEV_AUTH,prompt='consent')
        self.flow.params['access_type'] = 'offline'

    def authorize(self):
        return self.flow.step1_get_authorize_url()

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        code = request.args.get('code')
        credentials = self.flow.step2_exchange(code)
        return credentials


class SpotifySignIn(OAuthSignIn):
    def __init__(self):
        super(SpotifySignIn, self).__init__('spotify')
        self.oauth = spoauth.SpotifyOAuth(self.consumer_id,self.consumer_secret,SP_DEV_AUTH,scope='user-read-private playlist-modify-public user-read-email user-library-read playlist-modify-private user-top-read',cache_path='spotify.json')
        self.spotify = spotipy

    def authorize(self):
        print('ts auth spotify authorize')
        return self.oauth.get_authorize_url()

    def callback(self):
        print('ts auth spotify callback')
        if 'code' not in request.args:
            print('</3 BLEH </3>')
            return None, None, None
        code = request.args.get('code')
        print(request.args)
        body = self.oauth.get_access_token(code)
        access_token = body['access_token']
        refresh_token = body['refresh_token']
        expires_at = body['expires_at']
        sp = self.spotify.Spotify(auth=access_token)
        user = sp.current_user()

        results = {
            'name': user['display_name'],
            'email': user['email'],
            'spotify_user_id': user['id'],
            'access_token': access_token,
            'expires_at': expires_at,
            'refresh_token': refresh_token
        }

        self.results = results
        return "hello"

    def refresh(self,refresh_token):
        # r = requests.post('https://accounts.spotify.com/api/token',json.dumps({'grant_type':'refresh_token','refresh_token':refresh_token}),auth=(SPOTIFY_INFO['id'],SPOTIFY_INFO['secret']))
        token_info = self.oauth._refresh_access_token(refresh_token=refresh_token)
        return token_info
