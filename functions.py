from market_features import *
from market_plots import *

import os

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