"""
Webhook utils.
"""
import json
import sys

import requests
from .model import Team
from .util import user_summary

global WEBHOOK_URL, WEBHOOK_SECRET, WEBHOOK_ENABLED


def trigger_webhook(team: Team, event: str):
    if not WEBHOOK_ENABLED:
        return
    try:
        requests.post(WEBHOOK_URL, json=json.dumps({
            'event': event,  # update or create
            'webhook_secret': WEBHOOK_SECRET,
            'id': team.id,
            'name': team.name,
            'mod_name': team.mod_name,
            'members': [user_summary(member) for member in team.members],
            'profile_pic_id': team.profile_pic_id,
        }))
    except Exception as ex:
        sys.stderr.write("Failed to send webhook request: {}\n".format(ex))
