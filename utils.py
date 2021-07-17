import os
import re
import json
import requests
import pandas as pd
from collections import defaultdict

import wikipedia as wiki

def get_wrestler_image(wrestler_name):
    corrections = {"Hakuho": "Hakuho Sho"}
    new_entry = False
    try:
        wrestler_name = corrections[wrestler_name]
    except KeyError:
        pass
    with open("static/wrestler_urls.json", "r") as w:
        d = json.load(w)
    try:
        img, url  = d[wrestler_name]
    except KeyError:
        new_entry = True
        try:
            page = wiki.WikipediaPage(wrestler_name)
            images = page.images
            img = images[0]
            url = page.url
            for i in images:
                print(wrestler_name.split()[0], i)
                if re.search(wrestler_name.split()[0], i):
                    img = i
                    break
        except:
            img = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Yokohama-Sumo-Wrestler-Defeating-a-Foreigner-1861-Ipposai-Yoshifuji.png/800px-Yokohama-Sumo-Wrestler-Defeating-a-Foreigner-1861-Ipposai-Yoshifuji.png"
            url = "https://en.wikipedia.org/wiki/Sumo"

    if new_entry:
        d[wrestler_name] = (img, url)
        with open("static/wrestler_urls.json", "w") as s:
            json.dump(d, s)
    return img, url

def parse_table(html, columns):
    start = False
    rows = []
    for l in html.split("\n"):
        if l.startswith("Makuuchi"):
            start = True
        if start and l.startswith("</pre>"):
            break
        if start:
            row = dict(zip(columns, l.split()))
            if len(row) == len(columns):
                rows.append(row)
    df = pd.DataFrame(rows)
    return df

def parse_results(html):
    """
    ['M5e', 'Okinoumi', '(1-0)', 'oshidashi', 'M4w', 'Chiyotairyu', '(0-1)']
    """
    columns = ['rank_winner',
            'winner', 'record_winner',
            'method',
            'rank_loser',
            'loser',
            'record_loser'
            ]
    return parse_table(html, columns)

def parse_next_day(html):
    columns = ['rank_east',
            'east',
            'record_east',
            'rank_west',
            'west',
            'record_west'
            ]

    return parse_table(html, columns)

def get_next_day(year, month, bansho_dir="static/banshos"):
    # get last day
    day = max([int(f.split(".")[0].split("-")[-1]) for f in
                        os.listdir(bansho_dir)]) + 1

    month_str = str(month)
    if len(month_str) == 1:
        month_str = '0' + month_str
    url = f"http://sumodb.sumogames.de/Results_text.aspx?b={year}{month_str}&d={day}"
    # print(f"Making request: {url}")
    result = requests.get(url)
    result_df = parse_next_day(result.text)
    return result_df, day

def get_results(year, month, day):
    month_str = str(month)
    if len(month_str) == 1:
        month_str = '0' + month_str
    url = f"http://sumodb.sumogames.de/Results_text.aspx?b={year}{month_str}&d={day}"
    # print(f"Making request: {url}")
    result = requests.get(url)
    result_df = parse_results(result.text)
    return result_df

def add_bansho(bansho, bansho_file='banshos.txt'):
    """
    Add a bansho to the list of banshos we will keep track of.
    We make sure all the tracked banshos are unique.
    """
    with open(bansho_file, 'r') as banshos:
        bansho_set = set()
        for b in banshos:
            bansho_set.add(b.strip())
    if bansho not in bansho_set:
        with open(bansho_file, 'a') as banshos:
            banshos.write(bansho)


def check_league(league_dict):
    return True

def get_player_score(wrestlers,
                     result_df,
                     win_pts=1,
                     lose_pts=0,
                     rival_set=None,
                     rival_multiplier=1,
                     rank_bonus=0):
    if rival_set is None:
        rival_set = set()

    ranks = ['J', 'M', 'K','S','O','Y']
    ranks = dict(zip(ranks, range(len(ranks))))

    matches = []
    score = 0
    for row in result_df.itertuples():
        played = False
        rank_factor, match_win, rival_factor = (0, 0, 0)

        if row.winner not in wrestlers and row.loser not in wrestlers:
            continue
        active_wrestler = ""
        if row.winner in wrestlers and row.loser in wrestlers:
            continue
        if row.winner in wrestlers:
            played = True
            active_wrestler = row.winner

            match_win = win_pts
            my_rank = ranks[row.rank_winner[0]]
            his_rank = ranks[row.rank_loser[0]]

            # print(row.winner, " rank ", my_rank, " won against ", his_rank, row.loser)

            rank_factor = 1 if rank_bonus== 0\
                            else 1 + (max(0, rank_bonus * (his_rank - my_rank)))
            # print("rank factor ", rank_factor)
        if row.loser in wrestlers:
            # print(row.loser, " LOST")
            played = True
            active_wrestler = row.loser

            match_win = lose_pts

            my_rank = ranks[row.rank_loser[0]]
            his_rank = ranks[row.rank_winner[0]]
            # print(row.loser, " rank ", my_rank, " lost against", his_rank, row.winner)
            rank_factor = 1 if rank_bonus== 0\
                            else 1 + (max(0, rank_bonus* (my_rank - his_rank)))

            # print("rank factor ", rank_factor)
        rival_factor = 1
        if played and {row.winner, row.loser}.intersection(rival_set):
            rival_factor = 1 if rival_multiplier == 1\
                           else rival_multiplier
        # print("rival factor ", rival_factor)
        s = match_win * rank_factor * rival_factor
        # print("match score ", s)
        score += s

        if played:
            matches.append({'rank_winner': row.rank_winner,
                            'winner': row.winner,
                            'rank_loser': row.rank_loser,
                            'loser': row.loser,
                            'method': row.method,
                            'record_winner': row.record_winner,
                            'record_loser': row.record_loser,
                            'points': s,
                            'active_wrestler': active_wrestler
                            })
    return score, matches

