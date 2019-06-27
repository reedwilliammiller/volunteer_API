# Final Project Volunteer Sign-up API Documentation

To deploy, set up a Google Cloud Account and new project using the source code.  
Create OAuth2 credentials and insert the new client id and secret into the source code variables.
Deploy locally or on google cloud.

## Description
This project will serve as the backend for a Volunteer sign-up database that I am building for my local community club.  It stores users as Volunteer entities which can be signed up for Timeslot entities, which can be attached to a Role Entity which can be attached to an Event Entity.  
Only signed in Volunteers can create events, and only the admin of an event can edit or delete an event.
Only a signed in Volunteer can edit or delete their own volunteer profile.
The idea is that events can be created and volunteer roles can be created and assigned to an event.  For each role, timeslots can be created and assigned to the role, so a user will be able to see open timeslots for each role and sign up for the timeslot for a specific role for a specific event.  The volunteer’s total volunteer hours are increased or decreased if they sign up for or remove a timeslot.  


## URLs

### Only JSON Types Accepted
If accept/json is not in the header, any call will return:  
“Error: Unaccepted Media Type” with code 406

### Disallowed Methods
If you attempt any unsupported method call, it will return status 405

### Create an Event
POST  /events  

Requires the user to provide a valid JWT.  

If no JWT is provided, returns 'No Token Provided’, with code 401  

If an invalid JWT is provided, returns 'Invalid Token', with code 401  

Receives a JSON body as follows:
```javascript
{
    "title": “event title”,
    "event_date": “Datetime of event",
    "start_time": "Datetime of start of event",
    "end_time": "Datetime of end of event",
    "location_address": “address of event ",
    "location_name": “name of event location",
    "description": “description of event"
}
```
If Successful, returns the ID of the newly created event and status 201

Example:
POST /events
With body:
```javascript
{
    "title": "Candidate Forum",
    "event_date": "2019-08-03 (18:00:00.000) PDT",
    "start_time": "2019-08-03 (18:00:00.000) PDT",
    "end_time": "2019-08-03 (21:00:00.000) PDT",
    "location_address": "2811 Mount Rainier Drive South, Seattle, WA, 98144 ",
    "location_name": "Mount Baker Community Club",
    "description": "A night of discussion with the district 2 and district 3 city council candidates"
}
```
returns:
554234543534

Creates a new event with the admin as the user in the provided JWT


### View all Events
GET  /events  
Returns a JSON containing 5 of the events and a link to the next 5 events and a status of 200

Example:  
GET /events  

