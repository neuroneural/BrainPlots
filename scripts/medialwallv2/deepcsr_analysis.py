import pyvista as pv
import numpy as np
from scipy.spatial import cKDTree
import csv
import argparse


def read_stl(file_path):
    """Read an STL file and return points."""
    mesh = pv.read(file_path)
    return mesh.points

def hausdorff_distance(tree1, tree2):
    """Calculate the Hausdorff distance between two trees."""
    d1, _ = tree1.query(tree2.data)
    d2, _ = tree2.query(tree1.data)
    return max(np.max(d1), np.max(d2))

def assd(tree1, tree2):
    """Calculate the Average Symmetric Surface Distance."""
    d1, _ = tree1.query(tree2.data)
    d2, _ = tree2.query(tree1.data)
    return (np.mean(d1) + np.mean(d2)) / 2

def chamfer_distance(tree1, tree2):
    """Calculate the Chamfer distance."""
    d1, _ = tree1.query(tree2.data)
    d2, _ = tree2.query(tree1.data)
    return np.mean(d1) + np.mean(d2)

def process_files(base_dir, subject_id, hemis, types,csv_file,project):
    """Process files according to the naming conventions."""
    for hemi in hemis:
        for surface_type in types:
            # Construct file names
            file_ba = f"{base_dir}/deepcsr_{subject_id}_BA_{hemi}_{surface_type}.stl"
            file_ca = f"{base_dir}/deepcsr_{subject_id}_CA_{hemi}_{surface_type}.stl"
            # Read points from STL files
            points_ba = read_stl(file_ba)
            points_ca = read_stl(file_ca)
            # Create cKDTree
            tree_ba = cKDTree(points_ba)
            tree_ca = cKDTree(points_ca)
            # Compute distances
            hausdorff_dist = hausdorff_distance(tree_ba, tree_ca)
            assd_val = assd(tree_ba, tree_ca)
            chamfer_dist = chamfer_distance(tree_ba, tree_ca)
            # Output results
            print(f"Hausdorff Distance ({hemi}, {surface_type}): {hausdorff_dist}")
            print(f"ASSD ({hemi}, {surface_type}): {assd_val}")
            print(f"Chamfer Distance ({hemi}, {surface_type}): {chamfer_dist}")
            with open(csv_file, 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)

                # Write headers if the file is empty/new
                if csvfile.tell() == 0:
                    csv_writer.writerow(["Project", "Subject ID", "Hemisphere", "Surface Type", "Hausdorff Distance", "ASSD", "Chamfer Distance"])

                # Construct file names and perform distance calculations...
                # Write the results to the CSV file
                csv_writer.writerow([project, subject_id, hemi, surface_type, hausdorff_dist, assd_val, chamfer_dist])
            

# Example usage
parser = argparse.ArgumentParser(description="Distance Calculation Script")
parser.add_argument("--base_dir", required=True, help="Base directory for STL files")
parser.add_argument("--project", required=True, help="project name")
parser.add_argument("--subject_id", required=True, help="Subject ID")
args = parser.parse_args()


base_dir = args.base_dir#"/data/users2/washbee/speedrun/mwexperiments/BrainPlots/scripts/medialwallv2/deepcsr"#chatgpt, make argument.
subject_id = args.subject_id#"200008"#chatgpt, make argument. 
hemis = ["lh", "rh"]
types = ["pial", "white"]
csv_file = "distances.csv"
process_files(base_dir, subject_id, hemis, types,csv_file,args.project)
