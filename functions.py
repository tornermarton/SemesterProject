import numpy as np
import pandas as pd

import time
import math

from IPython.display import display

import matplotlib.pyplot as plt

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

def plot_LOB(lob_snapshot, depth):
    y_ask = lob_snapshot[1:depth*3:3]
    x_ask = lob_snapshot[:depth*3:3]
    
    y_bid = lob_snapshot[301:300+depth*3:3]
    x_bid = lob_snapshot[300:300+depth*3:3]
    
    y_cum_ask = []
    y_cum_bid = []
    
    sum_i = sum_j = 0
    
    for i,j in zip(y_ask, y_bid):
        sum_i += i
        sum_j += j
        y_cum_ask.append(sum_i)
        y_cum_bid.append(sum_j)
        
    fig, (ax1, ax2) = plt.subplots(2)
    
    # asks cumulated
    ax1.plot(x_ask, y_cum_ask, 'r', label="Asks")
    # bids cumulated
    ax1.plot(x_bid, y_cum_bid, 'g', label="Bids")
    
    ax1.fill_between(x_ask, y_cum_ask, y2=0, color=(1,0,0,0.3))
    ax1.fill_between(x_bid, y_cum_bid, y2=0, color=(0,1,0,0.3))

    ax1.set_title('LOB snapshot')
    ax1.set_ylabel('Cumulative Volume')
    ax1.set_xlabel('Price')
    ax1.grid()
    ax1.tick_params(grid_alpha=0.5)
    ax1.legend(loc='upper center')
    
    # asks
    ax2.plot(x_ask, y_ask, color='r', label="Asks")
    # bids
    ax2.plot(x_bid, y_bid, color='g', label="Bids")
    
    ax2.set_ylabel('Volume')
    ax2.set_xlabel('Price')
    ax2.grid()
    ax2.tick_params(grid_alpha=0.5)
    ax2.legend(loc='upper center')
    
    plt.rcParams["figure.figsize"] = [16, 9]
    plt.show()

def plot_price_movement(dataset):
    data = dataset[:, :600]
    time_ = dataset[:, 600]
    
    fig, ax = plt.subplots()
    
    # mid-price
    ax.plot(time_, [calc_mid_price(i) for i in data], 'r', label='Mid-price')
    # WAMP
    ax.plot(time_, [calc_WAMP(i) for i in data], 'g', label='WAMP')
    # WAMP
    ax.plot(time_, [calc_VWAP(i) for i in data], 'b', label='VWAP')

    ax.set_ylabel('Price')
    ax.set_xlabel('Time')
    ax.set_title('Daily price movement')

    ax.tick_params(grid_alpha=0.5)
    ax.grid()
    ax.legend(loc='upper center')
    
    plt.rcParams["figure.figsize"] = [16, 9]
    plt.show()
