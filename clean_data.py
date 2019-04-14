#!/usr/bin/env python3

import time, os
import numpy as np
import pandas as pd

from functions import *


def create_dir(path):
    if not os.path.exists(path):
        os.mkdirs(path)

def clean_dataset(dataset, start_time):
    clean = np.zeros([len(dataset), 4], dtype=float)
    
    cnt = 0
    
    for dp in dataset:
        if not dp[-1] < start_time:
            clean[cnt] = dp
            cnt += 1
        
    return clean[:cnt]


def clean_updates_files(data_root_dir, verbose=False):
    update_files, snapshot_files = read_file_list(data_root_dir, verbose=verbose)
    
    for path in update_files:
        dataset = np.loadtxt(path, delimiter=',')
        
        path_array = path.split('/')
        asset_pair = path_array[-2]
        
        date = path_array[-1].split('.')[0][-10:].split('-')
        date = [int(d) for d in date]
        start_time = time.mktime((date[0], date[1], date[2], 1, 0, 0, 0, 0, -1))

        clean = clean_dataset(dataset, start_time)
        clean = np.unique(clean, axis=0)
        clean = clean[clean[:,-1].argsort()]
        
        df = pd.DataFrame(clean)
        
        df.to_csv(path, 
                  compression='gzip',
                  header=False,
                  index=False)
        
        if verbose:
            print("File:", path, "cleaned.")
        
if __name__ == "__main__":
    clean_updates_files("data/kraken/", True)