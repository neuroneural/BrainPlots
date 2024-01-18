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
from mesh_intersection.bvh_search_tree import BVH #from torch_mesh_isect

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

def calculate_self_intersections(file_path, max_collisions=8, device='cuda'):
    input_mesh = trimesh.load(file_path)
    vertices = torch.tensor(input_mesh.vertices, dtype=torch.float32, device=device)
    faces = torch.tensor(input_mesh.faces.astype(np.int64), dtype=torch.long, device=device)
    triangles = vertices[faces].unsqueeze(dim=0)
    bvh_tree = BVH(max_collisions=max_collisions)
    outputs = bvh_tree(triangles).detach().cpu().numpy().squeeze()
    collisions = outputs[outputs[:, 0] >= 0, :]
    return collisions.shape[0]


def calculate_intersections(file_path1, file_path2, max_collisions=8, device='cuda'):
    # Load the first mesh
    mesh1 = trimesh.load(file_path1)
    vertices1 = torch.tensor(mesh1.vertices, dtype=torch.float32, device=device)
    faces1 = torch.tensor(mesh1.faces.astype(np.int64), dtype=torch.long, device=device)
    triangles1 = vertices1[faces1].unsqueeze(dim=0)

    # Load the second mesh
    mesh2 = trimesh.load(file_path2)
    vertices2 = torch.tensor(mesh2.vertices, dtype=torch.float32, device=device)
    faces2 = torch.tensor(mesh2.faces.astype(np.int64), dtype=torch.long, device=device)
    triangles2 = vertices2[faces2].unsqueeze(dim=0)

    # Initialize the BVH tree
    bvh_tree = BVH(max_collisions=max_collisions)

    # Check for collisions between the two meshes
    combined_triangles = torch.cat((triangles1, triangles2), dim=1)
    # print('shape triangles1, triangles2',triangles1.shape,triangles2.shape)
    outputs = bvh_tree(combined_triangles).detach().cpu().numpy().squeeze()
    collisions = outputs[outputs[:, 0] >= 0, :]
    return collisions.shape[0]



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
            mesh_c_mwrm = pv.read(file_c_mwrm)

            # Check for self-intersections in C_mwrm mesh
            self_intersect_c_mwrm, num_triangles_c_mwrm = -1, -1
            if mesh_c_mwrm.is_all_triangles():
                num_triangles_c_mwrm = mesh_c_mwrm.n_faces
                self_intersect_c_mwrm = calculate_self_intersections(file_c_mwrm)

            # Count triangles in BA and CA meshes
            num_triangles_ba = mesh_ba.n_faces if mesh_ba.is_all_triangles() else -1
            num_triangles_ca = mesh_ca.n_faces if mesh_ca.is_all_triangles() else -1

            # Calculate intersections between BA and CA
            intersect_ba_ca = calculate_intersections(file_ba, file_ca)
            total_intersections = calculate_intersections(file_ba, file_ca)
            self_intersections_mesh1 = calculate_self_intersections(file_ba)
            self_intersections_mesh2 = calculate_self_intersections(file_ca)
            intersections_between_meshes = total_intersections - (self_intersections_mesh1 + self_intersections_mesh2)
            
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
                            "Self-Intersection C_mwrm", "Total Triangles C_mwrm", 
                            "Intersections BA-CA", "Total Triangles BA", "Total Triangles CA"]
                    csv_writer.writerow(headers)

                # Write the results to the CSV file
                row = [project, subject_id, hemi, surface_type, hausdorff_dist, 
                    assd_val, chamfer_dist, self_intersect_c_mwrm, 
                    num_triangles_c_mwrm, intersections_between_meshes, num_triangles_ba, num_triangles_ca]
                csv_writer.writerow(row)
            
            # Color the CA mesh based on distance to BA
            colored_ca_mesh = color_mesh_by_distance(mesh_ca, tree_ba)
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