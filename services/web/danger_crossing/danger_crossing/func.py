"""Functions module for Danger Crossing. Contains all necessary functions
for processing the acc_dict into a heatmap.
"""

import datetime
import json
import os

import flask
import requests
import redis

from danger_crossing import app, pool


INJURY_TYPES = ["ALL", "MINOR", "MODERATE", "SERIOUS", "FATAL"]
DAMAGE_TYPES = ["ALL", "MINOR", "MODERATE", "EXTENSIVE", "TOTAL"]


@app.teardown_appcontext
def close_redis(e=None):
    """Closes the Redis connection when tearing down the app context."""
    redis = flask.g.pop('redis', None)

    if redis is not None:
        redis.connection_pool.disconnect()


def get_acc_dict():
    """Load the acc_dict from Redis.
    
    Returns:
        dict: A dictionary containing the accident data. If no data is
        found or a Redis error occurs, it returns an empty dictionary
    """
    try:
        redis = get_redis()
        acc_dict = redis.get('acc_dict')
        if acc_dict is None:
            return {}
        else:
            return json.loads(acc_dict)
    except redis.RedisError:
        return {}


def get_date_times(form):
    """Pull the start and end time from a Flask request form, and return them
    as datetime objects.

    Args:
        form (werkzeug.datastructures.ImmutableMultiDict): Flask request form

    Returns:
        date_start (datetime.datetime): Start date
        date_end (datetime.datetime): End date
    """
    try:
        date_end = datetime.datetime.strptime(form["date-end"], "%Y-%m-%d")
        date_end = date_end.replace(hour=23, minute=59, second=59)
        date_start = datetime.datetime.strptime(form["date-start"], "%Y-%m-%d")
    except KeyError:
        date_end = datetime.datetime.now()
        date_start = date_end - datetime.timedelta(days=365)
    return date_start, date_end


def get_redis():
    """Opens a new Redis connection if there is none yet for the
    current application context.
    """
    if 'redis' not in flask.g:
        flask.g.redis = redis.Redis(connection_pool=pool)
    return flask.g.redis


def get_report():
    """Generate an accident report based on the current session data.

    Returns:
        dict: A dictionary containing the report information.
    """
    return {
        "report_start_date": datetime.datetime.strftime(
            flask.session["date_start"], "%Y-%m-%d"),
        "report_end_date": datetime.datetime.strftime(
            flask.session["date_end"], "%Y-%m-%d"),
        "report_totals": flask.session["Totals"],
    }


def get_tile(zoom, x_coord, y_coord):
    """Retrieves the requested tile from the tile server

    Args:
        zoom (str): Zoom level of the tile.
        x_coord (str): X-coordinate of the tile.
        y_coord (str): Y-coordinate of the tile.
    """
    tile_server_url = "http://tile_server/tile"
    response = requests.get(
        os.path.join(tile_server_url, zoom, x_coord, y_coord), stream=True
    )
    return response.raw


def init_totals():
    """Initialize a session variable to keep track of totals.

    This function initializes the flask session variable "Totals" which
    contains total counts for each accident, injury, and damage type.
    """
    flask.session["Totals"] = {
        "All Accidents": 0,
        "Injuries": {injury.capitalize(): 0 for injury in INJURY_TYPES},
        "Damages": {damage.capitalize(): 0 for damage in DAMAGE_TYPES},
    }


def is_time_between(begin_time, end_time, check_time=datetime.datetime.now()):
    """Return True if check_time is between begin_time and end_time, otherwise
    return False.

    Args:
        begin_time (datetime.datetime): Start time
        end_time (datetime.datetime): End time
        check_time, optional (datetime.datetime): Check time (default is now)

    Returns:
        bool: True if check_time is between begin_time and end_time,
        otherwise False
    """
    check_time = check_time
    if begin_time < end_time:
        return begin_time <= check_time <= end_time
    return check_time >= begin_time or check_time <= end_time