returns:
```javascript
  {
    "events": [
        {
            "event_date": "2019-10-24 (14:00:00.000) PDT",
            "location_name": "Mount Baker Park",
            "roles": [],
            "end_time": "2019-10-24 (18:00:00.000) PDT",
            "location_address": "2521 Lake Park Dr S, Seattle, WA 98144",
            "title": "Test Event 3",
            "start_time": "2019-10-24 (14:00:00.000) PDT",
            "description": "Test Event #3",
            "admin": "user@gmail.com",
            "self": "https://your_url.appspot.com/events/5147289865682944",
            "id": 5147289865682944
        },
        {
            "location_name": "Mount Baker Park",
            "roles": [],
            "end_time": "2019-09-14 (18:00:00.000) PDT",
            "title": "Day in the Park",
            "location_address": "2521 Lake Park Dr S, Seattle, WA 98144",
            "start_time": "2019-09-14 (14:00:00.000) PDT",
            "description": "A day of playing in the park with music, bouncy houses, and other games",
            "admin": "user@gmail.com",
            "event_date": "2019-09-14 (14:00:00.000) PDT",
            "self": "https://your_url.appspot.com/events/5633226290757632",
            "id": 5633226290757632
        },
        {
            "event_date": "2019-11-24 (14:00:00.000) PDT",
            "location_name": "Mount Baker Park",
            "end_time": "2019-11-24 (18:00:00.000) PDT",
            "roles": [],
            "title": "Test Event 4",
            "location_address": "2521 Lake Park Dr S, Seattle, WA 98144",
            "start_time": "2019-11-24 (14:00:00.000) PDT",
            "description": "Test Event #4",
            "admin": "user@gmail.com",
            "self": "https://your_url.appspot.com/events/5638186843766784",
            "id": 5638186843766784
        },
        {
            "end_time": "2019-10-14 (18:00:00.000) PDT",
            "roles": [],
            "title": "Test Event 2",
            "location_address": "2521 Lake Park Dr S, Seattle, WA 98144",
            "start_time": "2019-10-14 (14:00:00.000) PDT",
            "description": "Test Event #2",
            "admin": "user@gmail.com",
            "event_date": "2019-10-14 (14:00:00.000) PDT",
            "location_name": "Mount Baker Park",
            "self": "https://your_url.appspot.com/events/5641497726681088",
            "id": 5641497726681088
        },
        {
            "event_date": "08/03/19",
            "location_name": "Mount Baker Community Club",
            "end_time": "08/03/19 9:00 PM",
            "roles": [],
            "title": "Candidate Forum",
            "location_address": "2811 Mount Rainier Drive South, Seattle, WA, 98144 ",
            "start_time": "08/03/19 6:00 PM",
            "description": "A night of discussion with the district 2 and district 3 city council candidates",
            "admin": "user@gmail.com",
            "self": "https://your_url.appspot.com/events/5643172898144256",
            "id": 5643172898144256
        }
    ],
    "next": "https://your_url.appspot.com/events?cursor=CjESK2oUbX5taWxscmVlZC00OTMtZmluYWxyEwsSBkV2ZW50cxiAgICg-Y2DCgwYACAA"
  }
```
### View a single Event
GET /events/:id  
Returns a JSON containing the information of the requested event and status 200  
Or if the event doesn’t exist, returns “Event Not Found” with code 404  

Example:  
GET /events/5147289865682944  

Returns:
```javascript
{
    "end_time": "2019-10-24 (18:00:00.000) PDT",
    "roles": [
        {
            "board_only": true,
            "event": "5147289865682944",
            "description": "Serve as an ambassador for the community club",
            "timeslots": [
                {
                    "start": "15:00",
                    "end": "18:00",
                    "volunteer": "user@gmail.com"
                }
            ],
            "title": "Ambassador"
        }
    ],
    "title": "Test Event 3",
    "location_address": "2521 Lake Park Dr S, Seattle, WA 98144",
    "start_time": "2019-10-24 (14:00:00.000) PDT",
    "description": "Test Event #3",
    "admin": "user@gmail.com",
    "event_date": "2019-10-24 (14:00:00.000) PDT",
    "location_name": "Mount Baker Park",
    "id": 5147289865682944,
    "self": "https://your_url.appspot.com/events/5147289865682944"
}
```
### Modify an Event
PUT /events/:id  
Receives a JSON as follows:  
```javascript
{
    "title": “event title”,
    "event_date": “Datetime of event",
    "start_time": "Datetime of start of event",
    "end_time": "Datetime of end of event",
    "location_address": “address of event ",
    "location_name": “name of event location",
    "description": “description of event"
}
```
If Successful, Returns ‘Event Updated’ with status 200  

Or if the event doesn’t exist, it will return ‘Event not Found’ with status 404  

Example:  
PUT /events/1234  
body:
```javascript
{
    "title": "New Event Modified",
    "event_date": "2019-08-03 (18:00:00.000) PDT",
    "start_time": "2019-08-03 (18:00:00.000) PDT",
    "end_time": "2019-08-03 (21:00:00.000) PDT",
    "location_address": "2811 Mount Rainier Drive South, Seattle, WA, 98144 ",
    "location_name": "Mount Baker Community Club",
    "description": "This event was modified"
}
```

Returns ‘Event Updated’ with status 200  


### Delete an Event
DELETE /events/:id  

