from flask import Blueprint, request
from google.auth.transport import requests
from google.cloud import datastore
import json

from google.oauth2 import id_token
from werkzeug.urls import url_quote

import constants

client = datastore.Client()

url = "url/volunteers goes here"

bp = Blueprint('volunteers', __name__, url_prefix='/volunteers')

client_id = r'client id goes here'

def get_one_page_of_volunteers(cursor=None):
    query = client.query(kind=constants.volunteers)
    query_iter = query.fetch(start_cursor=cursor, limit=5)
    page = next(query_iter.pages)
    volunteers = list(page)
    next_cursor = query_iter.next_page_token
    return volunteers, next_cursor

def remove_slots(vid):
    query = client.query(kind=constants.timeslots)
    query.add_filter('volunteer', '=', vid)
    slots = list(query.fetch())
    print(slots)
    for s in slots:
        slot = client.get(key=s.key)
        slot["volunteer"] = None
        client.put(slot)

def get_slots(vid):
    query = client.query(kind=constants.timeslots)
    query.add_filter('volunteer', '=', vid)
    slots = list(query.fetch())
    return slots

@bp.route('', methods=['GET'])
def volunteers_get_post():
    if 'application/json' not in request.accept_mimetypes:
        return 'Error: Unaccepted Media Type', 406
    if request.method == 'GET':
        cursor = request.args.get('cursor')
        if cursor is not None:
            cursor = str(cursor)
        results, next_cursor = get_one_page_of_volunteers(cursor)
        for v in results:
            v["id"] = v.key.id
            v["self"] = url + "/" + str(v.key.id)
        output = {"Volunteers": results}
        if next_cursor is not None:
            output["next"] = url + "?cursor=" + url_quote(next_cursor)
        else:
            output["next"] = None
        return json.dumps(output), 200
    else:
        return 'Method not recognized', 405

@bp.route('/<vid>', methods=['GET', 'PUT', 'DELETE'])
def volunteer_get_delete(vid):
    if 'application/json' not in request.accept_mimetypes:
        return 'Error: Unaccepted Media Type', 406
    vol_key = client.key(constants.volunteers, int(vid))
    vol = client.get(key=vol_key)
    if vol is None:
        return ('Volunteer not found', 404)
    if 'jwt' not in request.headers:
        return 'No Token Provided', 401
    req = requests.Request()
    try:
        id_info = id_token.verify_oauth2_token(
            request.headers['jwt'], req, client_id)
    except ValueError:
        # Invalid token
        return 'Invalid Token', 401
    if vol['email'] != id_info['email']:
        return '', 403
    if request.method == 'GET':
        timeslots = []
        slots = get_slots(vid)
        for s in slots:
            timeslots.append(url[:-10] + "timeslots/" + str(s.key.id))
        vol["timeslots"] = timeslots
        return json.dumps(vol), 200
    elif request.method == 'PUT':
        content = request.get_json()
        vol.update({
            "first_name": content["first_name"],
            "last_name": content["last_name"],
            "board_member": content["board_member"]
        })
        client.put(vol)
        return 'Volunteer Updated', 200
    elif request.method == 'DELETE':
        remove_slots(vid)
        client.delete(vol_key)
        return '', 204
    else:
        return 'Method not recognized', 405
