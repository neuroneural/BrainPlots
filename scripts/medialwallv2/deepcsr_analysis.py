import pyvista as pv
import numpy as np
from scipy.spatial import cKDTree
import csv
import argparse

import trimesh

import pyvista as pv
from scipy.spatial import cKDTree
from scipy.spatial import KDTree

import os
import torch
import numpy as np
import trimesh
import pyvista as pv
from scipy.spatial import cKDTree
import csv
import argparse
# from mesh_intersection.bvh_search_tree import BVH #from torch_mesh_isect
from intersection_count import *

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

def calculate_self_intersections(mesh):
    """Calculate the number of self-intersections in a mesh."""
    collision_count, _, _ = count_self_collisions(mesh, k=30)
    return collision_count

def calculate_intersections(mesh1, mesh2):
    """Calculate the number of intersections between two meshes."""
    collision_count, _, _ = count_collisions(mesh1, mesh2, k=30)
    return collision_count

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
            
            # Load the meshes
            mesh_ba = pv.read(file_ba)
            mesh_ca = pv.read(file_ca)
            mesh_c_mwrm = trimesh.load(file_c_mwrm)#pv.read(file_c_mwrm)
            
            # Check for self-intersections in C_mwrm mesh
            self_intersect_c_mwrm, num_triangles_c_mwrm = -1, -1
            # if mesh_c_mwrm.is_all_triangles():
                # num_triangles_c_mwrm = mesh_c_mwrm.n_faces
                # self_intersect_c_mwrm = calculate_self_intersections(file_c_mwrm)

            num_triangles_c_mwrm = mesh_c_mwrm.faces.shape[0]
            self_intersect_c_mwrm = calculate_self_intersections(mesh_c_mwrm)
        
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
            
            # Color the CA mesh based on distance to BA
            colored_ca_mesh = color_mesh_by_distance(mesh_ca, tree_ba)
            colored_ca_mesh_path = f"{project}_{subject_id}_CA_{hemi}_{surface_type}_distanceMesh.vtk"
            colored_ca_mesh.save(colored_ca_mesh_path)
            
            with open(csv_file, 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)

                # Write headers if the file is empty/new
                if csvfile.tell() == 0:
                    headers = ["Project", "Subject ID", "Hemisphere", "Surface Type", 
                            "Hausdorff Distance", "ASSD", "Chamfer Distance", 
                            "Self-Intersection C_mwrm", "Total Triangles C_mwrm", "Colored CA VTK Path"]
                    csv_writer.writerow(headers)

                # Write the results to the CSV file
                row = [project, subject_id, hemi, surface_type, hausdorff_dist, 
                    assd_val, chamfer_dist, self_intersect_c_mwrm, 
                    num_triangles_c_mwrm, colored_ca_mesh_path]
                csv_writer.writerow(row)



def process_files_wpint(base_dir, subject_id, hemis, csv_file, project):
    """Process files for calculating intersections between white and pial surfaces."""
    for hemi in hemis:
        # Construct file names for white and pial surfaces
        
        file_white = f"{base_dir}/{project}_{subject_id}_C_mwrm_{hemi}_white.stl"
        file_pial = f"{base_dir}/{project}_{subject_id}_C_mwrm_{hemi}_pial.stl"
                        
        # Load the white and pial meshes
        # mesh_white = pv.read(file_white)
        # mesh_pial = pv.read(file_pial)

        mesh_white = trimesh.load(file_white)
        mesh_pial = trimesh.load(file_pial)

        
        # # Calculate total intersections and self-intersections
        # total_intersections = calculate_intersections(file_white, file_pial)
        # self_intersections_white = calculate_self_intersections(file_white)
        # self_intersections_pial = calculate_self_intersections(file_pial)

        # Calculate intersections between white and pial, removing self-intersections
        #intersections_white_pial = total_intersections - (self_intersections_white + self_intersections_pial)
        intersections_white_pial = calculate_intersections(mesh_white, mesh_pial)
        # Count triangles in white and pial meshes
        # num_triangles_white = mesh_white.n_faces if mesh_white.is_all_triangles() else -1
        # num_triangles_pial = mesh_pial.n_faces if mesh_pial.is_all_triangles() else -1
        
        num_triangles_white = mesh_white.faces.shape[0]
        num_triangles_pial = mesh_pial.faces.shape[0]
        
        # Write results to CSV
        with open(csv_file, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)

            # Write headers if the file is empty/new
            if csvfile.tell() == 0:
                headers = ["Project", "Subject ID", "Hemisphere", 
                           "Intersections White-Pial", "Total Triangles White", "Total Triangles Pial", "File white","File pial"]
                csv_writer.writerow(headers)

            # Write the results to the CSV file
            row = [project, subject_id, hemi, intersections_white_pial, 
                   num_triangles_white, num_triangles_pial,
                   file_white ,file_pial]
            csv_writer.writerow(row)

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


# White-Pial Intersection CSV file
csv_file_intersections = "white_pial_intersections.csv"

# Process files
process_files_wpint(args.base_dir, args.subject_id, hemis, csv_file_intersections, args.project)
