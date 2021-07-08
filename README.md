# Sumo Fantasy Server

* [Active Rikishi](http://sumodb.sumogames.de/Rikishi.aspx?shikona=&heya=-1&shusshin=-1&b=202107&high=-1&hd=-1&entry=-1&intai=-1&sort=1)
* [Day results](http://sumodb.sumogames.de/Results_text.aspx?b=202107&d=1)


## Features

* Simple
* Transparent 
* Account-free
* Auto update results and leaderboards
* Trading 

## Flow

* Leauge is created with initial team choices and pushed to chain

## Components

### Teams

* Team = Pubkey (pk)
* A team is a list of `N` wrestler names `wrestlers`, where `N` is a fixed global parameter.
* A team is always accompanied by a signature `SIGN(wrestlers, bansho, day, nonce, pk)`
* Teams belong to leagues
* Teams can be modified by trading and dropping/picking up

### Leagues 

* A league is initialized by a fixed set of public keys (teams)
* Players each jointly enter:
    * Picks
    * Public key
* Once all the league initialization data is signed by all players, we create the league.
* League ID = `HASH(HASH(picks(pk_1), pk_1), HASH(picks(pk_2), pk_2), .., )`
* People can check listed public keys against the league ID to make sure no tampering.
* Optional: league ID is posted to the testnet (see: bitcoinlib package)

### Trading

* A trade can be requested and is accepted when both parties sign a trade message.
* Each team is updated accordingly

### Drops / Pick ups

* Teams can choose to drop one of their players and pick up an undrafted player.

### Scoring
  
### Rules

[Suggested rules](https://docs.google.com/document/d/1MOtX9giT3P6bUBNlyqHYC5LSrDJsSQz5UatvuD6M2f4/edit)
