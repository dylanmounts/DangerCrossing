FROM python:3.11

ENV FLASK_RUN_HOST=0.0.0.0

# set work directory
WORKDIR /usr/src/app

# install dependencies
COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

EXPOSE 5000

# copy project
COPY . /usr/src/app/
ENV FLASK_APP=danger_crossing
ENV FLASK_ENV=development
RUN pip install -e /usr/src/app/danger_crossing