import requests
import pandas as pd

def parse_results(results):
    """
    ['M5e', 'Okinoumi', '(1-0)', 'oshidashi', 'M4w', 'Chiyotairyu', '(0-1)']
    """
    keys = ['rank_winner',
            'winner', 'record_winner',
            'method',
            'rank_loser',
            'loser',
            'record_loser'
            ]
    start = False
    rows = []
    for l in results.split("\n"):
        if l.startswith("Makuuchi"):
            start = True
        if start and l.startswith("</pre>"):
            break
        if start:
            row = dict(zip(keys, l.split()))
            if len(row) == len(keys):
                rows.append(row)
    df = pd.DataFrame(rows)
    return df

def get_results(year, month, day):
    url = f"http://sumodb.sumogames.de/Results_text.aspx?b={year}{month}&d={day}"
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
            print(b)
            bansho_set.add(b.strip())
    if bansho not in bansho_set:
        with open(bansho_file, 'a') as banshos:
            banshos.write(bansho)


def check_league(league_dict):
    return True
