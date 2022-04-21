"""Danger Crossing

A Flask application that serves an interactive heatmap representing
traffic accidents reported by the Missouri State Highway Patrol. The
heatmap data is derived from an acc_dict.json file which is produced by
the associated Danger Maker module handled by the cron service.
"""

import secrets

import flask

app = flask.Flask(__name__)
app.secret_key = secrets.token_hex()

from danger_crossing import views
