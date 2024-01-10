import subprocess
import nibabel as nib
import numpy as np
import os
from stl import mesh
from plyfile import PlyData, PlyElement

def run_freesurfer_command(command):
    try:
        subjects_dir = "/data/users2/washbee/speedrun/mwexperiments"
        complete_command = f"source $FREESURFER_HOME/SetUpFreeSurfer.sh; export SUBJECTS_DIR={subjects_dir}; {command}"
        subprocess.run(complete_command, check=True, shell=True, executable="/bin/bash")
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        raise e

def create_binary_mask(label_path, num_vertices):
    label = nib.freesurfer.read_label(label_path)
    mask = np.zeros(num_vertices, dtype=bool)
    mask[label] = True
    return mask

subjects_dir = "/data/users2/washbee/speedrun/mwexperiments"
subject_id = '201818'
hemi = 'lh'

# Load the white surface
white_path = os.path.join(subjects_dir, subject_id, 'surf', f'{hemi}.white')
white_surface = nib.freesurfer.io.read_geometry(white_path)

# Load the medial wall label file
label_dir = os.path.join(subjects_dir, subject_id, 'label')
medial_wall_label_path = os.path.join(label_dir, f'{hemi}.Unknown.label')
if not os.path.exists(medial_wall_label_path):
    raise FileNotFoundError(f"Medial wall label file not found: {medial_wall_label_path}")

# Create a binary mask for the medial wall
medial_wall_mask = create_binary_mask(medial_wall_label_path, white_surface[0].shape[0])

# Extract medial wall points
medial_wall_points = white_surface[0][medial_wall_mask]

# Save medial wall points as a PLY file (point cloud)
ply_path = os.path.join(subjects_dir, subject_id, 'surf', f'{hemi}.medial_wall.ply')
vertices_tuple = np.array([(point[0], point[1], point[2]) for point in medial_wall_points], dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4')])
el = PlyElement.describe(vertices_tuple, 'vertex')
PlyData([el]).write(ply_path)

print(f"Medial wall points saved as PLY file to {ply_path}")
