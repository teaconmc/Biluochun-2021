"""
Webhook utils.
"""
import json
import sys

import requests
import hmac
import hashlib
from .model import Team
from .util import user_summary

WEBHOOK_URL = ""
WEBHOOK_SECRET = b""
WEBHOOK_ENABLED = False


def init_webhook_config(app):
    global WEBHOOK_URL, WEBHOOK_SECRET, WEBHOOK_ENABLED
    WEBHOOK_URL = app.config["WEBHOOK_URL"]
    WEBHOOK_SECRET = app.config["WEBHOOK_SECRET"]
    WEBHOOK_ENABLED = app.config["WEBHOOK_ENABLED"]


async def trigger_webhook(team: Team, event: str):
    if not WEBHOOK_ENABLED:
        sys.stderr.write("Webhook is not enabled.\n")
        return
    try:
        body_str = json.dumps({
            'event': event,  # update or create
            'id': team.id,
            'name': team.name,
            'mod_name': team.mod_name,
            'members': [user_summary(member) for member in team.members],
            'profile_pic_id': team.profile_pic_id,
        }, ensure_ascii=False)
        body = bytes(body_str, "utf-8")

        h = hmac.new(WEBHOOK_SECRET, body, hashlib.sha256)

        s = requests.Session()
        s.headers.update({"HmacSha256": h.hexdigest()})
        s.post(WEBHOOK_URL, data=body)
    except Exception as ex:
        sys.stderr.write("Failed to send webhook request: {}\n".format(ex))
