#!/usr/bin/env python

# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import google.auth.transport.requests
from google.cloud import datastore
from flask import Flask, redirect, request
from google.oauth2 import id_token
from pytz import timezone
from requests_oauthlib import OAuth2Session
import requests
import constants
import events
import roles
import slots
import volunteers

# This disables the requirement to use HTTPS so that you can test locally.
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.register_blueprint(events.bp)
app.register_blueprint(roles.bp)
app.register_blueprint(slots.bp)
app.register_blueprint(volunteers.bp)
client = datastore.Client()

# These should be copied from an OAuth2 Credential section at
# https://console.cloud.google.com/apis/credentials
client_id = r'client ID here'
client_secret = r'client Secret Here'

url = 'url here'

# This is the page that you will use to decode and collect the info from
# the Google authentication flow
redirect_uri = url + '/oauth'

# These let us get basic info to identify a user and not much else
# they are part of the Google People API
scope = ['https://www.googleapis.com/auth/userinfo.email',
         'https://www.googleapis.com/auth/userinfo.profile']
oauth = OAuth2Session(client_id, redirect_uri=redirect_uri,
                      scope=scope)

# does nothing currently
@app.route('/')
def index():
    authorization_url, state = oauth.authorization_url(
        'https://accounts.google.com/o/oauth2/auth',
        # access_type and prompt are Google specific extra
        # parameters.
        access_type="offline", prompt="select_account")
    return redirect(authorization_url)

# This is where users will be redirected back to and where you can collect
# the JWT for use in future requests
@app.route('/oauth')
def oauthroute():
    token = oauth.fetch_token(
        'https://accounts.google.com/o/oauth2/token',
        authorization_response=request.url,
        client_secret=client_secret)
    req = google.auth.transport.requests.Request()

    id_info = id_token.verify_oauth2_token(
        token['id_token'], req, client_id)
    headers = {'Authorization': 'Bearer ' + token["access_token"]}
    r = requests.get('https://content-people.googleapis.com/v1/people/me?personFields=names', headers=headers)
    person = r.json()
    query = client.query(kind=constants.volunteers)
    query.add_filter("email", "=", id_info['email'])
    results = list(query.fetch())
    if len(results) == 0:
        new_user = datastore.Entity(key=client.key(constants.volunteers))
        client.put(new_user)
        new_user.update({
            "first_name": person['names'][0]['givenName'].split(' ')[0],
            "last_name": person['names'][0]['familyName'],
            "email": id_info["email"],
            "board_member": False,
            "hours": 0
        })
        client.put(new_user)

    return "Your JWT is: %s" % token['id_token'], 201

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [START gae_python37_render_template]
