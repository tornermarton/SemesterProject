#!/usr/bin/env python3

import numpy as np
import argparse
import gzip
import os
from threading import Thread

from sklearn.preprocessing import StandardScaler

from functions.market.features import *
from functions.preprocessing import *

N_SS_PER_DAY = 1440


def process_asset_pair(file_paths: list,
                       lob_depth: int,
                       alpha: float,
                       label_window: int,
                       scaling_window: int,
                       binary_labels: bool = False,
                       use_wamp: bool = False,
                       verbosity: int = 0) -> None:
    """Process raw data from a single asset_pair. The result is a single file which contains all
    snapshots and the labels for each. """

    # How many days of data we have
    n_days = len(file_paths)

    # Numpy array shape: 3 elements (price, volume, timestamp) for each element in the LOB (both on ask and bid side)
    lob_size = 2 * lob_depth
    ss_shape = (lob_size, 3)

    # Counter to count the real number of generated datapoints (the sliding windows result some dataloss)
    global_cnt = 0

    # Path to save result
    path_array = file_paths[0].split("/")

    asset_pair = path_array[-2]

    filepath = "/".join(path_array[:-1]) + \
               "_d" + str(lob_depth) + \
               "_lw" + str(label_window) + \
               "_sw" + str(scaling_window) + \
               "_l" + ("2" if binary_labels else "3") + ".npy.gz"

    # The resulting dataset which will be saved
    dataset = np.zeros([n_days * N_SS_PER_DAY],
                       dtype=[('snapshot', np.float32, ss_shape), ('timestamp', np.float32, 1),
                              ('wamp', np.float32, 1), ('vwap', np.float32, 1),
                              ('label', int, 1)])

    if verbosity >= 1:
        print("Start processing", asset_pair, ".")

    # read dataset
    for day_cnt in range(n_days):
        raw_data = np.loadtxt(file_paths[day_cnt], delimiter=',')

        for row in raw_data:
            snapshot = row[:-1].reshape(-1, 3)

            bids = snapshot[100:100 + lob_depth]
            asks = snapshot[0:lob_depth]

            # calculate cumulative volumes
            for i in range(1, len(asks)):
                bids[i, 1] += bids[i - 1, 1]
                asks[i, 1] += asks[i - 1, 1]

            # bids should be reversed to create the correctly sorted order (ascending)
            # -> see datavisualization LOB snapshot
            dataset[global_cnt]["snapshot"] = np.concatenate((
                bids[::-1],
                asks
            ))

            dataset[global_cnt]["timestamp"] = row[-1]
            dataset[global_cnt]["wamp"] = calc_WAMP(dataset[global_cnt]["snapshot"].flatten(), lob_depth=lob_depth)
            dataset[global_cnt]["vwap"] = calc_VWAP(dataset[global_cnt]["snapshot"].flatten())

            global_cnt += 1

    # Trim blank rows (not all files contain exactly 1440 snapshots - net problems, etc.)
    dataset = dataset[:global_cnt]

    if verbosity >= 2:
        print("Start labeling", asset_pair, ".")

    # generate labels  (no labels can be generated for first and last label_window elements - data loss)
    for i in range(label_window - 1, len(dataset) - label_window):
        if use_wamp:
            feature = "wamp"
        else:
            feature = "vwap"

        # include i.
        history_mean = np.mean(dataset[feature][i - label_window + 1:i + 1])

        # exclude i.
        future_mean = np.mean(dataset[feature][i + 1:i + label_window + 1])

        # on whole period
        volatility = calc_volatility(dataset[feature][i - label_window + 1:i + label_window + 1])

        if binary_labels:
            dataset[i]["label"] = generate_binary_label(
                history_mean=history_mean,
                future_mean=future_mean,
            )
        else:
            dataset[i]["label"] = generate_trinary_label(
                history_mean=history_mean,
                future_mean=future_mean,
                threshold_base=volatility,
                alpha=alpha
            )

    if verbosity >= 2:
        print("Labeling done.")

    # Trim unlabeled data
    dataset = dataset[label_window - 1:-label_window]

    if verbosity >= 2:
        print("Start scaling", asset_pair, "asset-pair.")

    # do scaling
    day = 1440

    r = range(0, len(dataset["snapshot"]) - scaling_window - day, day)

    # scalers need to be fit in advance as during the process the preceding data is already scaled
    scalers = [StandardScaler().fit(dataset["snapshot"][i:i + scaling_window].reshape(-1, 3)) for i in r]

    for cnt, i in enumerate(r):
        start = i + scaling_window
        end = start + day

        dataset["snapshot"][start:end] = \
            scalers[cnt].transform(dataset["snapshot"][start:end].reshape(-1, 3)).reshape(-1, 2 * lob_depth, 3)

    if verbosity >= 2:
        print("Scaling done.")

    # Trim unscaled data
    dataset = dataset[scaling_window:(len(dataset) // day) * day]

    # gzip and save file
    with gzip.GzipFile(filepath, "wb") as file:
        np.save(file=file, arr=dataset)

    if verbosity >= 1:
        print("Done. File saved as:", filepath)

    return


def run(data_root_dir: str,
        lob_depth: int,
        alpha: float,
        label_window: int,
        scaling_window: int,
        binary_labels: bool = False,
        use_wamp: bool = False,
        verbosity: int = 0) -> None:
    """Do dataset generation process for each asset_pair"""

    n_asset_pairs = len(next(os.walk(data_root_dir))[1])

    updates_file_list, snapshots_file_list = read_file_list(data_root_dir=data_root_dir, verbose=(verbosity >= 2))

    n_files = len(snapshots_file_list)

    n_days = 0

    try:
        n_days = int(n_files / n_asset_pairs)
    except ZeroDivisionError:
        print("The correct format is: root/asset_pair/... (... means the files)")

    if verbosity >= 1:
        print(n_days, "days of data is going to be consumed from", n_asset_pairs, "asset-pairs.")
        print("UP,", "" if binary_labels else "NO_MOVE,", "DOWN labels are used at labelling.")

    threads = []

    for i in range(n_asset_pairs):
        t = Thread(target=process_asset_pair, args=(), kwargs={
            'file_paths': snapshots_file_list[i * n_days:i * n_days + n_days],
            'lob_depth': lob_depth,
            'alpha': alpha,
            'label_window': label_window,
            'scaling_window': scaling_window,
            'binary_labels': binary_labels,
            'use_wamp': use_wamp,
            'verbosity': verbosity
        })

        threads.append(t)

        t.start()

    for t in threads:
        t.join()

    if verbosity >= 1:
        print("Finished.")

    return


if __name__ == "__main__":
    np.random.seed(1234)

    parser = argparse.ArgumentParser(description="Generate dataset (labelling also) from collected data.")
    parser.add_argument("data_root_dir",
                        metavar="data_root_dir",
                        help="The root directory of the consumed data. (Parent folder)",
                        type=str
                        )

    parser.add_argument("-d", "--depth",
                        metavar="DEPTH",
                        help="Limit Order Book depth.",
                        default=100,
                        type=int
                        )

    parser.add_argument("-a", "--alpha",
                        metavar="ALPHA",
                        help="Alpha value at calculating threshold.",
                        default=1,
                        type=float
                        )

    parser.add_argument("-l", "--label_window",
                        metavar="WINDOW_SIZE",
                        help="Size of the sliding window (future and history) at labelling.",
                        default=100,
                        type=int
                        )

    parser.add_argument("-s", "--scaling_window",
                        metavar="WINDOW_SIZE",
                        help="Size of the sliding window at standard scaling.",
                        default=3 * 1440,
                        type=int
                        )

    parser.add_argument("--binary_labels",
                        help="Do not use NO_MOVE labels.",
                        action="store_true"
                        )

    parser.add_argument("--use_wamp",
                        help="Use WAMP instead of VWAP.",
                        action="store_true"
                        )

    parser.add_argument("-v", "--verbosity",
                        metavar="VERBOSITY",
                        help="The level of verbosity (0 is switched off).",
                        default=1,
                        choices=[0, 1, 2],
                        type=int
                        )

    args = parser.parse_args()

    run(data_root_dir=args.data_root_dir,
        lob_depth=args.depth,
        alpha=args.alpha,
        label_window=args.label_window,
        scaling_window=args.scaling_window,
        binary_labels=args.binary_labels,
        verbosity=args.verbosity)
