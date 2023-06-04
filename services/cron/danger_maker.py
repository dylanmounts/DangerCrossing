"""Danger Maker

This script scrapes the first page of accidents from the Missouri State
Highway Patrol's (MSHP) website and stores the results in a JSON
dictionary. If this dictionary already exists, the new results will be
appended to it, otherwise a new file will be created. The resulting
acc_dict.json file is where the Danger Crossing heatmap gets its data.

The script is intended to run as a crontab at some reasonable increment
to gather new accidents without impacting the MSHP's website. It
requires that `beautifulsoup4` and `requests` be installed within the
Python environment that runs the script.
"""

import datetime
import json
import re

import bs4
import requests
import redis


REDIS = redis.Redis(host='redis', port=6379, db=0)


class DangerMaker:
    """A class which represents a single instance of the web scraper which
    pulls accident information from the MSHP's website and records it in
    a JSON dictionary.

    Attributes:
        dict_dir (str): The location of the JSON dictionary on the server
        url (str): The URL of the MSHP's website
        acc_dict (dict): The JSON dictionary where accidents are recorded
    """

    def __init__(self):
        """Define attributes and begin the scraping process."""
        self.dict_dir = "/usr/src/app/acc_dict/complete_acc_dict.json"
        self.url = "https://www.mshp.dps.missouri.gov/HP68"
        self.acc_dict = self.get_acc_dict()
        self.make_danger()

    def get_acc_dict(self):
        """Return the acc_dict JSON from the dict_dir."""
        try:
            with open(self.dict_dir, "r", encoding="UTF-8") as file:
                try:
                    acc_dict = json.load(file)
                except json.decoder.JSONDecodeError:
                    acc_dict = {}
        except FileNotFoundError:
            acc_dict = {}
        return acc_dict

    def save_to_redis(self):
        """Save the acc_dict to Redis."""
        REDIS.set('acc_dict', json.dumps(self.acc_dict))

    def make_danger(self):
        """Pull the initial list of accident links from the MSHP website,
        process them, and save the results in the acc_dict JSON.
        """
        response = requests.get(f"{self.url}/search.jsp")
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        # The MSHP lists some accidents multiple times. We use a set to
        # remove duplicates.
        links = {
            link.get("href")
            for link in soup.find_all("a")
            if "ACC_RPT_NUM" in link.get("href")
        }
        for link in links:
            self.process_link(link)
        with open(self.dict_dir, "w", encoding="UTF-8") as file:
            file.write(json.dumps(self.acc_dict, indent=4))
        self.save_to_redis()

    def process_link(self, link):
        """Verify if the accident is already in the acc_dict, and if not,
        begin processing it.

        Args:
            link (str): URL of the accident to be processed
        """
        acc_num = re.search(r".+=(\d+)", link).group(1)
        if acc_num in self.acc_dict:
            print(f"{datetime.datetime.now()} already found {acc_num}")
            return
        print(f"{datetime.datetime.now()} capturing {acc_num}")
        response = requests.get(
            f"{self.url}/AccidentDetailsAction?ACC_RPT_NUM={acc_num}"
        )
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        tables = soup.find_all("table")
        for index, table in enumerate(tables):
            if index == 0:
                self.process_acc_info(table, acc_num)
            if index == 1:
                self.process_veh_info(table, acc_num)
            if index == 2:
                self.process_injury_info(table, acc_num)
            if index == 3:
                self.process_misc_info(table, acc_num)

    def process_acc_info(self, table, acc_num):
        """Pull the accident info (location, date, time, etc.) from the
        accident.

        Args:
            table (bs4.element.Tag): beautifulsoup4 table of accident info
            acc_num (str): Accident number to process
        """
        table_data = table.find_all("td")
        for index, data in enumerate(table_data):
            if index == 2:
                lat = float(data.text)
                self.acc_dict[acc_num] = {"lat": lat}
            if index == 3:
                lon = float(data.text)
                self.acc_dict[acc_num]["lon"] = lon
            if index == 4:
                date_text = data.text
            if index == 5:
                time_text = data.text
                acc_date = datetime.datetime.strptime(
                    f"{date_text} {time_text}", "%m/%d/%Y %I:%M%p"
                )
                self.acc_dict[acc_num]["accdatetime"] = str(acc_date)
            if index == 6:
                self.acc_dict[acc_num]["county"] = data.text
            if index == 7:
                self.acc_dict[acc_num]["location"] = data.text
            if index == 8:
                self.acc_dict[acc_num]["troop"] = data.text

    def process_veh_info(self, table, acc_num):
        """Pull the vehicle info (number of vehicles, damages, direction)
        from the accident.

        Args:
            table (bs4.element.Tag): beautifulsoup4 table of vehicle info
            acc_num (str): Accident number to process
        """
        self.acc_dict[acc_num]["vehicles"] = []
        table_rows = table.find_all("tr")
        for index, row in enumerate(table_rows):
            # Iterating over rows (vehicles)
            table_data = row.find_all("td")
            for i, data in enumerate(table_data):
                # Iterating across columns within rows
                if i == 2:
                    self.acc_dict[acc_num]["vehicles"].append({"damage": data.text})
                if i == 10:
                    self.acc_dict[acc_num]["vehicles"][index - 1][
                        "direction"
                    ] = data.text

    def process_injury_info(self, table, acc_num):
        """Pull the injury info (number of injuries and severity) from
        the accident.

        Args:
            table (bs4.element.Tag): beautifulsoup4 table of injury info
            acc_num (str): Accident number to process
        """
        table_rows = table.find_all("tr")
        for row in table_rows:
            table_data = row.find_all("td")
            for index, data in enumerate(table_data):
                if index == 0:
                    # We're using the vehicle number as the index, so we
                    # need to start at 0.
                    veh_no = int(data.text) - 1
                    try:
                        self.acc_dict[acc_num]["vehicles"][veh_no]["injured"] += 1
                    except KeyError:
                        self.acc_dict[acc_num]["vehicles"][veh_no]["injured"] = 1
                if index == 4:
                    try:
                        self.acc_dict[acc_num]["vehicles"][veh_no]["injuries"].append(
                            data.text
                        )
                    except KeyError:
                        self.acc_dict[acc_num]["vehicles"][veh_no]["injuries"] = [
                            data.text
                        ]

    def process_misc_info(self, table, acc_num):
        """Pull the accident description from the accident.

        Args:
            table (bs4.element.Tag): beautifulsoup4 table of misc info
            acc_num (str): Accident number to process
        """
        table_data = table.find_all("td")
        for data in table_data:
            self.acc_dict[acc_num]["misc"] = data.text

    def save_to_redis(self):
        """Save the acc_dict to Redis."""
        REDIS.set('acc_dict', json.dumps(self.acc_dict))


def main():
    """Call the DangerMaker class."""
    DangerMaker()


if __name__ == "__main__":
    main()
