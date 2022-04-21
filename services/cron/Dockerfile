FROM python:3.10

COPY requirements.txt /usr/src/app/requirements.txt
RUN pip3 install -r /usr/src/app/requirements.txt
COPY danger_maker.py /usr/src/app/danger_maker.py
RUN chmod 0644 /usr/src/app/danger_maker.py
RUN apt-get update && apt-get -y install cron
RUN crontab -l | { cat; echo "0 */3 * * * PYTHONPATH=/usr/local/lib/python3.10/site-packages python3 /usr/src/app/danger_maker.py"; } | crontab -