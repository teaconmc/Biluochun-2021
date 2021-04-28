# Biluochun

The crude admission system that intends to save us from manually managing Google Forms or alike.

## Setup

Python3 required.

```bash
python3 -m venv venv
. venv/bin/activate
pip3 install -r requirements.txt
```

## Start

```bash
BILUOCHUN_CONFIG_PATH="$PWD/config.py" gunicorn -w 4 -b 127.0.0.1:8080 -k gevent 'biluochun:create_app()'
```

Env. var. `BILUOCHUN_CONFIG_PATH` points to the configuration file to be used.

If test locally, either prepend `OAUTHLIB_INSECURE_TRANSPORT=1` to allow Authlib to use HTTP, 
or configure HTTPS for your local server (what?!)

## Authorization

Some endpoints require authorization. It can be obtained via `GET /api/login/azure` (which 
is the Microsoft OAuth2 login workflow). The authorization info is stored as session cookies. 

If, for any reason, you need to store session cookies under a different domain, set config field 
`SESSION_COOKIE_DOMAIN` in `config.py`. This value is used by Flask itself because Flask handles 
the session data.

When authorizaion is REQUIED but missing from the request, the response is `401 Unauthorized` 
with the following JSON object paylaod:

```json
{ "error": "Not logged in yet" }
```

### `GET /api/login/azure`

Sign-in endpoint. Will redirects you to Microsoft's sign-in page.

### `GET /api/login/complete`

OAuth callback endpoint. You should not call this. 
Microsoft, or Azure Active Directory to be more precise, will call this for you. 

The response is a `302 Found` to the frontend counterpart. The URL to that frontend is 
configurable (see `config.py`).

## Available endpoints

Any endpoints that require authorization will be noted with "Requires authorization".

### `GET /`

Always gives you `200 OK` with empty JSON Object `{}`. Serves as a simple, crude health check.

### `GET /api/users`

Retrieves all known participtants. The response is always `200 OK` with a JSON Array that looks like

```json
[
  { "id": 0, "name": "TeaCon Participtant A"  },
  { "id": 1, "name": "TeaCon Participtant B" },
  { "id": 2, "name": "TeaCon Participtant C" },
]
```

Array can be empty if no participtants are known to te system (oof).

### `GET /api/users/<user_id>`

Retrieves information about a particular participtant. If the requested participtant exists, 
the response will be `200 OK` with a JSON Object that looks like

```json
{
  "id": 1,
  "name": "TeaCon Participtant B",
}
```

Otherwise, it will return `404 Not Found` with

```json
{
  "error": "No such team"
}
```

### `GET /api/users/<user_id>/avatar`

Retrieve avatar (aka profile picture) of a specific participtant.

If the participtant does not exist, it will return `404 Not Found` with

```json
{
  "error": "No such team"
}
```

If the participtant has set an avatar, this endpoint will give you `200 OK`, and MIME type for the
response is `image/png`.
Otherwise, a `204 No Content` will be returned.

### `GET /api/team`

Retrieves all known teams. The response is always `200 OK` with a JSON Array that looks like

```json
[
  { "id": 0, "name": "Team A", "repo": "https://github.com/teaconmc/AreaControl" },
  { "id": 1, "name": "Team B", "repo": "https://github.com/teaconmc/ChromeBall" },
  { "id": 2, "name": "Team C", "repo": "https://github.com/teaconmc/SlideShow" },
]
```

Array can be empty if no teams are known to te system (oof).

### `GET /api/team/<team_id>`

Retrieves information about a particular team. If the requested team exists, the response will 
be `200 OK` with a JSON Object that looks like

```json
{
  "id": 0,
  "name": "Team B",
  "mod_name": "TeamBCraft",
  "repo": "https://github.com/teaconmc/ChromeBall",
  "desc": "Lorem ipsum",
  "invite": "0123456789abcedf"
}
```

Otherwise, it will return `404 Not Found` with

```json
{
  "error": "No such team"
}
```

### `GET /api/team/<team_id>/members`

Retrieves list of member users of the specified team. If the requested team exists, the response will 
be `200 OK` with a JSON Array that looks like

```json
[
  { "id": 0, "name": "TeaCon Participtant A" },
]
```

Array may be empty if no one is in the requested team (oof). 

If the requested team does not exist, it will return `404 Not Found` with

```json
{
  "error": "No such team"
}
```

### `GET /api/team/<team_id>/avatar`

Retrieve avatar (aka profile picture) of a specific team.

If the team does not exist, it will return `404 Not Found` with

```json
{
  "error": "No such team"
}
```

If the team has set an avatar, this endpoint will give you `200 OK`, and MIME type for the
response is `image/png`.
Otherwise, a `204 No Content` will be returned.

### `GET /api/team/<team_id>/icon`

Synonym of `GET /team/<team_id>/avatar`.

### `GET /api/team/<team_id>/profile_pic`

Synonym of `GET /team/<team_id>/avatar`.

### `GET /api/profile/`

Requires authorization.

"Homepage"-ish endpoint, will give you this JSON that describes the currently logged-in user:

