from google.auth.transport import requests
from google.oauth2 import id_token
from pytz import timezone
from flask import Blueprint, request
from google.cloud import datastore
import json

from werkzeug.urls import url_quote

import constants


client = datastore.Client()

url = "url/events goes here"

bp = Blueprint('events', __name__, url_prefix='/events')

client_id = r'client id goes here'


def get_slots(rid):
    query = client.query(kind=constants.timeslots)
    query.add_filter('role', '=', rid)
    timeslots = list(query.fetch())
    return timeslots

def get_role_by_id(rid):
    role_key = client.key(constants.roles, int(rid))
    role = client.get(key=role_key)
    return role

def remove_roles(eid):
    event_key = client.key(constants.events, int(eid))
    event = client.get(key=event_key)
    for r in event["roles"]:
        role = get_role_by_id(r)
        role["event"] = None
        client.put(role)

def get_one_page_of_events(cursor=None):
    query = client.query(kind=constants.events)
    query_iter = query.fetch(start_cursor=cursor, limit=5)
    page = next(query_iter.pages)
    events = list(page)
    next_cursor = query_iter.next_page_token
    return events, next_cursor

# Convert dates into json compatible string
def dateconverter(o, format="%a %b %d %Y %I:%M %p"):
    """Format a date time to (Default): HH:MM P"""
    if o is None:
        return ""
    pst = o.astimezone(timezone('US/Pacific'))

    return pst.strftime(format)

@bp.route('', methods=['GET', 'POST'])
def events_get_post():
    if 'application/json' not in request.accept_mimetypes:
        return 'Error: Unaccepted Media Type', 406
    if request.method == 'POST':
        # Make sure a registered user is creating the event
        if 'jwt' not in request.headers:
            return 'No Token Provided', 401
        req = requests.Request()
        try:
            id_info = id_token.verify_oauth2_token(
                request.headers['jwt'], req, client_id)
        except ValueError:
            # Invalid token
            return 'Invalid Token', 401
        query = client.query(kind=constants.volunteers)
        query.add_filter("email", "=", id_info['email'])
        results = list(query.fetch())
        if len(results) == 0:
            # user doesn't exist in database
            return '', 403
        content = request.get_json()
        new_event = datastore.Entity(key=client.key(constants.events))
        client.put(new_event)
        new_event.update({
            "title": content["title"],
            "event_date": content["event_date"],
            "start_time": content["start_time"],
            "end_time": content["end_time"],
            "location_address": content["location_address"],
            "location_name": content["location_name"],
            "admin": id_info["email"],
            "description": content["description"],
            "roles": []
        })
        client.put(new_event)
        return str(new_event.key.id), 201

    elif request.method == 'GET':
        cursor = request.args.get('cursor')
        if cursor is not None:
            cursor = str(cursor)
        results, next_cursor = get_one_page_of_events(cursor)
        for e in results:
            e["self"] = url + "/" + str(e.key.id)
            e["id"] = e.key.id
        output = {"events": results}
        if next_cursor is not None:
            output["next"] =  url + "?cursor=" + url_quote(next_cursor)
        else:
            output["next"] = None
        return json.dumps(output, default=dateconverter), 200
    else:
        return 'Method not recognized', 405

# either returns an event or deletes an event
@bp.route('/<eid>', methods=['GET', 'DELETE', 'PUT'])
def event_get_post_delete(eid):
    if 'application/json' not in request.accept_mimetypes:
        return 'Error: Unaccepted Media Type', 406
    event_key = client.key(constants.events, int(eid))
    event = client.get(key=event_key)
    if event is None:
        return ('Event not found', 404)
    if request.method == 'GET':
        event["id"] = event.key.id
        event["self"] = url + "/" + str(event.key.id)
        roles = []
        for r in event["roles"]:
            slots = []
            timeslots = get_slots(str(r))
            for t in timeslots:
                if t['volunteer'] is not None:
                    name_key = client.key(constants.volunteers, int(t['volunteer']))
                    name = client.get(key=name_key)
                    volunteer_name = name['email']
                else:
                    volunteer_name = ''
                slots.append({"start": t['start_time'], "end": t['end_time'], "volunteer": volunteer_name})
            role = get_role_by_id(str(r))
            role["timeslots"]= slots
            roles.append(role)
        event["roles"] = roles
        return json.dumps(event, default=dateconverter), 200
    elif request.method == 'PUT':
        if 'jwt' not in request.headers:
            return 'No Token Provided', 401
        req = requests.Request()
        try:
            id_info = id_token.verify_oauth2_token(
                request.headers['jwt'], req, client_id)
        except ValueError:
            # Invalid token
            return 'Invalid Token', 401
        if event['admin'] != id_info['email']:
            return '', 403
        content = request.get_json()
        event.update({
            "title": content["title"],
            "event_date": content["event_date"],
            "start_time": content["start_time"],
            "end_time": content["end_time"],
            "location_address": content["location_address"],
            "location_name": content["location_name"],
            "description": content["description"]
        })
        client.put(event)
        return 'Event Updated', 200
    elif request.method == 'DELETE':
        if 'jwt' not in request.headers:
            return 'No Token Provided', 401
        req = requests.Request()
        try:
            id_info = id_token.verify_oauth2_token(
                request.headers['jwt'], req, client_id)
        except ValueError:
            # Invalid token
            return 'Invalid Token', 401
        if event['admin'] != id_info['email']:
            return '', 403
        remove_roles(eid)
        client.delete(event_key)
        return '', 204
    else:
        return 'Method not recognized', 405

# add or remove a role from an event
@bp.route('/<eid>/roles/<rid>', methods=['DELETE', 'PUT'])
def event_role_put_delete(eid, rid):
    if 'application/json' not in request.accept_mimetypes:
        return 'Error: Unaccepted Media Type', 406
    role_key = client.key(constants.roles, int(rid))
    role = client.get(key=role_key)
    event_key = client.key(constants.events, int(eid))
    event = client.get(key=event_key)
    if 'jwt' not in request.headers:
        return 'No Token Provided', 401
    req = requests.Request()
    try:
        id_info = id_token.verify_oauth2_token(
            request.headers['jwt'], req, client_id)
    except ValueError:
        # Invalid token
        return 'Invalid Token', 401
    if event['admin'] != id_info['email']:
        return '', 403
    if role is None:
        return ('Role not found', 404)
    if event is None:
        return ('Event not found', 404)
    if request.method == 'PUT':
        if role["event"] is not None and role["event"] != event.key.id:
            return 'Role already assigned to another event', 400
        if role.key.id not in event["roles"]:
            event["roles"].append(role.key.id)
            client.put(event)
            role["event"] = eid
            client.put(role)
            return '', 200
        else:
            return 'Role already assigned to this event', 400
    elif request.method == 'DELETE':
        if role["event"] == str(event.key.id):
            event["roles"].remove(role.key.id)
            client.put(event)
            role["event"] = None
            client.put(role)
            return '', 204
        else:
            return 'Role not assigned to this event', 400
    else:
        return 'Method not recognized', 405
