import os
import numpy as np

from functions.market.features import *

__all__ = [
    "generate_binary_label",
    "generate_trinary_label",
    "make_label",
    "make_labels",
    "count_labels",
    "read_file_list"
]


# Labels: UP = 1; NO_MOVE = 0; DOWN = -1
def generate_binary_label(history_mean, future_mean):
    if future_mean < history_mean:
        return -1
    else:
        return 1


def generate_trinary_label(history_mean, future_mean, threshold_base, alpha):
    threshold = threshold_base * alpha

    if future_mean - history_mean < -threshold:
        return -1
    elif future_mean - history_mean > threshold:
        return 1
    else:
        return 0


def make_label(history_snapshots, future_snapshots, add_no_move=False, alpha=1):
    history_vwaps = [calc_VWAP(ss) for ss in history_snapshots]
    future_vwaps = [calc_VWAP(ss) for ss in future_snapshots]

    history_mean = np.mean(history_vwaps)
    future_mean = np.mean(future_vwaps)

    volatility = calc_volatility(np.concatenate((history_vwaps, future_vwaps)))

    if add_no_move:
        return generate_trinary_label(history_mean, future_mean, volatility, alpha)
    else:
        return generate_binary_label(history_mean, future_mean)


def make_labels(snapshots, add_no_move=False, alpha=1, window_size=100):
    if window_size < 1:
        raise AttributeError()

    y = np.zeros(len(snapshots) - 2 * window_size)

    for i in range(window_size, len(snapshots) - window_size):
        history_snapshots = snapshots[i - window_size:i]
        future_snapshots = snapshots[i:i + window_size]

        y[i - window_size] = make_label(history_snapshots, future_snapshots, add_no_move, alpha)

    return y


def count_labels(labels):
    up_cnt = 0
    down_cnt = 0
    nomove_cnt = 0
    for label in labels:
        if label == -1:
            down_cnt += 1
        if label == 0:
            nomove_cnt += 1
        if label == 1:
            up_cnt += 1

    print("UP labels:", up_cnt, '\t', '{}%'.format(up_cnt / (up_cnt + nomove_cnt + down_cnt) * 100))
    print("NO_MOVE labels:", nomove_cnt, '\t', '{}%'.format(nomove_cnt / (up_cnt + nomove_cnt + down_cnt) * 100))
    print("DOWN labels:", down_cnt, '\t', '{}%'.format(down_cnt / (up_cnt + nomove_cnt + down_cnt) * 100))


def read_file_list(data_root_dir, verbose=False):
    updates_file_list = []
    snapshots_file_list = []

    for (dirpath, dirnames, filenames) in os.walk(data_root_dir):
        updates_file_list.extend(
            [dirpath + '/' + filename for filename in filenames if filename != ".DS_Store" and filename[0] == 'u'])
        snapshots_file_list.extend(
            [dirpath + '/' + filename for filename in filenames if filename != ".DS_Store" and filename[0] == 's'])

    updates_file_list = sorted(updates_file_list)
    snapshots_file_list = sorted(snapshots_file_list)

    if verbose:
        print(len(snapshots_file_list), "update files read.")
        print(len(updates_file_list), "snapshot files read.")

    return updates_file_list, snapshots_file_list
