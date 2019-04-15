import os
import numpy as np

from functions.market.features import calc_spread, calc_WAMP

__all__ = [
    "make_label",
    "make_labels",
    "read_file_list"
]

# Labels: UP = 1; NO_MOVE = 0; DOWN = -1

def __generate_trinary_label(wamp, historical_wamp_mean, spread, alpha):
    if historical_wamp_mean - wamp < -(spread*alpha):
        return -1
    elif historical_wamp_mean - wamp > spread*alpha:
        return 1
    else:
        return 0

def __generate_binary_label(wamp, historical_wamp_mean):
    if historical_wamp_mean < wamp:
        return -1
    else:
        return 1

def make_label(snapshot, historical_snapshots, add_no_move=False, alpha=1):
    spread = calc_spread(snapshot)
    wamp = calc_WAMP(snapshot)

    mean = np.mean([calc_WAMP(ss) for ss in historical_snapshots])

    if add_no_move:
        return __generate_trinary_label(wamp, mean, spread, alpha)
    else:
        return __generate_binary_label(wamp, mean)


def make_labels(snapshots, add_no_move=False, alpha=1, delay=100):
    if delay < 1:
        raise AttributeError()

    y = np.zeros(len(snapshots)-delay)

    for i in range(len(y)):
        snapshot = snapshots[i]
        historical_snapshots = snapshots[i+1:i+delay+1]

        y[i] = make_label(snapshot, historical_snapshots,  add_no_move, alpha)

    return y

def count_labels(dataset):
    up_cnt = 0
    down_cnt = 0
    nomove_cnt = 0
    for i,data in enumerate(dataset):
        if data["label"] == -1:
            down_cnt += 1
        if data["label"] == 0:
            nomove_cnt += 1
        if data["label"] == 1:
            up_cnt += 1

    print("UP labels:", up_cnt, '\t', '{}%'.format(up_cnt/(up_cnt+nomove_cnt+down_cnt)*100))
    print("NO_MOVE labels:", nomove_cnt, '\t', '{}%'.format(nomove_cnt/(up_cnt+nomove_cnt+down_cnt)*100))
    print("DOWN labels:", down_cnt, '\t', '{}%'.format(down_cnt/(up_cnt+nomove_cnt+down_cnt)*100))

def read_file_list(data_root_dir, verbose=False):
    updates_file_list = []
    snapshots_file_list = []

    for (dirpath, dirnames, filenames) in os.walk(data_root_dir):
        updates_file_list.extend([dirpath+'/'+filename for filename in filenames if filename != ".DS_Store" and filename[0] == 'u'])
        snapshots_file_list.extend([dirpath+'/'+filename for filename in filenames if filename != ".DS_Store" and filename[0] == 's'])

    updates_file_list = sorted(updates_file_list)
    snapshots_file_list = sorted(snapshots_file_list)
    
    if verbose:
        print(len(snapshots_file_list), "update files read.")
        print(len(updates_file_list), "snapshot files read.")
        
    return updates_file_list, snapshots_file_list