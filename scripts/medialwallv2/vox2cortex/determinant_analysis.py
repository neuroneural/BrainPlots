import pandas as pd
import numpy as np
import re
import glob
import pickle
import os

# Function to get the file name of the corresponding STL file
def get_stl_file_name(directory, subject_id, hemisphere, surface_type):
    stl_filename_pattern = f"{directory}/deepcsr_{subject_id}_C_mwrm_{hemisphere}_{surface_type}.stl"
    return stl_filename_pattern if os.path.exists(stl_filename_pattern) else None

# Function to load and process each file
def process_file(file, directory):
    with open(file, 'rb') as f:
        matrix = pickle.load(f)

    subject_id, hemisphere, surface_type = re.findall(r'(\d+)_(lh|rh)_(pial|white)', file)[0]
    determinant = np.linalg.det(matrix)
    stl_file_name = get_stl_file_name(directory, subject_id, hemisphere, surface_type)

    return [subject_id, hemisphere, surface_type, determinant, stl_file_name]

# Directory containing your .pkl files
directory_path = '/data/users2/washbee/speedrun/mwexperiments/BrainPlots/scripts/medialwallv2/deepcsr'

# List all .pkl files in the directory
pkl_files = [file for file in glob.glob(f"{directory_path}/*_*_*_*.pkl")]

# Process each file
data = [process_file(file, directory_path) for file in pkl_files]

# Create DataFrame from data
df = pd.DataFrame(data, columns=["subject_id", "hemisphere", "surface_type", "determinant", "stl_file_name"])

# Calculate group stats
group_means = df.groupby(["hemisphere", "surface_type"])["determinant"].mean()
group_stds = df.groupby(["hemisphere", "surface_type"])["determinant"].std()

# Adding group stats to DataFrame
df = df.join(group_means, on=["hemisphere", "surface_type"], rsuffix='_group_mean')
df = df.join(group_stds, on=["hemisphere", "surface_type"], rsuffix='_group_std')

# Calculating number of standard deviations from mean
df["number of standard deviations from mean"] = (df["determinant"] - df["determinant_group_mean"]) / df["determinant_group_std"]

# Prepare the final DataFrame for CSV
df["project"] = "deepcsr"
df = df[["project", "subject_id", "hemisphere", "surface_type", "determinant", 
         "number of standard deviations from mean", "determinant_group_mean", "determinant_group_std", "stl_file_name"]]
df.columns = ["project", "subject_id", "hemisphere", "surfaceType", "determinant", 
               "number of standard deviations from mean", "group mean", "group stdev", "stl_file_name"]

# Saving to a CSV file
csv_file_path = 'determinants.csv'
df.to_csv(csv_file_path, index=False)

# Filtering for outliers
outliers = df[np.abs(df["number of standard deviations from mean"]) > 2.5]

# Saving outliers to a separate CSV file
outliers_csv_file_path = 'determinants_outliers.csv'
outliers.to_csv(outliers_csv_file_path, index=False)

# Extracting and saving STL file paths for outliers
outlier_stl_files = outliers['stl_file_name'].dropna()
outlier_stl_file_path = 'outlier_stl_files.csv'
outlier_stl_files.to_csv(outlier_stl_file_path, index=False, header=True)
