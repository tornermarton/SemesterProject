---
title: DATASET
tags: [Notebooks/SemesterProject]
created: '2019-03-08T20:57:45.398Z'
modified: '2019-03-19T18:28:25.319Z'
---

# DATASET

- [DATASET](#dataset)
  - [Sources and libraries](#sources-and-libraries)
  - [Format](#format)
    - [REST](#rest)
      - [URL](#url)
      - [Python](#python)
      - [Response payload](#response-payload)
    - [Websocket](#websocket)
      - [Subscription](#subscription)
      - [Updates](#updates)
      - [Errors](#errors)
    - [Stored data](#stored-data)
      - [Snapshot format](#snapshot-format)
      - [Update format](#update-format)


## Sources and libraries

Source: [Kraken](https://www.kraken.com)
API: [Kraken API](https://www.kraken.com/features/api)
Websocket library: [Autobahn](https://autobahn.readthedocs.io/en/latest/)

## Monitored asset-pairs

```python
[
  ['XBT', 'USD'], ['ETH', 'USD'], ['XMR', 'USD'], ['XRP', 'USD'], ['LTC', 'USD'],
  ['BCH', 'USD'], ['EOS', 'USD'], ['XLM', 'USD'], ['DASH', 'USD'], ['ADA', 'USD'],
  ['XBT', 'EUR'], ['ETH', 'EUR'], ['XMR', 'EUR'], ['XRP', 'EUR'], ['LTC', 'EUR'],
  ['BCH', 'EUR'], ['EOS', 'EUR'], ['XLM', 'EUR'], ['DASH', 'EUR'], ['ADA', 'EUR'],
  ['ETH', 'XBT'], ['XMR', 'XBT'], ['XRP', 'XBT'], ['LTC', 'XBT'], ['BCH', 'XBT']
]
```

## Format

Level2 order book data is used, where depth is set to 100 (100 best ask and 100 best bid - price aggregated). 
For each datapoint price, volume and last modification time is stored.
The data is queried via REST and Websocket API. It is saved in two formats: limit order book snapshots and updates. 
The snapshots are queried and saved every minute, the updates arrive real-time.

#### REST

pair = asset pair to get market depth for
count = maximum number of asks/bids (optional)

##### URL
```
https://api.kraken.com/0/public/Depth?pair=XBTUSD&count=100
```
##### Python

```python
import requests, json

r = requests.get('https://api.kraken.com/0/public/Depth', params={'pair': 'XBTUSD', 'count': '100'})

response = json.loads(r.text)

```

##### Response payload

```json
{
  "error":[],
  "result":{
    "XXBTZUSD":{
      "asks":[["3851.60000","7.139",1552328426], ... , ["3921.00000","0.310",1552290394]],
      "bids":[["3851.50000","24.613",1552328426], ... , ["3779.30000","16.500",1552326204]]
    }
  }
}
```


#### Websocket

Url: wss://ws.kraken.com

##### Subscription

Subscribe message payload:

```json
{
  "event": "subscribe",
  "pair": [
    "XBT/USD","XBT/EUR"
  ],
  "subscription": {
    "name": "book",
    "depth": 100
  }
}
```

Response payload (separate for each asset-pair):

Arrives if subscription status is updated (subscribe/unsubscribe).

```json
{
  "channelID": 0,
  "event": "subscriptionStatus",
  "status": "subscribed",
  "pair": "XBT/USD",
  "subscription": {
    "name": "book",
    "depth": 100
  }
}
```

##### Updates

Order book update message:

```json
[
  0,
  {"a": [
    [
      "5541.30000",
      "2.50700000",
      "1534614248.456738"
    ],
    [
      "5542.50000",
      "0.40100000",
      "1534614248.456738"
    ]
  ]
  },
  {"b": [
    [
      "5541.30000",
      "0.00000000",
      "1534614335.345903"
    ]
  ]
  }
]
```

##### Errors

Errors can be thrown as part of subscriptionStatus message.

#### Stored data

The data is stored in .csv files in the following structure:

```bash
data
└── kraken
    ├── base1_quote1
    │   ├── ss_2019-03-10.csv.gz
    │   ├── updates_2019-03-10.csv.gz
    │   ├── ss.csv
    │   └── updates.csv
    ├── base2_quote2
    ...
```

The crawler uses separate buffer files for updates and snapshots for each asset_pair and at the end of the day compresses the gathered data into separate, timestamped files.

##### Snapshot format

In a snapshot file each row is a snapshot.

A - ask  
B - bid  
D - depth   
P - price  
V - volume (quantity)  
TS - last modification timestamp  

E.g.: A_D1_P - depth1 ask price = best ask price, B_D100_V = worst bid volume

| A_D1_P | A_D1_V | A_D1_TS | A_D2_P | A_D2_V | A_D2_TS | ... | A_D100_P | A_D100_V | A_D100_TS | B_D1_P | B_D1_V | B_D1_TS | ... | B_D100_P | B_D100_V | B_D1_TS | SAVE_TS |
|--------|--------|---------|--------|--------|---------|-----|----------|----------|-----------|--------|--------|---------|-----|----------|----------|---------|---------|

##### Update format

In an update file each row is an update.

Sell/buy order update - 0/1.

Volume=0 means deleted price level, else it is the new volume (**NOT** DIFFERENCE).

| 0/1 | Price | Volume | Timestamp |
|-----|-------|--------|-----------|
