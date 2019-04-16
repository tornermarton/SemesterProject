#!/usr/bin/env python3

import numpy as np
import argparse
import gzip
import os

from functions.market.features import *
from functions.preprocessing import *


def run(data_root_dir, lob_depth=100, alpha=1, window_size=100, binary_labels=False, verbosity=0):
    if data_root_dir[-1] != '/':
        data_root_dir += '/'

    n_ss_per_file = 1440
    n_asset_pairs = len(next(os.walk(data_root_dir))[1])

    # read the list of data files
    updates_file_list, snapshots_file_list = read_file_list(data_root_dir=data_root_dir, verbose=(verbosity >= 2))

    n_files = len(snapshots_file_list)

    n_days = 0

    try:
        n_days = int(n_files / n_asset_pairs)
    except ZeroDivisionError:
        print("The correct format is: root/asset_pair/... (... mean the files)")

    if verbosity >= 1:
        print(n_days, "days of data is going to be consumed from", n_asset_pairs, "asset-pairs.")
        print("UP,", "" if binary_labels else "NO_MOVE,", "DOWN labels are used at labelling.")

    ss_shape = (2 * lob_depth, 3)

    global_cnt = 0

    for i in range(n_asset_pairs):
        dataset = np.zeros([n_days * n_ss_per_file],
                           dtype=[('snapshot', np.float32, ss_shape), ('rel_prices', np.float32, 2 * lob_depth),
                                  ('timestamp', np.float32, 1), ('wamp', np.float32, 1), ('label', int, 1)])

        asset_pair_name = snapshots_file_list[0].split("/")[-2]

        filepath = data_root_dir + asset_pair_name + \
                   "_d" + str(lob_depth) + \
                   "_w" + str(window_size) + \
                   "_l" + ("2" if binary_labels else "3") + ".npy.gz"

        if verbosity >= 1:
            print("Processing:", asset_pair_name)

        progress_cnt = 0

        for j in range(n_days):
            data = np.loadtxt(snapshots_file_list[i * n_days + j], delimiter=',')

            for j, ss in enumerate(data):
                snapshot = ss[:-1].reshape(-1, 3)
                timestamp = ss[-1]
                wamp = calc_VWAP(ss)

                dataset[global_cnt]["snapshot"] = np.concatenate((
                    snapshot[0:lob_depth],
                    snapshot[100:100 + lob_depth]
                ))
                dataset[global_cnt]["rel_prices"] = [price / wamp for price in dataset[global_cnt]["snapshot"][:, 0]]
                dataset[global_cnt]["timestamp"] = timestamp
                dataset[global_cnt]["wamp"] = wamp

                # calculate label for the last snapshot for which enough data is provided with this snapshot
                if progress_cnt >= 2 * window_size - 1:
                    history_mean = np.mean(dataset["wamp"][global_cnt - 2 * window_size + 1:global_cnt - window_size])
                    future_mean = np.mean(dataset["wamp"][global_cnt - window_size + 1:global_cnt + 1])

                    spread = calc_volatility(dataset["wamp"][global_cnt - window_size + 1:global_cnt + 1])

                    if binary_labels:
                        dataset[global_cnt - window_size]["label"] = generate_binary_label(
                            history_mean=history_mean,
                            future_mean=future_mean,
                        )
                    else:
                        dataset[global_cnt - window_size]["label"] = generate_trinary_label(
                            history_mean=history_mean,
                            future_mean=future_mean,
                            threshold_base=spread,
                            alpha=alpha
                        )

                progress_cnt += 1
                global_cnt += 1

        # leave out not labeled data
        dataset = dataset[window_size - 1:global_cnt - window_size]

        with gzip.GzipFile(filepath, "wb") as file:
            np.save(file=file, arr=dataset)

        if verbosity >= 1:
            print("Done. File saved as:", filepath)

    return


if __name__ == "__main__":
    np.random.seed(1234)
    np.set_printoptions(precision=2)

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

    parser.add_argument("-w", "--window",
                        metavar="WINDOW_SIZE",
                        help="Size of the sliding window (future and history) at labelling.",
                        default=100,
                        type=int
                        )

    parser.add_argument("-l", "--binary_labels",
                        help="Do not use NO_MOVE labels.",
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

    print(args)

    run(data_root_dir=args.data_root_dir,
        lob_depth=args.depth,
        alpha=args.alpha,
        window_size=args.window,
        binary_labels=args.binary_labels,
        verbosity=args.verbosity)
