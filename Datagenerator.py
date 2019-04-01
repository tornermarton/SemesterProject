import keras
import numpy as np

from multiprocessing import Pool
import os

from market_features import *

# https://stanford.edu/~shervine/blog/keras-how-to-generate-data-on-the-fly
class DataGenerator(keras.utils.Sequence):
    
    def __init__(self, data_root_dir, 
                 batch_size=64, 
                 n_labels=2,
                 depth=100,
                 alpha=0.1,
                 delay=100,
                 type_="train",
                 validation_split=0.2,
                 test_split=0.1,
                 shuffle=True
                ):
        """Initialize the generator"""
        
        self.data_root_dir = data_root_dir 
        self.batch_size = batch_size 
        self.n_labels = n_labels
        self.depth = depth
        self.alpha = alpha
        self.delay = delay
        self.type_ = type_
        self.shuffle = True
        
        self.n_asset_pairs, self.statistics = self.__build_statistics()
        
        self.n_files = len(self.statistics)
        self.n_days = int(np.ceil(self.n_files / self.n_asset_pairs))
        
        return
    
    def __len__(self):
        """Number of batches per epoch"""
        return int(np.ceil(self.total_frame_count / self.batch_size))
    
    def __read_files_lists(self):
        n_asset_pairs = 0
        update_files_list = []
        snapshot_files_list = []

        for (dirpath, dirnames, filenames) in os.walk(self.data_root_dir):
            if len(dirnames) != 0:
                n_asset_pairs = len(dirnames)
                
            update_files_list.extend(
                [dirpath+'/'+filename for filename in filenames if filename != ".DS_Store" and filename[0] == 'u'])
            snapshot_files_list.extend(
                [dirpath+'/'+filename for filename in filenames if filename != ".DS_Store" and filename[0] == 's'])

        update_files_list = sorted(update_files_list)
        snapshot_files_list = sorted(snapshot_files_list)

        if self.type_=="debug":
            print(len(snapshot_files_list), "update files read.")
            print(len(update_files_list), "snapshot files read.")

        return n_asset_pairs, update_files_list, snapshot_files_list
    
    def count_samples(self, file_path):
        loaded_data = np.loadtxt(file_path, delimiter=',')
        return len(loaded_data)
    
    def __build_statistics(self):
        n_asset_pairs, update_files_list, snapshot_files_list = self.__read_files_lists()
        
        stats = np.empty([len(snapshot_files_list)], 
                         dtype=[("id", np.int, 1), ("n_samples", np.int, 1), ("path", object, 1)])
        
        # use multiprocessing to speed up process
        p = Pool(8)
        n_snapshots_in_files = p.map(self.count_samples, snapshot_files_list)
        p.terminate()
        p.join()
        
        stats["id"] = range(len(snapshot_files_list))
        stats["n_samples"] = n_snapshots_in_files
        stats["path"] = snapshot_files_list
        
        return n_asset_pairs, stats