# Simple Sumo Fantasy Server


Create fantasy sumo leagues and auto update scores from [sumodb](sumodb.sumogames.de).

## Features

* Account-free
* Auto update results and leaderboards
* Rikishi images and links to wikipedia
* Custom leagues 

## Dependencies

```
pip install -r requirements.txt
```

## Setup

Create the following files and folders. Paths are relative to the repository root.

* `banshos.txt`: contains tournaments being tracked.
* `static/leagues`: contains league information
* `static/banshos`: contains results from tournaments we track
* `secret_key.py`: should define a single variable `session_key="<your secret key>"` This is just any random string.

## Run

```
python app.py
```


An easy way to host is on a [DigitalOcean Droplet](https://www.digitalocean.com/) and follow these [instructions](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04)

We are currently hosting on [sumo.ozeki.io](http://sumo.ozeki.io) but offer no service guarantees.
