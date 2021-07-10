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
