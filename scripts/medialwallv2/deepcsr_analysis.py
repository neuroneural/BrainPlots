import pyvista as pv
import numpy as np
from scipy.spatial import cKDTree
import csv
import argparse

import trimesh

import pyvista as pv
from scipy.spatial import cKDTree
from scipy.spatial import KDTree

def color_mesh_by_distance(mesh, tree_other):
    """Attach distances as a scalar field to each vertex of the mesh."""
    distances, _ = tree_other.query(mesh.points)
    distance_mesh = mesh.copy()

    # Assign the distances to the point data
    distance_mesh.point_data['Distance'] = distances

    return distance_mesh


def load_mesh(file_path):
    """Load an STL file and return a trimesh object."""
    return trimesh.load(file_path)


def count_self_intersections(mesh):
    """
    Count the number of self-intersections in a mesh using PyVista.
    """
    # Attempt to find self-intersections
    intersection, _, _ = mesh.intersection(mesh)

    # Get the cell IDs involved in the intersections
    input0_cell_ids = intersection['Input0CellID']
    input1_cell_ids = intersection['Input1CellID']

    # Combine and find unique intersecting cell IDs
    # This approach assumes that each unique ID represents a distinct part of an intersection
    unique_intersecting_ids = set(input0_cell_ids).union(set(input1_cell_ids))

    # Count the number of unique intersections
    num_intersections = len(unique_intersecting_ids)

    return num_intersections


def read_stl(file_path,returnMesh=False):
    """Read an STL file and return points."""
    mesh = pv.read(file_path)
    if not returnMesh:
        return mesh.points
    else:
        return mesh
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

def process_files(base_dir, subject_id, hemis, types, csv_file, project):
    """Process files according to the naming conventions."""
    for hemi in hemis:
        for surface_type in types:
            # Construct file names for BA, CA and C_mwrm meshes
            file_ba = f"{base_dir}/{project}_{subject_id}_BA_{hemi}_{surface_type}.stl"
            file_ca = f"{base_dir}/{project}_{subject_id}_CA_{hemi}_{surface_type}.stl"
            file_c_mwrm = f"{base_dir}/{project}_{subject_id}_C_mwrm_{hemi}_{surface_type}.stl"
            
            # Load the C_mwrm mesh and check for self-intersections
            mesh_c_mwrm = pv.read(file_c_mwrm)
            # self_intersect_c_mwrm = count_self_intersections(mesh_c_mwrm)

            # Read points and create cKDTree for distance calculations between BA and CA
            points_ba = read_stl(file_ba)
            points_ca = read_stl(file_ca)
            tree_ba = cKDTree(points_ba)
            tree_ca = cKDTree(points_ca)

            # Compute distances
            hausdorff_dist = hausdorff_distance(tree_ba, tree_ca)
            assd_val = assd(tree_ba, tree_ca)
            chamfer_dist = chamfer_distance(tree_ba, tree_ca)

            # Output results and write to CSV
            print(f"Hausdorff Distance ({hemi}, {surface_type}): {hausdorff_dist}")
            print(f"ASSD ({hemi}, {surface_type}): {assd_val}")
            print(f"Chamfer Distance ({hemi}, {surface_type}): {chamfer_dist}")
            with open(csv_file, 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)

                # Write headers if the file is empty/new
                if csvfile.tell() == 0:
                    headers = ["Project", "Subject ID", "Hemisphere", "Surface Type", 
                               "Hausdorff Distance", "ASSD", "Chamfer Distance", 
                               "Self-Intersection C_mwrm", "Total Triangles C_mwrm"]
                    csv_writer.writerow(headers)

                # Write the results to the CSV file
                # row = [project, subject_id, hemi, surface_type, hausdorff_dist, 
                #        assd_val, chamfer_dist, self_intersect_c_mwrm, 
                #        len(mesh_c_mwrm.triangles)]
                row = [project, subject_id, hemi, surface_type, hausdorff_dist, 
                       assd_val, chamfer_dist, -1, 
                       -1]
                csv_writer.writerow(row)
            
            ca_mesh = read_stl(file_ca,returnMesh=True)
            
            # Color the CA mesh based on distance to BA
            colored_ca_mesh = color_mesh_by_distance(ca_mesh, tree_ba)
            print(colored_ca_mesh.point_data['Distance'])
            
            # Save the colored mesh
            colored_ca_mesh_path = f"{project}_{subject_id}_CA_{hemi}_{surface_type}_distanceMesh.vtk"
            colored_ca_mesh.save(colored_ca_mesh_path)


# Command line argument parsing
parser = argparse.ArgumentParser(description="Distance Calculation Script")
parser.add_argument("--base_dir", required=True, help="Base directory for STL files")
parser.add_argument("--project", required=True, help="project name")
parser.add_argument("--subject_id", required=True, help="Subject ID")
args = parser.parse_args()

# Process files
hemis = ["lh", "rh"]
types = ["pial", "white"]
csv_file = "distances.csv"
process_files(args.base_dir, args.subject_id, hemis, types, csv_file, args.project)