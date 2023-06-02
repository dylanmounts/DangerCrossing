"""Views module for the Danger Crossing app.

Requires the associated func.py module."""

import datetime
import json
import os

import flask

from danger_crossing import app, func

CWD = "/usr/src/app/danger_crossing/danger_crossing/"


@app.route("/", methods=["POST", "GET"])
def danger_crossing():
    """Return the heatmap template with the user's selected data."""
    injury_types = ["ALL", "MINOR", "MODERATE", "SERIOUS", "FATAL"]
    damage_types = ["ALL", "MINOR", "MODERATE", "EXTENSIVE", "TOTAL"]
    flask.session["Totals"] = {
        "All Accidents": 0,
        "Injuries": {injury.capitalize(): 0 for injury in injury_types},
        "Damages": {damage.capitalize(): 0 for damage in damage_types},
    }
    if len(flask.request.form) == 0:
        flask.session["injury_selection"] = ["SERIOUS", "FATAL"]
    else:
        flask.session["injury_selection"] = [
            injury for injury in injury_types if f"btn{injury}" in flask.request.form
        ]

    flask.session["date_start"], flask.session["date_end"] = func.get_date_times(
        flask.request.form
    )
    date_start_str = datetime.datetime.strftime(flask.session["date_start"], "%Y-%m-%d")
    date_end_str = datetime.datetime.strftime(flask.session["date_end"], "%Y-%m-%d")
    now_str = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")

    try:
        with open(
            os.path.join(CWD, "acc_dict/complete_acc_dict.json"), "r", encoding="UTF-8"
        ) as file:
            acc_dict = json.load(file)
    except FileNotFoundError:
        acc_dict = {}
    coords_list = func.process_acc_dict(acc_dict)

    # Capture session data to send to the template, but clear the session
    # to prevent unexpected behavior.
    injury_selection = flask.session["injury_selection"]
    totals = flask.session["Totals"]
    flask.session.clear()

    return flask.render_template(
        "index.html",
        date_start=date_start_str,
        now=now_str,
        date_end=date_end_str,
        injury_types=injury_types,
        injury_selection=injury_selection,
        coords_list=coords_list,
        totals=totals,
    )


@app.route("/tile", methods=["GET"])
def tile_server():
    """Create the requested tile if it doesn't exist yet, then return
    the tile."""
    zoom = flask.request.args.get("zoom")
    x_coord = flask.request.args.get("x_coord")
    y_coord = flask.request.args.get("y_coord")
    return func.get_tile(zoom, x_coord, y_coord)


if __name__ == "__main__":
    app.run()
