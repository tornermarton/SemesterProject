import matplotlib.pyplot as plt
import matplotlib.patches as patches

from functions.market.features import *

__all__ = [
    "plot_LOB",
    "plot_price_movement",
    "plot_labels"
]


def plot_LOB(lob_snapshot, depth):
    y_ask = lob_snapshot[1:depth * 3:3]
    x_ask = lob_snapshot[:depth * 3:3]

    y_bid = lob_snapshot[301:300 + depth * 3:3]
    x_bid = lob_snapshot[300:300 + depth * 3:3]

    y_cum_ask = []
    y_cum_bid = []

    sum_i = sum_j = 0

    for i, j in zip(y_ask, y_bid):
        sum_i += i
        sum_j += j
        y_cum_ask.append(sum_i)
        y_cum_bid.append(sum_j)

    # share x axis
    fig, (ax1, ax2) = plt.subplots(2, sharex=True, figsize = (16, 9))
    fig.subplots_adjust(hspace=0.05, bottom=0.0)

    # asks cumulated
    ax1.plot(x_ask, y_cum_ask, 'r', label="Asks")
    # bids cumulated
    ax1.plot(x_bid, y_cum_bid, 'g', label="Bids")

    ax1.fill_between(x_ask, y_cum_ask, y2=0, color=(1, 0, 0, 0.3))
    ax1.fill_between(x_bid, y_cum_bid, y2=0, color=(0, 1, 0, 0.3))

    ax1.set_title('Limit Order Book snapshot')
    ax1.set_ylabel('Cumulative Volume')
    ax1.grid(alpha=0.5)
    ax1.legend(loc='upper center')

    # asks
    ax2.plot(x_ask, y_ask, color='r', label="Asks")
    # bids
    ax2.plot(x_bid, y_bid, color='g', label="Bids")

    ax2.set_ylabel('Volume')
    ax2.set_xlabel('Price')
    ax2.grid(alpha=0.5)
    ax2.legend(loc='upper center')

    plt.show()


def plot_price_movement(dataset):
    data = dataset[:, :600]

    fig, ax = plt.subplots(figsize = (16, 9))

    # mid-price
    ax.plot([calc_mid_price(i) for i in data], 'r', label='Mid-price')
    # WAMP
    ax.plot([calc_WAMP(i) for i in data], 'g', label='WAMP')
    # WAMP
    ax.plot([calc_VWAP(i) for i in data], 'b', label='VWAP')

    ax.set_ylabel('Price')
    ax.set_xlabel('Time')
    ax.set_title('Daily price movement')

    ax.grid(alpha=0.5)
    ax.legend(loc='upper center')

    plt.show()


def plot_labels(values, labels):
    fig, ax = plt.subplots(figsize = (16, 9))

    ax.plot(values)

    for i, label in enumerate(labels):
        if label == 1:
            ax.axvspan(i-0.5, i+0.5, alpha=0.3, color="green", lw=0)
        elif label == -1:
            ax.axvspan(i-0.5, i+0.5, alpha=0.3, color="red", lw=0)

    ax.set_ylabel('Price')
    ax.set_xlabel('Time')
    ax.set_title('Daily price movement')

    ax.legend([patches.Rectangle((0, 0), 1, 1, facecolor='green'),
               patches.Rectangle((0, 0), 1, 1, facecolor='white'),
               patches.Rectangle((0, 0), 1, 1, facecolor='red')],
              ('UP', 'SIDEWAY_MOVE', 'DOWN'))

    plt.show()
