# File: CMZ_data_explorer/data_extraction.py
# -*- coding: utf-8 -*-

# This code extracts data from the grid file and processes it into large, combined, pickle files.
# The pickle files contain data for cshock and protostellar object (hot core) models, which are used in the visualization app.
# Having such files allows for faster loading in the visualization app, as well as efficient querying the data in the app.

# Import necessary libraries and modules
# Note: Ensure that the functionality module is in the same directory or adjust the import path accordingly
import h5py
import pandas as pd
import numpy as np
import pickle
from functionality import(
                          extract_cshock,
                          extract_hotcore,
                          mol_all
                         )
from config import (
                cshock_pkl,
                hotcore_pkl,
                grid_path
               )

# Read the grid file
with h5py.File(grid_path) as file_handle:
    data_keys = list(file_handle.keys())

# Read the grid data
shape_list = [pd.read_hdf(grid_path, key).shape for key in data_keys[1:]]
grid_df     = pd.read_hdf(grid_path, key=data_keys[0])

# Add validity information to the grid data - was model run without errors and is it in the dataset?
grid_df["is_in_dataset_keys"]        = grid_df["run_id"].isin(data_keys[1:])
grid_df["parent_is_in_dataset_keys"] = grid_df["parent_run_id"].isin(data_keys[1:])

# Filter the grid data for cshock and hotcore models
cshock_df   = grid_df.query("model_type == 'cshock' & parent_is_in_dataset_keys").reset_index(drop=True)
hotcore_df  = grid_df.query("model_type == 'hotcore' & parent_is_in_dataset_keys").reset_index(drop=True)

# Filter the successful and unsuccessful cshock and hotcore models
cshock_succesful  = cshock_df[cshock_df["is_in_dataset_keys"]].reset_index(drop=True)
hotcore_succesful = hotcore_df[hotcore_df["is_in_dataset_keys"]].reset_index(drop=True)

cshock_unsuccesful  = cshock_df[~cshock_df["is_in_dataset_keys"]].reset_index(drop=True)
hotcore_unsuccesful = hotcore_df[~hotcore_df["is_in_dataset_keys"]].reset_index(drop=True)

processed_cshock  = extract_cshock(grid_path, grid_df, cshock_succesful, mol_all)
processed_hotcore = extract_hotcore(grid_path, grid_df, hotcore_succesful, mol_all)

cshock_df = pd.DataFrame(processed_cshock)
with open(cshock_pkl, 'wb') as file:
    pickle.dump(cshock_df, file)

hotcore_df = pd.DataFrame(processed_hotcore)
with open(hotcore_pkl, 'wb') as file:
    pickle.dump(hotcore_df, file)