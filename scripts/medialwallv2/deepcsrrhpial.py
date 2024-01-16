import pyvista as pv
from remove_medial_wall import * #should have _alignMeshesAndGetMatrix
import remove_medial_wall
import os
import subprocess
from medial_wall_util import *

# Assuming the files are in a format readable by PyVista, like .ply, .stl, etc.
# Specify the file path and the bash command
subjects_dir ="/home/users/washbee1/mwexperiments/"
subject_id = "201818"
hemi = 'rh'
surfType = "pial"#pial or white
project = 'deepcsr'
file_path = os.path.join(subjects_dir,subject_id,"surf",f"{hemi}.{surfType}.stl")
file_path_fs = os.path.join(subjects_dir,subject_id,"surf",f"{hemi}.{surfType}")
bash_command = f"mris_convert {file_path_fs} {file_path}"

# Check if the file exists
if not os.path.exists(file_path):
    # File does not exist, execute the bash command
    subprocess.run(bash_command, shell=True)

proj_gt_path = os.path.join('/data/users2/washbee/speedrun/deepcsr-preprocessed/', subject_id, f'{hemi}_{surfType}.stl')
source_mesh = pv.read(proj_gt_path)#project's transformed ground truth
save_mesh(source_mesh,f"{project}_{subject_id}_B_{hemi}_{surfType}.stl",'stl')

fs_gt_path= os.path.join(subjects_dir,subject_id,'surf',f'{hemi}.{surfType}.stl')
target_mesh = pv.read(fs_gt_path)#Freesurfer
save_mesh(target_mesh,f"{project}_{subject_id}_A_{hemi}_{surfType}.stl",'stl')

centered_source, centering_matrix = alignCentersAndGetMatrix(target_mesh, source_mesh)

scaled_source, scaling_matrix = scaleToMatchBoundingBox(centered_source, target_mesh)

aligned_source, icp_matrix = remove_medial_wall._alignMeshesAndGetMatrix(target_mesh, scaled_source, rigid=False)#maybe needs to be True

print('aligned source type',type(aligned_source))

save_mesh(aligned_source,f"{project}_{subject_id}_BA_{hemi}_{surfType}.stl",'stl')

combined_transformation_matrix = icp_matrix @ scaling_matrix @ centering_matrix #correct order? 

pred_path = os.path.join('/data/users2/washbee/speedrun/outputdirs/deepcsr-output_dir/checkpoints/predict_debug/',
                        f'{subject_id}_{hemi}_{surfType}.stl')
third_mesh = pv.read(pred_path)
save_mesh(third_mesh,f"{project}_{subject_id}_C_{hemi}_{surfType}.stl",'stl')

transformed_third_mesh = third_mesh.copy().transform(combined_transformation_matrix)
save_mesh(aligned_source,f"{project}_{subject_id}_CA_{hemi}_{surfType}.stl",'stl')

meshA = pv.read(pred_path)  # Replace with the path to your mesh file

mw_file_path = os.path.join(subjects_dir,subject_id,'surf',f'{hemi}.{surfType}.medial_wall.ply')

# Check if the file exists
if not os.path.exists(mw_file_path):
    createMedialWallPly(mw_file_path)

medial_wall = pv.read(mw_file_path)
medial_wall.save(f"{project}_{subject_id}_mw_{hemi}_{surfType}.ply", binary=True)

transformed_medial_wall = medial_wall.copy().transform(np.linalg.inv(combined_transformation_matrix))
transformed_medial_wall.save(f"{project}_{subject_id}_invmw_{hemi}_{surfType}.ply", binary=True)

# Recalculate the normals
# transformed_medial_wall.compute_normals(cell_normals=True, point_normals=False, inplace=True)

# Save the mesh
points = transformed_medial_wall.points

print('minuspatch start')
modified_mesh = minuspatch_optimized(meshA, points,K=60)
if isinstance(modified_mesh, pv.UnstructuredGrid):
    modified_mesh = modified_mesh.extract_surface()

modified_mesh.compute_normals(cell_normals=True, point_normals=False, inplace=True)

print('minuspatch end')

save_mesh(modified_mesh,f"{project}_{subject_id}_C_mwrm_{hemi}_{surfType}.stl",'stl')