def rec_dd():
    return defaultdict(rec_dd)

def compute_results(league_id, n_days=15):
    """ Compute latest results for a league.
        Store everything needed to display results in a dict.
    """
    with open(f"static/leagues/{league_id}.json", "r") as l:
        league_dict = json.load(l)
    result_dict = rec_dd()

    result_dict['league_string'] = json.dumps(league_dict)
    result_dict['league_id'] = league_id
    result_dict['n_players'] = league_dict['n_players']
    result_dict['roster_size'] = league_dict['roster_size']

    bansho_year = league_dict['bansho_year']
    bansho_month = league_dict['bansho_month']

    result_dict['bansho'] = f"{bansho_month}-{bansho_year}"

    score_params = {
                    'win_pts': league_dict['win_pts'],
                    'lose_pts': league_dict['lose_pts'],
                    'rival_multiplier': league_dict['rival'],
                    'rank_bonus': league_dict['rank_bonus']
                   }


    wrestler_dict = dict()
    for player in range(league_dict['n_players']):
        wrestler_dict[player] = league_dict[f'player_{player}_roster']
        result_dict[player]['player_id'] = league_dict[f'player_{player}']

    days_played = set()
    for player in range(league_dict['n_players']):
        wrestlers = wrestler_dict[player]
        result_dict[player]['wrestlers'] = wrestlers
        for w in wrestlers:
            result_dict[w] = get_wrestler_image(w)

        total_score = 0
        wrestler_total_pts = defaultdict(int)
        for day in range(league_dict['start_day'], n_days+1):
            try:
                fname = f"static/banshos/{bansho_year}-{int(bansho_month)}-{day}.csv"
                # print(fname)
                df = pd.read_csv(fname)
            except FileNotFoundError:
                print("file not found")
                continue

            rivals = set()
            for other_player in range(league_dict['n_players']):
                if other_player != player:
                    rivals |= set(wrestler_dict[other_player])
            score_params['rival_set'] = rivals
            score, matches = get_player_score(wrestler_dict[player], df, **score_params)
            total_score += score

            result_dict[player][day]['matches'] = matches
            result_dict[player][day]['score'] = score

            for m in matches:
                # print(m['points'])
                # print(m)
                wrestler_total_pts[m['active_wrestler']] += m['points']
                result_dict[m['winner']] = get_wrestler_image(m['winner'])
                result_dict[m['loser']] = get_wrestler_image(m['loser'])

            days_played.add(day)
        result_dict[player]['total'] = total_score
        result_dict[player]['total_by_wrestler'] = wrestler_total_pts
    result_dict['days_played'] = sorted(list(days_played))

    # get sumo pictures
    return result_dict

def schedule_dict(year, month, day):
    df = pd.read_csv(f"static/schedules/{year}-{int(month)}-{day}.csv")
    matches = []
    print(df)
    for row in df.itertuples():
        matches.append({
                        'east': row.east,
                        'rank_east': row.rank_east,
                        'record_east': row.record_east,
                        'west': row.west,
                        'rank_west': row.rank_west,
                        'record_west': row.record_west
                        })
    return matches

def get_wrestler_list():
    with open("static/wrestler_urls.json", "r") as w:
        wrestlers = json.load(w)
    wrestler_list = []
    for w, (img, url) in wrestlers.items():
            wrestler_list.append({'name': w,
                                  'image': img,
                                  'url': url,
                                  'rank': 'O'
                                  })
    return sorted(wrestler_list, key=lambda x:x['name'])

if __name__ == "__main__":
    # df = get_results('2021', '07', '1')
    # df.to_csv("results_example.csv")
    df = pd.read_csv('results_example.csv')
    s = get_player_score(['Hakuho', 'Tochinoshin'], df, rivals={'Meisei', 'Aoiyama'})
    # print(s)

