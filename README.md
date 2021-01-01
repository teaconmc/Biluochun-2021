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

## Available endpoints

Note that all endpoints under `/dashboard/` require a authorization token. It can be obtained from 
`GET /login/azure` (which will redirects you to `/login/complete`). It is a JWT token; your request 
MUST have the following header line when accessing endpoints in `/dashboard/`

```
Authorization: JWT <the token>
```

Otherwise, the response is `401 Unauthorized` with the following JSON object paylaod:

```json
{ "error": "Not logged in yet" }
```

### `GET /`

Always gives you `200 OK` with empty JSON Object `{}`. Serves as a simple, crude health check.

### `GET /api/team`

Retrieves all known teams. The response is always `200 OK` with a JSON Array that looks like

```json
[
  { "name": "Team A", "repo": "https://github.com/teaconmc/AreaControl" },
  { "name": "Team B", "repo": "https://github.com/teaconmc/ChromeBall" },
  { "name": "Team C", "repo": "https://github.com/teaconmc/SlideShow" },
]
```

Array can be empty if no teams are known to te system (oof).

### `GET /api/team/<team_name>`

Retrieves information about a particular team. If the request team exists, the response will 
be `200 OK` with a JSON Object that looks like

```json
{
  "name": "Team B",
  "mod_name": "TeamBCraft",
  "repo": "https://github.com/teaconmc/ChromeBall"
}
```

Otherwise, it will return `404 Not Found` with

```json
{
  "error": "No such team"
}
```

### `GET /api/team/<team_name>/avatar`

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

### `GET /api/team/<team_name>/icon`

Synonym of `GET /team/<team_name>/avatar`.

### `GET /api/team/<team_name>/profile_pic`

Synonym of `GET /team/<team_name>/avatar`.

### `GET /login/azure`

Sign-in endpoint. Will redirects you to Microsoft's sign-in page.

### `GET /login/complete`

OAuth callback endpoint. You should not call this. 
Microsoft, or Azure Active Directory to be more precise, will call this for you. 

The response will look like 

```json
{
  "token": "<jwt token>"
}
```

Store the JWT token for later uses.

### `POST /dashboard/logout` _Deprecated_

Sign out from our system. You do not need any particular payload.

Will redirect back to Microsoft's logout system to fully sign-out.

### `GET /dashboard/`

"Homepage"-ish endpoint, will give you this JSON that describes the currently logged-in user:

```json
{
  "name": "TeaCon Participtant A",
  "team": {
    "name": "Awesome Team 1",
    "mod_name": "Team1Craft",
    "repo": "https://github.com/teaconmc/Biluochun"
  }
}
```

If the current user does not belong to a team, `team` field will be `null`.

### `GET /dashboard/avatar/`

Retrieve current user's avatar (aka profile picture). 

If the user has set an avatar, this endpoint will give you `200 OK`, and MIME type for the 
response is `image/png`. 
Otherwise, a `204 No Content` will be returned.

### `GET /dashboard/profile_pic`

Synonym of `GET /dashboard/avatar`.

### `POST /dashboard/avatar/`

Update current user's avatar (Aka profile picture).

Payload may be `multipart/form-data` with the following REQUIRED field present:

  - `avatar`: the avatar (aka profile picture) of the currently logged-in user, type `file`.

Payload may also be the image binary. Please indicate the `content-type` in your request 
header fields.

Upon a successful `POST` request, this endpoint will return `200 OK` with empty json object `{}`.
Otherwise, it will return `400 Bad Request` with a JSON object that looks like

```json
{
  "error": "GG",
  "details": "what"
}
```

### `POST /dashboard/profile_pic`

Synonym of `POST /dashboard/avatar`.

### `POST /dashboard/update`

Update user's information for currently logged-in user. 

Payload is `multipart/form-data`. Note that there is session-based CSRF protection, so the 
POST request MUST include session data.
The following fields are available:

  - `name`: the display name of the currently logged-in user, type `text`.
  - `team_id`: the numeric id of the team that this user belongs to, type `text`, must be 
    parseable as a non-negative integer.

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

### `POST /dashboard/team/new`

Creates a new team. The currently logged-in user MUST NOT belong to any other team. 
This endpoint does not need any payload.

Upon a successful `POST` request, this endpoint will return `200 OK` with empty json object `{}`. 
Otherwise, it will return `400 Bad Request` with a JSON object that looks like

```json
{
  "error": "You have already been in a team!" 
}
```

### `POST /dashboard/team/update`

Update information for the team that currently logged-in user belongs to.

Payload is `multipart/form-data`. Note that there is session-based CSRF protection, so the
POST request MUST include session data.
The following fields are available:

  - `name`: the display name of the team, type `text`.
  - `mod_name`: the display name of the mod created by this team, type `text`.
  - `profile_pic`: the avatar (aka profile picture) of the team, type `file`.
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

REQUIRES a logged-in user; otherwise `401 Unauthorized` will be returned.


