from flask import Blueprint, request
from google.cloud import datastore
import json

from pytz import timezone
from werkzeug.urls import url_quote

import constants

client = datastore.Client()

url = "url/roles goes here"

bp = Blueprint('roles', __name__, url_prefix='/roles')

client_id = r'client id goes here'

def event_name(eid):
    event_key = client.key(constants.events, int(eid))
    event = client.get(key=event_key)
    return event["title"]


def get_slot_by_id(sid):
    slot_key = client.key(constants.timeslots, int(sid))
    slot = client.get(key=slot_key)
    return slot


def remove_slots(rid):
    role_key = client.key(constants.roles, int(rid))
    role = client.get(key=role_key)
    for s in role["timeslots"]:
        slot = get_slot_by_id(s)
        slot["role"] = None
        client.put(slot)


def remove_event(eid, rid):
    event_key = client.key(constants.events, int(eid))
    event = client.get(key=event_key)
    event["roles"].remove(int(rid))
    client.put(event)


def get_one_page_of_roles(cursor=None):
    query = client.query(kind=constants.roles)
    query_iter = query.fetch(start_cursor=cursor, limit=5)
    page = next(query_iter.pages)
    roles = list(page)
    next_cursor = query_iter.next_page_token
    return roles, next_cursor


# Convert dates into json compatible string
def timeconverter(o, format="%I:%M %p"):
    """Format a date time to (Default): HH:MM P"""
    if o is None:
        return ""
    pst = o.astimezone(timezone('US/Pacific'))

    return pst.strftime(format)


@bp.route('', methods=['GET', 'POST'])
def roles_get_post():
    if 'application/json' not in request.accept_mimetypes:
        return 'Error: Unaccepted Media Type', 406
    if request.method == 'POST':
        content = request.get_json()
        new_role = datastore.Entity(key=client.key(constants.roles))
        client.put(new_role)
        new_role.update({
            "title": content["title"],
            "event": None,
            "timeslots": [],
            "description": content["description"],
            "board_only": content["board_only"]
        })
        client.put(new_role)
        return str(new_role.key.id), 201

    elif request.method == 'GET':
        cursor = request.args.get('cursor')
        if cursor is not None:
            cursor = str(cursor)
        results, next_cursor = get_one_page_of_roles(cursor)
        for r in results:
            r["id"] = r.key.id
            r["self"] = url + "/" + str(r.key.id)
            if r["event"] is not None:
                r["event"] = event_name(r["event"])
        output = {"roles": results}
        if next_cursor is not None:
            output["next"] = url + "?cursor=" + url_quote(next_cursor)
        else:
            output["next"] = None
        return json.dumps(output), 200
    else:
        return 'Method not recognized', 405

# either returns an role or deletes a role
@bp.route('/<rid>', methods=['GET', 'DELETE', 'PUT'])
def role_get_post_delete(rid):
    if 'application/json' not in request.accept_mimetypes:
        return 'Error: Unaccepted Media Type', 406
    role_key = client.key(constants.roles, int(rid))
    role = client.get(key=role_key)
    if role is None:
        return ('Role not found', 404)
    if request.method == 'GET':
        role["id"] = role.key.id
        role["self"] = url + "/" + str(role.key.id)
        timeslots = []
        for s in role["timeslots"]:
            slot = get_slot_by_id(s)
            timeslots.append({"id": slot.key.id, "start": slot['start_time'], "end": slot['end_time'], "volunteer": slot['volunteer']})
        role["timeslots"] = timeslots
        return json.dumps(role, default=timeconverter), 200
    elif request.method == 'PUT':
        content = request.get_json()
        role.update({
            "title": content["title"],
            "description": content["description"],
            "board_only": content["board_only"]
        })
        client.put(role)
        return 'Role updated', 200
    elif request.method == 'DELETE':
        remove_slots(rid)
        remove_event(role["event"], rid)
        client.delete(role_key)
        return '', 204
    else:
        return 'Method not recognized', 405


@bp.route('/<rid>/timeslots/<sid>', methods=['DELETE', 'PUT'])
def role_timeslot_put_delete(rid, sid):
    if 'application/json' not in request.accept_mimetypes:
        return 'Error: Unaccepted Media Type', 406
    slot_key = client.key(constants.timeslots, int(sid))
    slot = client.get(key=slot_key)
    role_key = client.key(constants.roles, int(rid))
    role = client.get(key=role_key)
    if role is None:
        return ('Role not found', 404)
    if slot is None:
        return ('Timeslot not found', 404)
    if request.method == 'PUT':
        if slot["role"] is not None and slot["role"] != str(role.key.id):
            return 'Timeslot already assigned to another role', 400
        if slot.key.id not in role["timeslots"]:
            role["timeslots"].append(slot.key.id)
            client.put(role)
            slot["role"] = rid
            client.put(slot)
            return 'Timeslot assigned to role', 200
        else:
            return 'Timeslot already assigned to this event', 400
    elif request.method == 'DELETE':
        role["timeslots"].remove(slot.key.id)
        client.put(role)
        slot["role"] = None
        client.put(slot)
        return '', 204
    else:
        return 'Method not recognized', 405