def process_acc_dict(acc_dict):
    """Processes a dictionary of accident data for heatmap generation.

    This function is the main method for processing the acc_dict. It
    iterates through the input accident data, filters out invalid or
    irrelevant data points, and prepares a new dictionary where each
    entry represents an accident with lat-lon and date-time details.

    Args:
        acc_dict (dict): A dictionary containing accident data. Each
            key is an accident identifier, and each value is a
            dictionary containing details about the accident such as
            lat-lon and date-time of the accident, and information
            about the vehicles involved.

    Returns:
        coords_dict (dict): A new dictionary containing processed
            accident data suitable for heatmap generation. Each key is
            an accident identifier, and each value is a dictionary
            containing lat-lon and date-time details of the accident.
    """
    coords_dict = {}
    for acc in acc_dict:
        lat = acc_dict[acc]["lat"]
        lon = acc_dict[acc]["lon"]
        if lat == 0 or lon == 0:
            continue
        date_time = acc_dict[acc]["accdatetime"]
        # Handling for inconsistent data
        try:
            date_time = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S%z")
            date_time = date_time.replace(tzinfo=None)
        except ValueError:
            date_time = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
        if not is_time_between(
            flask.session["date_start"], flask.session["date_end"], date_time
        ):
            continue
        vehicles = acc_dict[acc]["vehicles"]
        injury_found = process_injuries(vehicles)
        # Don't include accidents we didn't ask for.
        if not injury_found:
            continue
        if acc not in coords_dict:
            flask.session["Totals"]["All Accidents"] += 1
            coords_dict[acc] = {
                "lon": lon,
                "lat": lat,
                "date_time": date_time,
            }
    return coords_dict


def process_injuries(vehicles):
    """Individual vehicles are represented as a dictionary. The function
    takes a list of those dictionaries and verifies if an injury type the
    user selected was found. If so, the injuries are counted and the
    damages are processed.

    Args:
        vehicles (list): All of the vehicles in the accident represented
        as dictionaries
    Returns:
        bool: True if the an injury type requested by the user was found,
        otherwise false
    """
    injury_found = False
    for vehicle in vehicles:
        damage_found = False
        try:
            for injury in vehicle["injuries"]:
                if injury in flask.session["injury_selection"]:
                    flask.session["Totals"]["Injuries"]["All"] += 1
                    injury_found = True
                    damage_found = True
                else:
                    continue
                if injury == "FATAL":
                    flask.session["Totals"]["Injuries"]["Fatal"] += 1
                elif injury == "SERIOUS":
                    flask.session["Totals"]["Injuries"]["Serious"] += 1
                elif injury == "MODERATE":
                    flask.session["Totals"]["Injuries"]["Moderate"] += 1
                elif injury == "MINOR":
                    flask.session["Totals"]["Injuries"]["Minor"] += 1
        except KeyError:
            pass
        if damage_found:
            process_damages(vehicle)
    return injury_found


def process_damages(vehicle):
    """Count the damages from each vehicle.

    Args:
        vehicle (dict): Representation of the vehicle as a dictionary
    """
    damage_types = ["MINOR", "MODERATE", "EXTENSIVE", "TOTAL"]
    damage = vehicle["damage"]
    # The MSHP rarely reports damages as None. We ignore those.
    if damage not in damage_types:
        return
    flask.session["Totals"]["Damages"]["All"] += 1
    flask.session["Totals"]["Damages"][damage.capitalize()] += 1


def set_injury_info():
    """Set the selected injury types in the session.

    Sets the injury type for filtering accidents based on the submitted
    form data.
    """
    if len(flask.request.form) == 0:
        flask.session["injury_selection"] = ["SERIOUS", "FATAL"]
    else:
        flask.session["injury_selection"] = [
            injury for injury in INJURY_TYPES if f"btn{injury}" in flask.request.form
        ]


def set_date_info():
    """Set the start and end dates in the session.

    Sets the start and end dates for filtering accident data based on
    the submitted form data.
    """
    flask.session["date_start"], flask.session["date_end"] = get_date_times(
        flask.request.form
    )
