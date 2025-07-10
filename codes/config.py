# -------- Configuration file for the CMZ data explorer --------
# This file contains paths and constants used in:
# - the data extraction (if you don't have the pickle files), and
# - the visualization process.
# It is essential to **set the absolute paths correctly**

# Define the absolute paths for the input pickle files
hotcore_pkl = "YOUR_ABSOLUTE_PATH/hotcore.pkl"
cshock_pkl  = "YOUR_ABSOLUTE_PATH/cshock.pkl"

ZETA_SCALE_FACTOR   = 1.310e-17 # Scale factor for zeta values: the data is presented as ZETA/ZETA_0, where ZETA_0 = 1.310e-17
DEFAULT_MARKER_SIZE = 12        # Default marker size for the scatter plot - but it is also adjustable in the visualization
DEFAULT_OPACITY     = 0.7       # Default opacity for the scatter plot

# --------------------------------------------------------------
# IF YOU NEED TO GENERATE PKL FILES FROM THE GRID DATA
# Define the absolute path to the grid file,
# i.e., the one downloaded from Zenodo.
# --------------------------------------------------------------
grid_name   = 'GRID_NAME.h5'
grid_path   = f"YOUR_ABSOLUTE_PATH/{grid_name}"