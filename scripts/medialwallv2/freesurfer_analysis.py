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
            file_a_mwrm = f"{base_dir}/{project}_{subject_id}_A_mwrm_{hemi}_{surface_type}.stl"#not required for freesurfer
            
            # Load the meshes
            mesh_a_mwrm = trimesh.load(file_a_mwrm)
            
            # Check for self-intersections in C_mwrm mesh
            self_intersect_a_mwrm, num_triangles_a_mwrm = -1, -1 #rename _a_mwrm

            num_triangles_a_mwrm = mesh_a_mwrm.faces.shape[0] #rename _a_mwrm
            self_intersect_a_mwrm = calculate_self_intersections(mesh_a_mwrm) #rename _a_mwrm
            
            with open(csv_file, 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)

                # Write headers if the file is empty/new
                if csvfile.tell() == 0:
                    headers = ["Project", "subject_id", "Hemisphere", "Surface Type",
                            "Hausdorff Distance", "ASSD", "Chamfer Distance", 
                            "Self-Intersection A_mwrm", "Total Triangles A_mwrm", "Colored CA VTK Path"]
                    csv_writer.writerow(headers)

                # Write the results to the CSV file
                hausdorff_dist = 'NA'
                assd_val = 'NA'
                chamfer_dist = 'NA'
                colored_ca_mesh_path = "NA"
                row = [project, subject_id, hemi, surface_type,
                       hausdorff_dist, assd_val, chamfer_dist, # not required for freesurfer
                       self_intersect_a_mwrm, num_triangles_a_mwrm,
                       colored_ca_mesh_path # not required for freesurfer
                       ]
                csv_writer.writerow(row)

def process_files_wpint(base_dir, subject_id, hemis, csv_file, project):
    """Process files for calculating intersections between white and pial surfaces."""
    for hemi in hemis:
        # Construct file names for white and pial surfaces
        file_white = f"{base_dir}/{project}_{subject_id}_A_mwrm_{hemi}_white.stl"
        file_pial = f"{base_dir}/{project}_{subject_id}_A_mwrm_{hemi}_pial.stl"
        
        mesh_white = trimesh.load(file_white)
        mesh_pial = trimesh.load(file_pial)
        
        # Calculate intersections between white and pial, removing self-intersections
        intersections_white_pial = calculate_intersections(mesh_white, mesh_pial)
        
        num_triangles_white = mesh_white.faces.shape[0]
        num_triangles_pial = mesh_pial.faces.shape[0]
        
        # Write results to CSV
        with open(csv_file, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)

            # Write headers if the file is empty/new
            if csvfile.tell() == 0:
                headers = ["Project", "subject_id", "Hemisphere", 
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
