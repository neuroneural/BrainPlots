import pyvista as pv
import os
import subprocess
import numpy as np
import argparse
from remove_medial_wall import *  # Assuming this has necessary functions like createMedialWallPly
import remove_medial_wall
from medial_wall_util import *
import pickle


# Setting up argparse to handle command line arguments
parser = argparse.ArgumentParser(description="Mesh processing script")
parser.add_argument("--subjects_dir", required=True, help="Directory containing subject folders")
parser.add_argument("--subject_id", required=True, help="Subject ID")
parser.add_argument("--hemi", required=True, help="Hemisphere (lh/rh)")
parser.add_argument("--surfType", required=True, help="Surface type (pial/white)")
parser.add_argument("--project", required=True, help="Project name")

# Parse arguments
args = parser.parse_args()

# Assigning values from command line arguments
subjects_dir = args.subjects_dir
subject_id = args.subject_id
hemi = args.hemi
surfType = args.surfType
project = args.project

fs_gt_path = os.path.join(subjects_dir,subject_id,'surf',f'{hemi}.{surfType}.stl')
file_path_fs = os.path.join(subjects_dir,subject_id,'surf',f'{hemi}.{surfType}')

bash_command = f"mris_convert {file_path_fs} {fs_gt_path}"

print('subject_id',subject_id)

print('bash_command',bash_command)

# Check if the file exists
if not os.path.exists(fs_gt_path):
    # File does not exist, execute the bash command
    subprocess.run(bash_command, shell=True)

meshA = pv.read(fs_gt_path)#Freesurfer
save_mesh(meshA,f"{project}_{subject_id}_A_{hemi}_{surfType}.stl",'stl')

mw_file_path = os.path.join(subjects_dir,subject_id,'surf',f'{hemi}.{surfType}.medial_wall.ply')

# Check if the file exists
if not os.path.exists(mw_file_path):
    createMedialWallPly(mw_file_path)

medial_wall = pv.read(mw_file_path)
medial_wall.save(f"{project}_{subject_id}_mw_{hemi}_{surfType}.ply", binary=True)

# Save the mesh
points = medial_wall.points

print('minuspatch start')
modified_mesh = minuspatch_optimized(meshA, points,K=60)
if isinstance(modified_mesh, pv.UnstructuredGrid):
    modified_mesh = modified_mesh.extract_surface()

modified_mesh.compute_normals(cell_normals=True, point_normals=False, inplace=True)

print('minuspatch end')

save_mesh(modified_mesh,f"{project}_{subject_id}_A_mwrm_{hemi}_{surfType}.stl",'stl')
