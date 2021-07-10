import requests

import pandas as pd


def parse_results(results):
    """
    ['M5e', 'Okinoumi', '(1-0)', 'oshidashi', 'M4w', 'Chiyotairyu', '(0-1)']
    """
    keys = ['rank_winner',
            'winner',
            'record_winner',
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
    print(url)
    result = requests.get(url)
    result_df = parse_results(result.text)
    pass

if __name__ == "__main__":
    results = get_results('2021', '07', '1')
    pass
