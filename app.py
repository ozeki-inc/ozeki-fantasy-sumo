import sys
import os
import json
import hashlib

from flask import Flask
from flask import request
from flask import render_template


app = Flask(__name__)

def check_league(league_dict):
    return True

@app.route("/league_submit", methods=["POST", "GET"])
def league_submit():
    """
    Read the league creation inputs and validate,
    post to blockchain and return to home.
    """
    # do league sanity checks.
    if request.method == 'POST':
        result = request.form
        n_players = sum([r.startswith('pk') for r in result])
        n_wrestlers = sum([r.startswith('wres') for r in result]) // n_players

        pubkeys = []
        league_dict = {}
        for i in range(n_players):

            pubkeys.append(result[f'pk_{i}'])

            wrestlers_i = [result[f'wrestler_{i}_{j}'] for j in range(n_wrestlers)]
            wrestlers_i_sorted = sorted(wrestlers_i)
            league_dict[result[f'pk_{i}']] = wrestlers_i_sorted
        pass
    if check_league(league_dict):
        league_dict_string = json.dumps(league_dict)
        return render_template("league_sign.html",
                               league_dict=league_dict_string,
                               pubkeys=pubkeys)
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
        print(request.form)
        n_players = int(result['teams'])
        roster_size = int(result['roster'])

    return render_template("league_create.html",
                        roster_size=roster_size,
                        n_teams=n_players)

@app.route("/")
def home():
    # load available leagues
    leagues = os.listdir("static/leagues")
    print(leagues)
    return render_template("home.html", leagues=leagues)

if __name__ == "__main__":
    app.run(debug=True)
