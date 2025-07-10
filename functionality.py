# File: CMZ_data_explorer/functionality.py
# -*- coding: utf-8 -*-
"""
This module contains functions and variables used for data extraction (data_extraction.py) 
and processing of the CMZ models. It also includes functions to format molecule names, 
round values, and query the data for specific conditions related to the models.
"""
# Import necessary libraries
import numpy as np
import pandas as pd

# Define molecules names and their categories
mol_diatomic: list[str]           = ['CS', 'SO', 'SIO', 'NS+']
mol_diatomic_bulk: list[str]      = ['@CS', '@SO', '@SIO']
mol_diatomic_surface: list[str]   = ['#CS', '#SO', '#SIO']
mol_triatomic: list[str]          = ['C2S', 'HCN', 'HNC', 'HCO', 'HCO+']
mol_triatomic_bulk: list[str]     = ['@C2S', '@HCN', '@HNC', '@HCO']
mol_triatomic_surface: list[str]  = ['#C2S', '#HCN', '#HNC', '#HCO']
mol_tetratomic: list[str]         = ['H2CO', 'HNCO']
mol_tetratomic_bulk: list[str]    = ['@H2CO', '@HNCO']
mol_tetratomic_surface: list[str] = ['#H2CO', '#HNCO']
mol_polyatomic: list[str]         = ['HC3N', 'CH2CO']
mol_polyatomic_bulk: list[str]    = ['@HC3N', '@CH2CO']
mol_polyatomic_surface: list[str] = ['#HC3N', '#CH2CO']
mol_coms_gas: list[str]           = ['CH3CN', 'CH3OH', 'CH3SH', 'NH2CHO', 'CH3CCH', 'CH3CHO', 'CH3NCO', 'HCOOCH3', 'C2H5CN', 'C2H5OH', 'CH3OCH3']
mol_coms_bulk: list[str]          = ['@CH3CN', '@CH3OH', '@CH3SH', '@NH2CHO', '@CH3CCH', '@CH3CHO', '@CH3NCO', '@HCOOCH3', '@C2H5CN', '@C2H5OH', '@CH3OCH3']
mol_coms_surface: list[str]       = ['#CH3CN', '#CH3OH', '#CH3SH', '#NH2CHO', '#CH3CCH', '#CH3CHO', '#CH3NCO', '#HCOOCH3', '#C2H5CN', '#C2H5OH', '#CH3OCH3']
mol_all_gas: list[any]            = mol_diatomic + mol_triatomic + mol_tetratomic + mol_polyatomic + mol_coms_gas
mol_all_bulk: list[any]           = mol_diatomic_bulk + mol_triatomic_bulk + mol_tetratomic_bulk + mol_polyatomic_bulk + mol_coms_bulk
mol_all_surface: list[any]        = mol_diatomic_surface + mol_triatomic_surface + mol_tetratomic_surface + mol_polyatomic_surface + mol_coms_surface
mol_all: list[any]                = mol_all_gas + mol_all_bulk + mol_all_surface
mol_exc_coms_gas: list[any]       = mol_diatomic + mol_triatomic + mol_tetratomic + mol_polyatomic
mol_exc_coms_bulk: list[any]      = mol_diatomic_bulk + mol_triatomic_bulk + mol_tetratomic_bulk + mol_polyatomic_bulk
mol_exc_coms_surface: list[any]   = mol_diatomic_surface + mol_triatomic_surface + mol_tetratomic_surface + mol_polyatomic_surface
mol_exc_coms: list[any]           = mol_exc_coms_gas + mol_exc_coms_bulk + mol_exc_coms_surface


# Define ranges for the parameters used in the models
ranges_hotcore = {
                    'final_temp':  [100., 150., 200., 250., 300., 350., 400., 450., 500.],
                    'initialDens': [1.e+06, 1.e+07, 1.e+08],
                    'zeta':        [10., 100., 1000., 10000.],
                    'radfield':    [1000., 10000.],
                    'initialTemp': [15., 20., 25., 30., 35.]
}

ranges_cshock = {
                    'shock_vel':   [10., 15., 20., 25., 30., 35., 40.],
                    'initialDens': [1.e+04, 1.e+05, 1.e+06],
                    'zeta':        [10., 100., 1000., 10000.],
                    'radfield':    [10., 100., 1000., 10000.],
                    'initialTemp': [15., 20., 25., 30., 35.]
}

# --------------------
# FUNCTION DEFINITIONS
# --------------------

def format_molecule_HTML(label):
    """
    Create a proper, latex-like format for molecules. 

    Args:
        label(str) : Molecule name in its original form.

    Returns:
        str: Formatted name of a given molecule.
    """
    formatted_label = ''
    i = 0
    while i < len(label):
        char = label[i]
        if char.isdigit():
            formatted_label += f"<sub>{char}</sub>"
        elif char == '+':
            formatted_label += "<sup>+</sup>"
        elif char == 'S' and i < len(label) - 1 and label[i + 1] == 'I':
            formatted_label += "Si"
            i += 1
        else:
            formatted_label += char
        i += 1
    return formatted_label