Deletes the event and returns status 204  
Or if the event doesn’t exist, it will return ‘Event not Found’ with status 404  

Example:  
DELETE /events/1234  

Returns status 204  


### Assign a Role to an Event
PUT /events/:eid/roles/:rid  

Assigns a role to an event and returns status 200  
Also assigns the event to the role’s “event” field  
Or if the event doesn’t exist, it will return ‘Event not Found’ with status 404  
Or if the role doesn’t exist, it will return ‘Role not Found’ with status 404  

Requires the user to be the admin of the event and to provide a valid JWT.  

If no JWT is provided, returns 'No Token Provided’, with code 401  

If an invalid JWT is provided, returns 'Invalid Token', with code 401  

If a valid JWT is provided, but the user is not the admin of the event, returns 403  

If the role is already assigned to another event, returns ‘Role already assigned to another event’ with status 400  

If the role is already assigned to the called event, returns 'Role already assigned to this event'
with status 400  

Example:  
PUT /events/1234/roles/5678  

Returns 200  

### Removes a Role from an Event
DELETE /events/:eid/roles/:rid  

Removes a role from an event and returns status 204  
Also removes the event from the role’s “event” field  
Or if the event doesn’t exist, it will return ‘Event not Found’ with status 404  
Or if the role doesn’t exist, it will return ‘Role not Found’ with status 404  

Requires the user to be the admin of the event and to provide a valid JWT.  

If no JWT is provided, returns 'No Token Provided’, with code 401  

If an invalid JWT is provided, returns 'Invalid Token', with code 401  

If a valid JWT is provided, but the user is not the admin of the event, returns 403  

If the role is not assigned to the called event, returns 'Role not assigned to this event'
with status 400  

Example:  
DELET /events/1234/roles/5678  

Returns 204  

### Create a Role
POST  /roles  

Receives a JSON body as follows:  
```javascript
{
    "title": “role title",
    "description": “role description",
    "board_only": boolean
}
```
If Successful, returns the ID of the newly created role and status 201  

Example:  
POST /roles  
With body:  
```javascript
{
    "title": "tear-down",
    "description": "tear-down the tables and chairs",
    "board_only": false
}
```
returns:  
1234314  

Creates a new role  


### View all Roles
GET  /roles  
Returns a JSON containing 5 of the roles and a link to the next 5 roles and a status of 200  

Example:  
GET /roles  

returns:
```javascript
{
    "roles": [
        {
            "event": null,
            "timeslots": [],
            "description": "tear-down the tables and chairs",
            "title": "tear-down",
            "board_only": false,
            "id": 5070276337336320,
            "self": "https://your_url.appspot.com/roles/5070276337336320"
        },
        {
            "board_only": true,
            "event": "New Event Modified",
            "description": "Serve as an ambassador for the community club",
            "timeslots": [
                4863277368606720
            ],
            "title": "Ambassador",
            "id": 5645015573331968,
            "self": "https://your_url.appspot.com/roles/5645015573331968"
        },
        {
            "timeslots": [],
            "description": "Cleanup after event",
            "title": "Cleanup",
            "board_only": false,
            "event": null,
            "id": 5674823384563712,
            "self": "https://your_url.appspot.com/roles/5674823384563712"
        },
        {
            "title": "tear-down",
            "board_only": false,
            "event": null,
            "description": "tear-down the bouncy houses",
            "timeslots": [],
            "id": 5701330244993024,
            "self": "https://your_url.appspot.com/roles/5701330244993024"
        },
        {
            "board_only": false,
            "event": null,
            "description": "Setup tables and chairs",
            "timeslots": [],
            "title": "Setup",
            "id": 5712088936742912,
            "self": "https://your_urll.appspot.com/roles/5712088936742912"
        }
    ],
    "next": "https://your_url.appspot.com/roles?cursor=CjASKmoUbX5taWxscmVlZC00OTMtZmluYWxyEgsSBVJvbGVzGICAgMDV45IKDBgAIAA%3D"
}
```

