import numpy as np
import math

#https://www.quantstart.com/articles/high-frequency-trading-ii-limit-order-book

__all__ = [
    "calc_spread",
    "calc_mid_price",
    "calc_WAMP",
    "calc_VWAP",
    "calc_volatility",
    "calc_WAMP_volatility",
    "calc_VWAP_volatility"
]

def calc_spread(lob_snapshot):
    best_bid_price  = lob_snapshot[300]
    best_ask_price  = lob_snapshot[0]
    
    return best_ask_price - best_bid_price

def calc_mid_price(lob_snapshot):
    best_bid_price  = lob_snapshot[300]
    best_ask_price  = lob_snapshot[0]
    
    return (best_bid_price + best_ask_price) / 2

# Weighted Average Mid-Price or Microprice
def calc_WAMP(lob_snapshot):
    best_bid_price  = lob_snapshot[300]
    best_bid_volume = lob_snapshot[301]
    
    best_ask_price  = lob_snapshot[0]
    best_ask_volume = lob_snapshot[1]
    
    wamp = (best_bid_volume*best_ask_price + best_ask_volume*best_bid_price) / (best_bid_volume+best_ask_volume)
    
    return wamp

def calc_VWAP(lob_snapshot):
    sum_price_x_volume_bid = 0
    sum_price_x_volume_ask = 0
    sum_volume_bid = 0
    sum_volume_ask = 0
    
    size = len(lob_snapshot)
    
    for i,j in zip(range(0, int(size/2)-1, 3), range(int(size/2), size-1, 3)):
        sum_price_x_volume_ask += lob_snapshot[i]*lob_snapshot[i+1]
        sum_price_x_volume_bid += lob_snapshot[j]*lob_snapshot[j+1]
        
        sum_volume_ask += lob_snapshot[i+1]
        sum_volume_bid += lob_snapshot[j+1]
    
    VWAP_bid = sum_price_x_volume_bid / sum_volume_bid
    VWAP_ask = sum_price_x_volume_ask / sum_volume_ask
    
    return (VWAP_bid*sum_volume_ask + VWAP_ask*sum_volume_bid) / (sum_volume_bid +sum_volume_ask)

def calc_volatility(prices):
    mean = np.sum(prices) / len(prices)
    
    variance = np.sum([ (i - mean)*(i - mean) for i in prices]) / len(prices)
    
    return math.sqrt(variance)

def calc_VWAP_volatility(dataset):
    return calc_volatility([calc_VWAP(i) for i in dataset[:, :600]])

def calc_WAMP_volatility(dataset):
    return calc_volatility([calc_WAMP(i) for i in dataset[:, :600]])