def custom_round(value):
    """Round the value to the nearest significant figure based on its magnitude.
    Args:
        value (float): The value to be rounded.
    Returns:
        float: The rounded value.
    """
    if value < 10 and value > 9:
        return np.round(value, -1)  # Round to 10 for values between 9 and 10
    elif value < 100:
        return np.round(value, -1)  # Round to nearest 10 for values < 100
    elif value < 1000:
        return np.round(value, -2)  # Round to nearest 100 for values < 1000
    else:
        return np.round(value, -3)  # Round to nearest 1000 for values >= 1000 
    
def find_age_for_post_shock(df, initialTemp):
    """
    Find the age when the model enters the post-shock stage.
    Only for cshock models.

    Args:
    df (pd.DataFrame): DataFrame containing 'Time' and 'gasTemp' columns.
    final_temp (float): The final temperature to find the age for.

    Returns:
    float: The age when the temperature reaches the final temperature. 
           Returns None if the final temperature is not found.
    """
    temp_df = df[(df['gasTemp'] == initialTemp) & (df['Time'] > 1e1)]
    return temp_df.iloc[0]['Time']

# Function to determine the stage of the shock
def shock_stage(age, temp, initialTemp, age_for_post_shock):
    """
    Determine the stage of the shock based on age and temperature.

    Args:
    age (float): 'Time' column.
    temp (float): 'gasTemp' column.
    initialTemp (float): The initial temperature of the model.
    age_for_post_shock (float): The age when the model enters the post-shock stage.
    Returns:
    str: The stage of the shock ('pre-shock', 'shock', 'post-shock', or 'unknown').
    Notes: We only consider the first 1e5 years after the shock event for the post-shock stage.
           This is for the sake of consistency with the hotcore stage definition.
    """
    if age == 0 and temp == initialTemp:
        stage = 'pre-shock'
    elif temp > initialTemp:
        stage = 'shock'
    elif temp == initialTemp and age >= age_for_post_shock and age < age_for_post_shock+1e5:
        stage = 'post-shock'
    else:
        stage = 'unknown'
    return stage

def find_age_for_final_temp(df, final_temp):
    """
    Find the age when the temperature reaches the final temperature.
    Only for hotcore models, where the final temperature is defined.

    Args:
    df (pd.DataFrame): DataFrame containing 'Time' and 'gasTemp' columns.
    final_temp (float): The final temperature to find the age for.

    Returns:
    float: The age when the temperature reaches the final temperature. 
           Returns None if the final temperature is not found.
    """
    temp_df = df[df['gasTemp'] == final_temp]
    return temp_df.iloc[0]['Time']

def hotcore_stage(temp, age, initialTemp, final_temp, age_for_final_temp):
    """
    Determine the stage of the hot core based on temperature and age.

    Args:
    temp (float): 'gasTemp' column.
    age (float): 'Time' column.
    initialTemp (float): The initial temperature of the model.
    final_temp (float): The final temperature of the model.
    age_for_final_temp (float): The age when the model reaches the final temperature.
    Returns:
    str: The stage of the hot core ('pre-warmup', 'warmup', 'hotcore', or 'unknown').
    Notes: We only consider the first 1e5 years after the final temperature is reached for the hotcore stage.
           Consistent with a typical lifetime of a hot core.
    """
    if temp == initialTemp:
        stage = 'pre-warmup'
    elif temp > initialTemp and temp < final_temp:
        stage = 'warmup'
    elif temp == final_temp and age <= age_for_final_temp+1e5:
        stage = 'hotcore'
    else:
        stage = 'unknown'
    return stage

