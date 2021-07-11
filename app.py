import os
import json
import hashlib
import datetime

from flask import Flask
from flask import request
from flask import render_template
from flask import session

from apscheduler.schedulers.background import BackgroundScheduler

from utils import add_bansho
from utils import check_league
from utils import get_results
from utils import compute_results

from secret_key import session_key

def update_leagues():
    # open banzuke.txt and see if current month in tracklist
    year = datetime.date.today().year
    month = datetime.date.today().month
    day = datetime.date.today().day

    check = False
    with open("banshos.txt", "r") as banshos:
        for l in banshos:
            bansho_date = datetime.datetime.strptime(l, "%Y-%M")
            if bansho_date.month == month and bansho_date.year == year:
                check = True

    # if yes, fetch latest tournament results and store them
    if check:
        for bansho_day in range(1, 16):
            bansho_file = f"{year}-{month}-{day}.csv"
            if bansho_file in os.listdir("static/banshos"):
                continue
            else:
                bansho_df = get_results(year, month, day)
                if len(bansho_df) > 0:
                    bansho_df.to_csv(os.path.join("static/banshos", bansho_file))
        pass

sched = BackgroundScheduler(daemon=True)
sched.add_job(update_leagues,'interval',seconds=60)
sched.start()

app = Flask(__name__)

app.secret_key = session_key

@app.route("/league_view/<league_id>", methods=["POST", "GET"])
def league_view(league_id):
    results_dict = compute_results(league_id)
    return render_template("view_league.html", results_dict=results_dict)

@app.route("/league_submit", methods=["POST", "GET"])
def league_submit():
    """
    Read the league creation inputs and validate,
    post to blockchain and return to home.
    """
    # do league sanity checks.
    if request.method == 'POST':
        print(session['bansho'])
        result = request.form

        pubkeys = []
        league_dict = {}

        league_dict['n_players'] = session['n_players']
        league_dict['roster_size'] = session['roster_size']
        league_dict['start_day'] = session['start_day']
        league_dict['bansho'] = session['bansho']
        league_dict['bansho_year'] = session['bansho'].split("-")[0]
        league_dict['bansho_month'] = session['bansho'].split("-")[1]

        for i in range(session['n_players']):

            pubkeys.append(result[f'pk_{i}'])

            wrestlers_i = [result[f'wrestler_{i}_{j}'] \
                           for j in range(session['roster_size'])]
            wrestlers_i_sorted = sorted(wrestlers_i)
            league_dict[result[f'pk_{i}']] = wrestlers_i_sorted
        pass
    if check_league(league_dict):
        league_dict_string = json.dumps(league_dict)
        league_hash = hashlib.sha256(league_dict_string.encode('ascii')).hexdigest()

        with open(f"static/leagues/{league_hash}.json", "w") as league_dump:
            league_dump.write(league_dict_string)

        return render_template("league_sign.html",
                               league_dict=league_dict_string,
                               pubkeys=pubkeys,
                               league_hash=league_hash)
    else:
        return render_template("error.html")

@app.route("/league_setup", methods=["POST", "GET"])
def league_setup():
    """
    Take in the parameters for creating the league.
    e.g. number of teams, tournament dates, scoring scheme, etc.
    """
    if request.method == 'POST':
        result = request.form
        n_players = int(result['teams'])
        roster_size = int(result['roster'])
        bansho = result['bansho']
        start_day = int(result['start'])

        session['n_players'] = n_players
        session['roster_size'] = roster_size
        session['start_day'] = start_day
        session['bansho'] = bansho

    add_bansho(bansho)

    return render_template("league_create.html",
                           roster_size=roster_size,
                           n_teams=n_players,
                           bansho=bansho,
                           start_day=start_day
                           )

@app.route("/")
def home():
    # load available leagues
    leagues = os.listdir("static/leagues")
    print(leagues)
    return render_template("home.html", leagues=leagues)

if __name__ == "__main__":
    app.run(debug=True)
