from datetime import datetime, timedelta

from flask import Blueprint, request
from google.auth.transport import requests
from google.cloud import datastore
import json

from google.oauth2 import id_token
from pytz import timezone
from werkzeug.urls import url_quote
import constants

client = datastore.Client()

url = "url/timeslots goes here"

bp = Blueprint('timeslots', __name__, url_prefix='/timeslots')

client_id = r'client id goes here'


def role_name(rid):
    role_key = client.key(constants.roles, int(rid))
    role = client.get(key=role_key)
    return role["title"]

def remove_slot(rid, sid):
    role_key = client.key(constants.roles, int(rid))
    role = client.get(key=role_key)
    role["timeslots"].remove(int(sid))
    client.put(role)

def get_one_page_of_slots(cursor=None):
    query = client.query(kind=constants.timeslots)
    query_iter = query.fetch(start_cursor=cursor, limit=5)
    page = next(query_iter.pages)
    slots = list(page)
    next_cursor = query_iter.next_page_token
    return slots, next_cursor


def remove_volunteer(vid, hours):
    v_key = client.key(constants.volunteers, int(vid))
    v = client.get(key=v_key)
    newhours = v["hours"] - hours
    v.update({"hours": newhours})
    client.put(v)


# Convert dates into json compatible string
def timeconverter(o, format="%I:%M %p"):
    """Format a date time to (Default): HH:MM P"""
    if o is None:
        return ""
    pst = o.astimezone(timezone('US/Pacific'))
    return pst.strftime(format)


@bp.route('', methods=['GET', 'POST'])
def slots_get_post():
    if 'application/json' not in request.accept_mimetypes:
        return 'Error: Unaccepted Media Type', 406
    if request.method == 'POST':
        content = request.get_json()
        new_slot = datastore.Entity(key=client.key(constants.timeslots))
        client.put(new_slot)
        fmt = '%H:%M'
        tdelta = datetime.strptime(content["end_time"], fmt) - datetime.strptime(content["start_time"], fmt)
        new_slot.update({
            "role": None,
            "start_time": content["start_time"],
            "end_time": content["end_time"],
            "length": tdelta.seconds/3600,
            "volunteer": None
        })
        client.put(new_slot)
        return str(new_slot.key.id), 201

    elif request.method == 'GET':
        cursor = request.args.get('cursor')
        if cursor is not None:
            cursor = str(cursor)
        results, next_cursor = get_one_page_of_slots(cursor)
        for s in results:
            s["id"] = s.key.id
            s["self"] = url + "/" + str(s.key.id)
            if s["role"] is not None:
                s["role"] = role_name(s["role"])
        output = {"timeslots": results}
        if next_cursor is not None:
            output["next"] = url + "?cursor=" + url_quote(next_cursor)
        else:
            output["next"] = None
        return json.dumps(output), 200
    else:
        return 'Method not recognized', 405

# either returns an role or deletes a role
@bp.route('/<sid>', methods=['GET', 'DELETE', 'PUT'])
def slot_get_post_delete(sid):
    if 'application/json' not in request.accept_mimetypes:
        return 'Error: Unaccepted Media Type', 406
    slot_key = client.key(constants.timeslots, int(sid))
    slot = client.get(key=slot_key)
    if slot is None:
        return ('Timeslot not found', 404)
    if request.method == 'GET':
        slot["id"] = slot.key.id
        if slot["role"] is not None:
            slot["role"] = role_name(slot["role"])
        return json.dumps(slot, default=timeconverter)
    elif request.method == 'PUT':
        content = request.get_json()
        fmt = '%H:%M'
        tdelta = datetime.strptime(content["end_time"], fmt) - datetime.strptime(content["start_time"], fmt)
        slot.update({
            "start_time": content["start_time"],
            "end_time": content["end_time"],
            "length": tdelta.seconds / 3600
        })
        client.put(slot)
        return 'Slot Updated', 200
    elif request.method == 'DELETE':
        if slot["volunteer"] is not None:
            remove_volunteer(slot["volunteer"], slot["length"])
        if slot["role"] is not None:
            remove_slot(slot["role"], sid)
        client.delete(slot_key)
        return '', 204
    else:
        return 'Method not recognized', 405

@bp.route('/<sid>/volunteers/<vid>', methods=['PUT', 'DELETE'])
def slot_volunteer_put_delete(sid, vid):
    if 'application/json' not in request.accept_mimetypes:
        return 'Error: Unaccepted Media Type', 406
    slot_key = client.key(constants.timeslots, int(sid))
    slot = client.get(key=slot_key)
    if slot is None:
        return 'Timeslot not found', 404
    volunteer_key = client.key(constants.volunteers, int(vid))
    volunteer = client.get(key=volunteer_key)
    if volunteer is None:
        return 'Volunteer not found', 404
    if request.method == 'PUT':
        if slot["volunteer"] is not None:
            return 'Timeslot Taken', 400
        if 'jwt' not in request.headers:
            return 'No Token Provided', 401
        req = requests.Request()
        try:
            id_info = id_token.verify_oauth2_token(
                request.headers['jwt'], req, client_id)
        except ValueError:
            # Invalid token
            return 'Invalid Token', 401
        user_key = client.key(constants.volunteers, int(vid))
        user = client.get(key=user_key)
        if user is None or user['email'] != id_info['email']:
            return '', 403
        slot.update({
            'volunteer': vid
        })
        hours = volunteer["hours"] + slot["length"]
        volunteer.update({
            'hours': hours
        })
        client.put(slot)
        client.put(volunteer)
        return 'Volunteer Added', 200
    elif request.method == 'DELETE':
        if slot["volunteer"] != vid:
            return ('Volunteer Not Signed up for Slot', 400)
        slot.update({
            'volunteer': None
        })
        hours = volunteer["hours"] - slot["length"]
        volunteer.update({
            'hours': hours
        })
        client.put(slot)
        client.put(volunteer)
        return '', 204
    else:
        return 'Method not recognized', 405