### View a single Role
GET /roles/:id  
Returns a JSON containing the information of the requested role and status 200  
Or if the role doesn’t exist, returns “Role Not Found” with code 404  

Example:  
GET /roles/5645015573331968  

Returns:
```javascript
{
    "title": "Ambassador",
    "board_only": true,
    "event": "New Event Modified",
    "description": "Serve as an ambassador for the community club",
    "timeslots": [
        {
            "id": 4863277368606720,
            "start": "15:00",
            "end": "18:00",
            "volunteer": "5717023518621696"
        }
    ],
    "id": 5645015573331968,
    "self": "https://your_url.appspot.com/roles/5645015573331968"
}
```

### Modify a Role
PUT /roles/:id    
Receives a JSON as follows:  
```javascript 
{
    "title": “role title",
    "description": “role description",
    "board_only": boolean
}
```
If Successful, Returns ‘Role Updated’ with status 200  

Or if the event doesn’t exist, it will return ‘Role not Found’ with status 404  

Example:
PUT /roles/1234

body:
```javascript
{
    "title": “tear-down Tables",
    "description": "tear-down the tables and chairs",
    "board_only": false
}
```
Returns ‘Role Updated’ with status 200  


### Delete a Role
DELETE /roles/:id  

Deletes the role and returns status 204  
Or if the role doesn’t exist, it will return ‘Role not Found’ with status 404  

Example:  
DELETE /roles/1234  

Returns status 204  


### Assign a Timeslot to a Role
PUT /roles/:rid/timeslots/:tid  

Assigns a time slot to a role and returns status 200  
Also assigns the role’s event to the timeslot’s “event” field  
Or if the time slot doesn’t exist, it will return ‘Timeslot not Found’ with status 404  
Or if the role doesn’t exist, it will return ‘Role not Found’ with status 404  

If the time slot is already assigned to another role, returns ‘Timeslot already assigned to another role’ with status 400  

If the time slot is already assigned to the called role, returns 'Timeslot already assigned to this role'
with status 400  

Example:  
PUT /roles/1234/timeslots/5678  
 
Returns 200  

### Remove a Timeslot from a Role
DELETE /events/:eid/roles/:rid  

Removes a time slot from a role and returns status 204  
Also removes the role’s event from the timeslot’s “event” field  
Or if the time slot doesn’t exist, it will return ‘Timeslot not Found’ with status 404  
Or if the role doesn’t exist, it will return ‘Role not Found’ with status 404  

If the timeslot is not assigned to the called role, returns 'Timeslot not assigned to this role'
with status 400  

Example:  
DELET /roles/1234/timeslots/5678  

Returns 204  


### Create a Timeslot
POST  /timeslots  

Receives a JSON body as follows:  
```javascript
{
    "start_time": “Start time of event in HH:MM format”,
     ”end_time": “End time of event in HH:MM format”
}
```
If Successful, returns the ID of the newly created timeslot and status 201  

Example:  
POST /timeslots  
With body:  
```javascript
{
    "start_time": “18:00”,
     ”end_time": “20:00”
}
```
returns:  
1234314  

Creates a new timeslot  


### View all Timeslots
GET  /timeslots  
Returns a JSON containing 5 of the timeslots and a link to the next 5 timeslots and a status of 200  

Example:  
GET /timeslots  

