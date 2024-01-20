import open3d as o3d
import pandas as pd
import numpy as np
import re
import glob

# Function to calculate bounding box volume of a .ply file
def calculate_bounding_box_volume(ply_file):
    point_cloud = o3d.io.read_point_cloud(ply_file)
    bounding_box = point_cloud.get_axis_aligned_bounding_box()
    extent = bounding_box.get_extent()
    volume = extent[0] * extent[1] * extent[2]
    return volume

# Function to create a corresponding .stl file path
def create_stl_file_path(subject_id, hemisphere, surface_type):
    return f"deepcsr_{subject_id}_C_mwrm_{hemisphere}_{surface_type}.stl"

# Function to process each .ply file
def process_ply_file(file):
    subject_id, hemisphere, surface_type = re.findall(r'deepcsr_(\d+)_mw_(lh|rh)_(pial|white)', file)[0]
    bounding_box_volume = calculate_bounding_box_volume(file)
    stl_file_path = create_stl_file_path(subject_id, hemisphere, surface_type)

    return [file, subject_id, hemisphere, surface_type, bounding_box_volume, stl_file_path]

# Directory containing your .ply files
directory_path = '.'

# List all .ply files in the directory
ply_files = [file for file in glob.glob(f"{directory_path}/deepcsr_*_mw_*_*.ply")]

# Process each file
data = [process_ply_file(file) for file in ply_files]

# Create DataFrame from data
df = pd.DataFrame(data, columns=["file_path", "subject_id", "hemisphere", "surface_type", "bounding_box_volume", "stl_file_path"])

# Calculate group stats
group_means = df.groupby(["hemisphere", "surface_type"])["bounding_box_volume"].mean().rename('group_mean')
group_stds = df.groupby(["hemisphere", "surface_type"])["bounding_box_volume"].std().rename('group_stdev')

# Adding group stats to DataFrame
df = df.join(group_means, on=["hemisphere", "surface_type"])
df = df.join(group_stds, on=["hemisphere", "surface_type"])

# Calculating number of standard deviations from mean
df["number of standard deviations from mean"] = (df["bounding_box_volume"] - df["group_mean"]) / df["group_stdev"]

# Prepare the final DataFrame for CSV
df["project"] = "deepcsr"
df = df[["project", "file_path", "subject_id", "hemisphere", "surface_type", "bounding_box_volume", 
         "number of standard deviations from mean", "group_mean", "group_stdev", "stl_file_path"]]

# Saving to a CSV file
csv_file_path = 'mw_volumes.csv'
df.to_csv(csv_file_path, index=False)

# Filtering for outliers
outliers = df[df["number of standard deviations from mean"] < -2.0]

# Saving outliers to a separate CSV file
outliers_csv_file_path = 'mw_outliers.csv'
outliers.to_csv(outliers_csv_file_path, index=False)

# Extracting and saving file paths of outliers
outlier_file_paths = outliers['file_path']
outlier_file_paths_csv = 'mw_outlier_ply_file_paths.csv'
outlier_file_paths.to_csv(outlier_file_paths_csv, index=False, header=True)

# Extracting and saving STL file paths of outliers
outlier_stl_file_paths = outliers['stl_file_path']
outlier_stl_file_paths_csv = 'mw_outlier_stl_file_paths.csv'
outlier_stl_file_paths.to_csv(outlier_stl_file_paths_csv, index=False, header=True)
