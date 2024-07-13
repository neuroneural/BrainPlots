import pandas as pd
import shutil
import os

# List of your CSV files
csv_files = [
    'cortexode_euler_top_5_worst_outliers.csv',
    'cortexode_rk4_top_5_worst_outliers.csv',
    'corticalflow_top_5_worst_outliers.csv',
    'corticalflow++_top_5_worst_outliers.csv',
    'freesurfer_top_5_worst_outliers.csv',
    'pialnn_top_5_worst_outliers.csv',
    'topofit_top_5_worst_outliers.csv',
    'vox2cortex_top_5_worst_outliers.csv'
]

for file_name in csv_files:
    # Read CSV file, assuming it's in the current directory or provide the correct path
    df = pd.read_csv(file_name)
    
    # Extract the first row after the header
    row = df.iloc[0]
    
    # Extract relevant data from the row
    value2, value3, surface_type = row[1], row[2], row[3]
    
    # Construct the base part of the file name from the CSV file name
    base_name = file_name.split('_top_5')[0]
    project_name= base_name.split('_')[0]
    # Construct the relative file path
    if project_name == 'freesurfer':
        relative_path = f"../{base_name}/{project_name}_{value2}_A_mwrm_{value3}_{surface_type}.stl"
    else:
        relative_path = f"../{base_name}/{project_name}_{value2}_C_mwrm_{value3}_{surface_type}.stl"
    
    #print('relative path',relative_path)
    
    # Determine the current working directory
    current_directory = os.getcwd()
    
    if project_name == 'freesurfer':
        destination_path = os.path.join(current_directory, f"{base_name}_{value2}_A_mwrm_{value3}_{surface_type}.stl")
    else:
        destination_path = os.path.join(current_directory, f"{base_name}_{value2}_C_mwrm_{value3}_{surface_type}.stl")

    # Copy the file from the relative path to the current directory
    shutil.copy(relative_path, destination_path)
    
    print(f"Copied: {relative_path} to {destination_path}")