returns:  
```javascript
{
    "timeslots": [
        {
            "role": "Ambassador",
            "length": 3,
            "end_time": "18:00",
            "volunteer": "5717023518621696",
            "start_time": "15:00",
            "id": 4863277368606720,
            "self": "https://your_url/timeslots/4863277368606720"
        },
        {
            "volunteer": null,
            "start_time": "15:00",
            "role": null,
            "length": 1,
            "end_time": "16:00",
            "id": 5071313269948416,
            "self": "https://your_url/timeslots/5071313269948416"
        },
        {
            "role": null,
            "length": 1,
            "end_time": "18:00",
            "volunteer": null,
            "start_time": "17:00",
            "id": 5077110938927104,
            "self": "https://your_url/timeslots/5077110938927104"
        },
        {
            "end_time": "18:00",
            "volunteer": null,
            "start_time": "17:00",
            "role": null,
            "length": 1,
            "id": 5080222944722944,
            "self": "https://your_url/timeslots/5080222944722944"
        },
        {
            "volunteer": null,
            "start_time": "16:00",
            "role": null,
            "length": 1,
            "end_time": "17:00",
            "id": 5081247260868608,
            "self": "https://your_url/timeslots/5081247260868608"
        }
    ],
    "next": "https://your_url/timeslots?cursor=CjQSLmoUbX5taWxscmVlZC00OTMtZmluYWxyFgsSCVRpbWVzbG90cxiAgICQ4auDCQwYACAA"
}
```
### View a single Timeslot
GET /timeslots/:id  
Returns a JSON containing the information of the requested timeslot and status 200  
Or if the timeslot doesn’t exist, returns “Timeslot Not Found” with code 404  

Example:  
GET /timeslots/4863277368606720  

Returns:
```javascript
{
    "volunteer": "5717023518621696",
    "start_time": "15:00",
    "role": "Ambassador",
    "length": 3,
    "end_time": "18:00",
    "id": 4863277368606720,
    "self": "https://your_url/timeslots/4863277368606720"
}
```
### Modify a Timeslot
PUT /timeslots/:id  
Receives a JSON as follows:  
```javascript
{
    "start_time": “Start time of event in HH:MM format”,
     ”end_time": “End time of event in HH:MM format”
}
```
If Successful, Returns ‘Timeslot Updated’ with status 200  

Or if the timeslot doesn’t exist, it will return ‘Timeslot not Found’ with status 404  

Example:  
PUT /timeslots/4863277368606720  

body:  
```javascript
{
    "end_time": "18:00",
    "start_time": "15:00"
}
```
Returns ‘Timeslot Updated’ with status 200  


### Delete a Timeslot
DELETE /roles/:id  

Deletes the role and returns status 204  
Or if the role doesn’t exist, it will return ‘Role not Found’ with status 404  

Example:  
DELETE /roles/1234  

Returns status 204  


### Assign a Volunteer to a Timeslot
PUT /timeslots/:tid/volunteers/:vid  

Assigns a volunteer to a timeslot and returns status 200  
Increases the volunteer’s “hours” field by the length of the timeslot  
Or if the timeslot doesn’t exist, it will return ‘Timeslot not Found’ with status 404  
Or if the volunteer doesn’t exist, it will return ‘Volunteer not Found’ with status 404  

If the timeslot is already taken, returns ‘Timeslot taken’ with status 400  

Example:  
PUT /timeslots/1234/volunteers/5678  

Returns “Volunteer Added”, 200  
increases Volunteer 5678’s hours by length of 1234 timeslot  


### Remove a Volunteer from a Timeslot
DELETE /timeslots/:tid/volunteers/:vid  

Removes a volunteer from a timeslot and returns status 204  
Also decreases the volunteer’s hours by the length of the timeslot  
Or if the timeslot doesn’t exist, it will return ‘Timeslot not Found’ with status 404  
Or if the volunteer doesn’t exist, it will return ‘Volunteer not Found’ with status 404  

If the timeslot is not assigned to the called volunteer, returns 'Volunteer Not Signed up for Slot'
with status 400  

Example:  
DELETE /timeslots/1234/volunteers/5678  

Returns 204  
decreases volunteer 5678’s hours by timeslot 1234’s length  
View all Volunteers  
GET  /volunteers  
Returns a JSON containing 5 of the volunteers and a link to the next 5 volunteers and a status of 200  

Example:  
GET /volunteers  

