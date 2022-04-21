"""Functions module for Danger Crossing. Contains all necessary functions
for processing the acc_dict into a heatmap.
"""

import datetime
import os
import shutil

import flask
import requests

CWD = "/usr/src/app/danger_crossing/danger_crossing/"


def create_tile(zoom, x_coord, y_coord):
    """Create the local directory for the zoom and x_coord if it doesn't
    exist, then request the new tile from the tile server and save it.

    Args:
        zoom (str): Zoom level of new tile.
        x_coord (str): X-coordinate of new tile.
        y_coord (str): Y-coordinate of new tile.
    """
    image = f"{y_coord}.png"
    directory = os.path.join(CWD, f"tiles/{zoom}/{x_coord}")
    if not os.path.isdir(directory):
        try:
            os.mkdir(directory)
        except FileNotFoundError:
            os.mkdir(os.path.join(CWD, f"tiles/{zoom}"))
            os.mkdir(directory)
    # The function is designed to request tiles from a tile server
    # container living on the same pod. A URL for an external tile server
    # could be substituted.
    tile_server_url = "http://tile_server/tile"
    response = requests.get(
        os.path.join(tile_server_url, zoom, x_coord, y_coord), stream=True
    )
    with open(os.path.join(directory, image), "wb") as file:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, file)


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
    """Primary function for processing the acc_dict.json file. The acc_dict
    currently contains a significant amount of data which isn't being used.
    The map could be improved to incorporate it, but for now this function
    essentially parses the unnecessary information down to a list of
    coordinates matching the conditions requested by the user.

    Args:
        acc_dict (dict): JSON dictionary of accidents

    Returns:
        coord_list (list): List of coordinates to be mapped
    """
    seen_coords = {}
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
        if (lon, lat) not in seen_coords:
            flask.session["Totals"]["All Accidents"] += 1
            seen_coords[(lon, lat)] = [date_time]
        else:
            for time_check in seen_coords[(lon, lat)]:
                # The MSHP reports some incidents multiple times. This check is to avoid duplicates.
                if (
                    time_check - datetime.timedelta(minutes=5)
                    < date_time
                    < time_check + datetime.timedelta(minutes=5)
                ):
                    continue
            flask.session["Totals"]["All Accidents"] += 1
            seen_coords[(lon, lat)].append(date_time)

    coords_list = [coord[0] for coord in seen_coords.items()]

    return coords_list


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
