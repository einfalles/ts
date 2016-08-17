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
from flask import Flask, render_template, request, redirect, jsonify, session, url_for,current_app
from oauth2client.client import OAuth2WebServerFlow, flow_from_clientsecrets
from oauth2client.tools import run_flow

CLIENT_SECRETS_FILE = "client_secrets.json"
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
PROD_AUTH = 'http://tunesmash.herokuapp.com/auth'
DEV_AUTH = 'http://localhost:5000/auth'
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
        self.flow = OAuth2WebServerFlow(client_id=self.consumer_id,client_secret=self.consumer_secret,scope=['https://www.googleapis.com/auth/userinfo.profile','https://www.googleapis.com/auth/youtube'],redirect_uri=PROD_AUTH,prompt='consent')      
        self.flow.params['access_type'] = 'offline'

    def authorize(self):
        return self.flow.step1_get_authorize_url()

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        code = request.args.get('code')
        credentials = self.flow.step2_exchange(code)
        return credentials


def get_authenticated_service(email):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SCOPE,message=MISSING_CLIENT_SECRETS_MESSAGE)
    flow.params['access_type'] = 'offline'
    store = oams.get_credential_storage(filename='multi.json',client_id=email,user_agent='app',scope=['https://www.googleapis.com/auth/youtube','https://www.googleapis.com/auth/userinfo.profile'])
    credentials = store.get()
    if credentials is None or credentials.invalid == True:
        credentials = run_flow(flow, store)
    store.put(credentials)
    return credentials
