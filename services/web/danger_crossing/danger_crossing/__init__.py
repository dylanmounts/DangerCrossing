"""Danger Crossing

A Flask application that serves an interactive heatmap representing
traffic accidents reported by the Missouri State Highway Patrol. The
heatmap data is derived from an acc_dict.json file which is produced by
the associated Danger Maker module handled by the cron service.
"""

import secrets

import flask
import redis

app = flask.Flask(__name__)
app.secret_key = secrets.token_hex()
pool = redis.ConnectionPool(host='redis', port=6379, db=0)

from danger_crossing import views
