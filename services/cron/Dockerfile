FROM python:3.11

# set work directory
WORKDIR /usr/src/app

# install dependencies
COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install -r /usr/src/app/requirements.txt

# copy project
COPY danger_maker.py /usr/src/app/danger_maker.py
RUN chmod 0644 /usr/src/app/danger_maker.py
RUN apt-get update && apt-get -y install cron
RUN crontab -l | { cat; echo "0 */3 * * * PYTHONPATH=/usr/local/lib/python3.11/site-packages python3 /usr/src/app/danger_maker.py"; } | crontab -