```json
{
  "id": 1,
  "name": "TeaCon Participtant A",
  "team": {
    "name": "Awesome Team 1",
    "mod_name": "Team1Craft",
    "repo": "https://github.com/teaconmc/Biluochun"
  }
}
```

If the current user does not belong to a team, `team` field will be `null`.

### `GET /api/profile/avatar/`

Requires authorization.

Retrieve current user's avatar (aka profile picture). 

If the user has set an avatar, this endpoint will give you `200 OK`, and MIME type for the 
response is `image/png`. 
Otherwise, a `204 No Content` will be returned.

### `GET /api/profile/profile_pic`

Requires authorization.

Synonym of `GET /dashboard/avatar`.

### `POST /api/profile/avatar/`

Requires authorization.

Update current user's avatar (Aka profile picture).

Payload MUST `multipart/form-data` with the following REQUIRED field present:

  - `avatar`: the avatar (aka profile picture) of the currently logged-in user, type `file`.

Upon a successful `POST` request, this endpoint will return `200 OK` with empty json object `{}`.
Otherwise, it will return `400 Bad Request` with a JSON object that looks like

```json
{
  "error": "GG",
  "details": "what"
}
```

### `POST /api/profile/profile_pic`

Requires authorization.

Synonym of `POST /dashboard/avatar`.

### `POST /api/profile/`

Requires authorization.

Update user's information for currently logged-in user. 

Payload is `multipart/form-data`. Note that there is session-based CSRF protection, so the 
POST request MUST include session data.
The following fields are available:

  - `name`: the display name of the currently logged-in user, type `text`.

All fields can be left empty to indicate "no change".

Upon a successful `POST` request, this endpoint will return `200 OK` with empty json object `{}`.
Otherwise, it will return `400 Bad Request` with a JSON object that looks like

```json
{
  "error": "GG",
  "details": "what"
}
```

Note that `details` may be JSON String or JSON Object. 

### `GET /api/profile/team`

Requires authorization.

Get the information of the team that currently logged-in user belongs to.

Return value is similar to that of `GET /api/team/<team_id>`, except when the user does not 
belong to any team, the result is `404 Not Found` with:

```json
{ 
  "error": "You have not joined a team yet!"
}
```

### `POST /api/profile/team`

Requires authorization.

Accept an invitation and thus join a team. The request payload MUST be `multipart/form-data` with 
the following field(s) present:

  - `invite_code`: The invitation code of a team. `GET /api/team/<team_id>` contains it.

Upon success, an empty JSON Object `{}` is returned.

If the currently logged-in user has joined a team, the result is `409 Conflict` with:

```json
{
  "error": "You have joined a team!"
}
```

### `PUT /api/profile/team`

Requires authorization.

Synonym of `POST /api/profile/team`.

### `DELETE /api/profile/team`

Requires authorization.

Quit the current team for the currently logged-in user. This effectively set the team to `null` for 
the currently logged-in user.

Upon success, an empty JSON Object `{}` is returned.

If the currently logged-in user does not belong to any team, the result is `404 Not Found` with:

```json
{ 
  "error": "You have not joined a team yet!"
}
```

### `POST /api/team/`

Requires authorization.

Creates a new team. The currently logged-in user MUST NOT belong to any other team. 
Payload of this endpoint is OPTIONAL. If payload present, it MUST be `multipart/form-data`, 
and one or more of the following fields MAY be present in the payload:

  - `name`: the display name of the team, type `text`.  
    If not specified, default to `{user.name}'s team`.
  - `mod_name`: the display name of the mod created by this team, type `text`.  
    If not specified, default to `{user.name}'s mod`.
  - `description`: short (or long) descriptions for the team, type `text`.  
    If not specified, default to empty.  
    Note for frontend dev: you might want a `<textarea>` for this one.
  - `repo`: the URL of the team's git repository, type `text`, will be checked against 
    a URL validator.  
    If not specified, default to empty.  

Upon a successful `POST` request, this endpoint will return `200 OK` with empty json object `{}`. 
Otherwise, it will return `400 Bad Request` with a JSON object that looks like

```json
{
  "error": "You have already been in a team!" 
}
```

### `POST /api/team/<team_id>`

Requires authorization.

Update information for the team with the specified id.

Payload is `multipart/form-data`. Note that there is session-based CSRF protection, so the
POST request MUST include session data.
The following fields are available:

  - `name`: the display name of the team, type `text`.
  - `mod_name`: the display name of the mod created by this team, type `text`.
  - `description`: short (or long) descriptions for the team, type `text`. 
    Note for frontend dev: you might want a `<textarea>` for this one.
  - `repo`: the URL of the team's git repository, type `text`, will be checked against 
    a URL validator.

All fields can be left empty to indicate "no change".

Upon a successful `POST` request, this endpoint will return `200 OK` with empty json object `{}`.
Otherwise, it will return `400 Bad Request` with a JSON object that looks like

```json
{
  "error": "GG",
  "details": "what"
}
```

Note that `details` may be JSON String or JSON Object.

### `POST /api/team/<team_id>/avatar`

Requires authorization.

Update the avatar of the requested team.

This endpoint is handled in the same fashion as of `POST /api/profile/avatar/`.