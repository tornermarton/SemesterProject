import numpy as np
import math

def calc_spread(lob_snapshot):
    best_bid_price  = lob_snapshot[300]
    best_ask_price  = lob_snapshot[0]
    
    return best_ask_price - best_bid_price

def calc_mid_price(lob_snapshot):
    best_bid_price  = lob_snapshot[300]
    best_ask_price  = lob_snapshot[0]
    
    return (best_bid_price + best_ask_price) / 2

def calc_WAMP(lob_snapshot):
    best_bid_price  = lob_snapshot[300]
    best_bid_volume = lob_snapshot[301]
    
    best_ask_price  = lob_snapshot[0]
    best_ask_volume = lob_snapshot[1]
    
    wamp = (best_bid_price*best_bid_volume + best_ask_price*best_ask_volume) / (best_bid_volume+best_ask_volume)
    
    return wamp

def calc_VWAP(lob_snapshot):
    sum_price_x_volume = 0
    sum_volume = 0
    
    for i in range(0, len(lob_snapshot)-1, 3):
        price = lob_snapshot[i]
        volume = lob_snapshot[i+1]
        
        sum_price_x_volume += price*volume
        sum_volume += volume
    
    return sum_price_x_volume / sum_volume

def calc_volatility(prices):
    mean = np.sum(prices) / len(prices)
    
    variance = np.sum([ (i - mean)*(i - mean) for i in prices]) / len(prices)
    
    return math.sqrt(variance)

def calc_VWAP_volatility(dataset):
    return calc_volatility([calc_VWAP(i) for i in dataset[:, :600]])

def calc_WAMP_volatility(dataset):
    return calc_volatility([calc_WAMP(i) for i in dataset[:, :600]])
