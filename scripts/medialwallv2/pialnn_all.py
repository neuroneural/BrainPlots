import pyvista as pv
import os
import subprocess
import numpy as np
import argparse
from remove_medial_wall import *  # Assuming this has necessary functions like createMedialWallPly
import remove_medial_wall
from medial_wall_util import *
import pickle

def rotation_matrix_x(angle_rad):
    identity_matrix = np.identity(4)
    identity_matrix[0:3,0:3] = np.array([[1, 0, 0],
                     [0, np.cos(angle_rad), -np.sin(angle_rad)],
                     [0, np.sin(angle_rad), np.cos(angle_rad)]])
    return identity_matrix

def rotation_matrix_y(angle_rad):
    identity_matrix = np.identity(4)
    identity_matrix[0:3,0:3] = np.array([[np.cos(angle_rad), 0, np.sin(angle_rad)],
                     [0, 1, 0],
                     [-np.sin(angle_rad), 0, np.cos(angle_rad)]])
    return identity_matrix

def rotation_matrix_z(angle_rad):
    identity_matrix = np.identity(4)
    identity_matrix[0:3,0:3] = np.array([[np.cos(angle_rad), -np.sin(angle_rad), 0],
                     [np.sin(angle_rad), np.cos(angle_rad), 0],
                     [0, 0, 1]])
    return identity_matrix

# Setting up argparse to handle command line arguments
parser = argparse.ArgumentParser(description="Mesh processing script")
parser.add_argument("--subjects_dir", required=True, help="Directory containing subject folders")
parser.add_argument("--subject_id", required=True, help="Subject ID")
parser.add_argument("--hemi", required=True, help="Hemisphere (lh/rh)")
parser.add_argument("--surfType", required=True, help="Surface type (pial/white)")
parser.add_argument("--project", required=True, help="Project name")
parser.add_argument("--project_gt_base_path", required=True, help="Base path for project's ground truth")
parser.add_argument("--project_pred_base_path", required=True, help="Base path for project's predictions")

# Parse arguments
args = parser.parse_args()

# Assigning values from command line arguments
subjects_dir = args.subjects_dir
subject_id = args.subject_id
hemi = args.hemi
surfType = args.surfType
project = args.project
project_gt_base_path = args.project_gt_base_path
project_pred_base_path = args.project_pred_base_path

proj_gt_path = os.path.join(project_gt_base_path, f'pialnn_{hemi}_{subject_id}_gt.stl')
fs_gt_path = os.path.join(subjects_dir,subject_id,'surf',f'{hemi}.{surfType}.stl')
file_path_fs = os.path.join(subjects_dir,subject_id,'surf',f'{hemi}.{surfType}')

bash_command = f"mris_conxvert {file_path_fs} {fs_gt_path}"

print('subject_id',subject_id)

print('bash_command',bash_command)

# Check if the file exists
if not os.path.exists(fs_gt_path):
    # File does not exist, execute the bash command
    subprocess.run(bash_command, shell=True)

source_mesh = pv.read(proj_gt_path)#project's transformed ground truth
save_mesh(source_mesh,f"{project}_{subject_id}_B_{hemi}_{surfType}.stl",'stl')

target_mesh = pv.read(fs_gt_path)#Freesurfer
save_mesh(target_mesh,f"{project}_{subject_id}_A_{hemi}_{surfType}.stl",'stl')

rot = rotation_matrix_x(np.pi / -2.0)
source_mesh_rot = source_mesh.copy().transform(rot)
save_mesh(source_mesh_rot,f"{project}_{subject_id}_B_rotmx_{hemi}_{surfType}.stl",'stl')

centered_source, centering_matrix = alignCentersAndGetMatrix(target_mesh, source_mesh_rot)

scaled_source, scaling_matrix = scaleToMatchBoundingBox(centered_source, target_mesh)

aligned_source, icp_matrix = remove_medial_wall._alignMeshesAndGetMatrix(target_mesh, scaled_source, rigid=False)#maybe needs to be True

print('aligned source type',type(aligned_source))

save_mesh(aligned_source,f"{project}_{subject_id}_BA_{hemi}_{surfType}.stl",'stl') 

combined_transformation_matrix = icp_matrix @ scaling_matrix @ centering_matrix @ rot #correct order? 

############# unit test for transformation matrix being equivalent to the steps to obtain it
# test_mesh = source_mesh.copy().transform(combined_transformation_matrix)
# t_p = cKDTree(test_mesh.points)
# t_a = cKDTree(aligned_source.points)
# d1, _ = t_a.query(t_p.data)
# d2, _ = t_p.query(t_a.data)
# hd = max(np.max(d1), np.max(d2))
# print('hd',hd)
# assert hd < .0001
#############

# Save the combined transformation matrix as a pickle file
matrix_filename = f"{project}_{subject_id}_{hemi}_{surfType}_transformation_matrix.pkl"
with open(matrix_filename, 'wb') as matrix_file:
    pickle.dump(combined_transformation_matrix, matrix_file)

pred_path = os.path.join(project_pred_base_path,
    f'pialnn_{hemi}_{subject_id}.stl')

third_mesh = pv.read(pred_path)
save_mesh(third_mesh,f"{project}_{subject_id}_C_{hemi}_{surfType}.stl",'stl')

transformed_third_mesh = third_mesh.copy().transform(combined_transformation_matrix)
save_mesh(transformed_third_mesh,f"{project}_{subject_id}_CA_{hemi}_{surfType}.stl",'stl')

meshA = pv.read(pred_path)  # Replace with the path to your mesh file

mw_file_path = os.path.join(subjects_dir,subject_id,'surf',f'{hemi}.{surfType}.medial_wall.ply')

# Check if the file exists
if not os.path.exists(mw_file_path):
    createMedialWallPly(mw_file_path)

medial_wall = pv.read(mw_file_path)
medial_wall.save(f"{project}_{subject_id}_mw_{hemi}_{surfType}.ply", binary=True)

transformed_medial_wall = medial_wall.copy().transform(np.linalg.inv(combined_transformation_matrix))
transformed_medial_wall.save(f"{project}_{subject_id}_invmw_{hemi}_{surfType}.ply", binary=True)

# Save the mesh
points = transformed_medial_wall.points

print('minuspatch start')
modified_mesh = minuspatch_optimized(meshA, points,K=60)
if isinstance(modified_mesh, pv.UnstructuredGrid):
    modified_mesh = modified_mesh.extract_surface()

modified_mesh.compute_normals(cell_normals=True, point_normals=False, inplace=True)

print('minuspatch end')

save_mesh(modified_mesh,f"{project}_{subject_id}_C_mwrm_{hemi}_{surfType}.stl",'stl')
