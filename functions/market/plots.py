import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from functions.market.features import *

__all__ = [
    "plot_LOB",
    "plot_price_movement",
    "plot_labels"
]

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
    
    plt.show()
    
def plot_labels(wamps, labels):
    fig, ax = plt.subplots()

    markers = ['ro' if label == -1 else 'go' if label == 1 else 'y.' for label in labels]

    for i, wamp in enumerate(wamps):    
        ax.plot(i, wamp, markers[i])
        
    ax.set_ylabel('Price')
    ax.set_xlabel('Time')
    ax.set_title('Daily price movement')
    
    ax.legend([Line2D([0], [0], marker='o', color='g', label='UP', markersize=15),
               Line2D([0], [0], marker='.', color='y', label='NO_MOVE', markersize=15),
               Line2D([0], [0], marker='o', color='r', label='DOWN', markersize=15),], 
              ('UP', 'NO_MOVE', 'DOWN'))

    plt.show()
