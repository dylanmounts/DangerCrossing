"""Views module for the Danger Crossing app.

Defines the routes and associated request handling logic.
"""

import datetime
import json

import flask

from danger_crossing import app, func


@app.route("/", methods=["GET"])
def danger_crossing():
    """Return the heatmap template with the user's selected data."""
    func.init_totals()
    func.set_injury_info()
    func.set_date_info()

    date_start_str = datetime.datetime.strftime(flask.session["date_start"], "%Y-%m-%d")
    date_end_str = datetime.datetime.strftime(flask.session["date_end"], "%Y-%m-%d")
    now_str = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")

    coords_dict = func.process_acc_dict(func.get_acc_dict())

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
        injury_types=func.INJURY_TYPES,
        injury_selection=injury_selection,
        coords_dict=coords_dict,
        totals=totals,
    )


@app.route("/get_accident", methods=["GET"])
def get_accident():
    """Retrieve the accident information for the given accident id from
    the accident dictionary."""
    accident_id = flask.request.args.get("accident_id")
    return json.dumps(func.get_acc_dict()[accident_id])


@app.route("/get_map", methods=["POST"])
def get_map():
    func.init_totals()
    func.set_injury_info()
    func.set_date_info()
    return func.process_acc_dict(func.get_acc_dict())


@app.route("/get_tile", methods=["GET"])
def tile_server():
    """Create the requested tile if it doesn't exist yet, then return
    the tile."""
    zoom = flask.request.args.get("zoom")
    x_coord = flask.request.args.get("x_coord")
    y_coord = flask.request.args.get("y_coord")
    return func.get_tile(zoom, x_coord, y_coord)


if __name__ == "__main__":
    app.run()