def read_cshock_data(grid_path, grid_df, cshock_succesful, mol_all):
    """
    Read and process data from the cshock models.
    Args:
        grid_path (str): Path to the grid file.
        grid_df (pd.DataFrame): DataFrame containing the grid.
        cshock_succesful (pd.DataFrame): DataFrame containing successful cshock models.
        mol_all (list): List of all molecules to include in the output.
    Yields:
        dict: A dictionary containing the processed data for each cshock model.
    """
    for run_id in cshock_succesful["run_id"]:

        row_info    = grid_df.query(f"run_id == '{run_id}'").iloc[0]
        parent_info = grid_df.query(f"run_id == '{row_info['parent_run_id']}'").iloc[0]

        metallicity    = parent_info['metallicity']
        cloud_radfield = parent_info['radfield']
        cloud_zeta     = parent_info['zeta']

        if row_info['model_type'] != 'cshock':
            continue
        df = pd.read_hdf(grid_path, run_id)
    
        # Ensure model returns to steady state
        if df.iloc[-1]['gasTemp'] != row_info['initialTemp']:
            continue
        # Ensure at least one shock event
        if not (df['gasTemp'] > row_info['initialTemp']).any():
            continue
        
        age_for_post_shock = find_age_for_post_shock(df, row_info['initialTemp'])

        for _, row in df.iterrows():
            yield {
                'age': row['Time'], 
                'locDens': row['Density'], 
                'locTemp': row['gasTemp'], 
                'Av': row['Av'], 
                'stage': shock_stage(row['Time'], row['gasTemp'], row_info['initialTemp'], age_for_post_shock),
                'run_id': run_id,
                'parent_run_id': row_info['parent_run_id'],
                'bm0': row_info['bm0'],
                'B0': custom_round(row_info['bm0'] * np.sqrt(row_info['initialDens'])),
                'shock_vel': row_info['shock_vel'],
                'initialDens': row_info['initialDens'], 
                'initialTemp': row_info['initialTemp'],
                'zeta': row_info['zeta'], 
                'radfield': row_info['radfield'], 
                'metallicity': metallicity, 
                'cloud_radfield': cloud_radfield, 
                'cloud_zeta': cloud_zeta,
                **{f"{species}": row[species] for species in mol_all},
            }


def read_hotcore_data(grid_path, grid_df, hotcore_succesful, mol_all):
    """
    Read and process data from the hotcore models.
    Args:
        grid_path (str): Path to the grid file.
        grid_df (pd.DataFrame): DataFrame containing the grid.
        hotcore_succesful (pd.DataFrame): DataFrame containing successful hotcore models.
        mol_all (list): List of all molecules to include in the output.
    Yields:
        dict: A dictionary containing the processed data for each hotcore model.
    """
    for run_id in hotcore_succesful["run_id"]:

        row_info    = grid_df.query(f"run_id == '{run_id}'").iloc[0]
        parent_info = grid_df.query(f"run_id == '{row_info['parent_run_id']}'").iloc[0]

        metallicity    = parent_info['metallicity']
        cloud_radfield = parent_info['radfield']
        cloud_zeta     = parent_info['zeta']
        
        if row_info['model_type'] != 'hotcore':
            continue
        df = pd.read_hdf(grid_path, run_id)

        # Ensure the model converges to final_temp
        if df.iloc[-1]['gasTemp'] != row_info['final_temp']:
            continue

        age_for_final_temp = find_age_for_final_temp(df, row_info['final_temp'])

        for _, row in df.iterrows():
            yield {
                'age': row['Time'], 
                'locDens': row['Density'], 
                'locTemp': row['gasTemp'], 
                'Av': row['Av'], 
                'stage': hotcore_stage(row['gasTemp'], row['Time'], row_info['initialTemp'], row_info['final_temp'], age_for_final_temp),
                'run_id': run_id,
                'parent_run_id': row_info['parent_run_id'],
                'bm0': row_info['bm0'],
                'final_temp': row_info['final_temp'],
                'initialDens': row_info['initialDens'], 
                'initialTemp': row_info['initialTemp'],
                'zeta': row_info['zeta'], 
                'radfield': row_info['radfield'], 
                'metallicity': metallicity, 
                'index': row_info['model_index'], 
                'cloud_radfield': cloud_radfield, 
                'cloud_zeta': cloud_zeta,
                **{f"{species}": row[species] for species in mol_all},
            }

def extract_hotcore(grid_path, grid_df, hotcore_succesful, species_list):
    """
    Extract data from the hotcore models and return it as a DataFrame.
    Args:
        grid_path (str): Path to the grid file.
        grid_df (pd.DataFrame): DataFrame containing the grid.
        hotcore_succesful (pd.DataFrame): DataFrame containing successful hotcore models.
        species_list (list): List of species to include in the output.
    Returns:
        pd.DataFrame: A DataFrame containing the extracted data for hotcore models.
    """
    extracted_data = []
    for row in read_hotcore_data(grid_path, grid_df, hotcore_succesful, species_list):
        extracted_data.append(row)
    return pd.DataFrame(extracted_data)

def extract_cshock(grid_path, grid_df, cshock_succesful, species_list):
    """
    Extract data from the cshock models and return it as a DataFrame.
    Args:
        grid_path (str): Path to the grid file.
        grid_df (pd.DataFrame): DataFrame containing the grid.
        cshock_succesful (pd.DataFrame): DataFrame containing successful cshock models.
        species_list (list): List of species to include in the output.
    Returns:
        pd.DataFrame: A DataFrame containing the extracted data for cshock models.
    """
    extracted_data = []
    for row in read_cshock_data(grid_path, grid_df, cshock_succesful, species_list):
        extracted_data.append(row)
    return pd.DataFrame(extracted_data)