returns:
```javascript
{
    "Volunteers": [
        {
            "email": "user@oregonstate.edu",
            "first_name": "Name",
            "last_name": "Miller",
            "hours": 0,
            "board_member": false,
            "id": 5665833682468864,
            "self": "http://127.0.0.1:8080/volunteers/5665833682468864"
        },
        {
            "email": "user@gmail.com",
            "first_name": "Name2",
            "last_name": "Miller",
            "hours": 0,
            "board_member": false,
            "id": 6203010845769728,
            "self": "http://127.0.0.1:8080/volunteers/6203010845769728"
        }
    ],
    "next": null
}
```
### View a single Volunteer
GET /volunteers/:id  

Requires the user to be the actual volunteer and to provide a valid JWT.  

If no JWT is provided, returns 'No Token Provided’, with code 401  

If an invalid JWT is provided, returns 'Invalid Token', with code 401  

If a valid JWT is provided, but the user is not the volunteer, returns 403  

Returns a JSON containing the information of the requested volunteer info and status 200  
Or if the volunteer doesn’t exist, returns “Volunteer Not Found” with code 404  

Example:  
GET /volunteers/1234  

Returns:
```javascript
{
    "volunteer": "5717023518621696",
    "start_time": "15:00",
    "role": "Ambassador",
    "length": 3,
    "end_time": "18:00",
    "id": 4863277368606720,
    "self": "https://your_url/timeslots/4863277368606720"
}
```


### Modify a Volunteer
PUT /volunteers/:id  

Requires the user to be the actual volunteer and to provide a valid JWT.  

If no JWT is provided, returns 'No Token Provided’, with code 401  

If an invalid JWT is provided, returns 'Invalid Token', with code 401  

If a valid JWT is provided, but the user is not the volunteer, returns 403  

Receives a JSON as follows:
```javascript
{
    "first_name": “String with First Name”,
    "last_name": “String with Last Name”,
    "board_member": boolean

}
```
If Successful, Returns ‘Volunteer Updated’ with status 200  

Or if the volunteer doesn’t exist, it will return ‘Volunteer not Found’ with status 404  

Example:  
PUT /volunteers/1234  

body:
```javascript
{
    “first_name": “Vol”,
    "last_name": “McVolFace”,
    "board_member": false
}
```
Returns ‘Volunteer Updated’ with status 200  


### Delete a Volunteer
DELETE /volunteer/:id  

Requires the user to be the actual volunteer and to provide a valid JWT.  

If no JWT is provided, returns 'No Token Provided’, with code 401  

If an invalid JWT is provided, returns 'Invalid Token', with code 401  

If a valid JWT is provided, but the user is not the volunteer, returns 403  

Deletes the Volunteer and returns status 204  
Also removes the volunteer from any timeslots they had signed up for  

Or if the  volunteer doesn’t exist, it will return ‘Volunteer not Found’ with status 404  


Example:  
DELETE /volunteers/1234  

Returns status 204  


## Entities

### Volunteer (user)
```javascript
{
            "board_member": boolean,
            "email": String, (loaded from google profile when created)
            "first_name": String, (loaded from google profile when created)
            "last_name": “String, (loaded from google profile when created)
            "hours": Integer,
            "id": Integer
}
```




### Event
```javascript
{
            "location_name": string,
            "end_time": date-time,
            "roles": array of role entity IDs, 
            "title": string,
            "location_address": string,
            "start_time": date-time,
            "description": string,
            "admin": ID of Volunteer entity that created it,
            "event_date": date-time,
            "id": Integer
}
```
### Role
```javascript
{
            "title": string,
            "board_only": boolean,
            "event": ID of event Entity if related,
            "description": string,
            "timeslots": array of Timeslot Entity IDs if related,
            "id": Integer
}
```
### Timeslot
```javascript
{
            "role": ID of Role Entity if related,
            "length": Integer,
            "end_time": Date-Time,
            "volunteer": ID of Volunteer signed up for Role,
            "start_time": "Date-Time,
            "id": Integer
}
```
