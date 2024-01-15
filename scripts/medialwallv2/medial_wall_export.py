import numpy as np
import pickle
from plyfile import PlyData, PlyElement
import subprocess
import nibabel as nib
import numpy as np
import os

def run_freesurfer_command(command):
    print('Running command:', command)
    try:
        # Set the FreeSurfer SUBJECTS_DIR environment variable
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

# Set the subject directory and the subject ID
subjects_dir = "/data/users2/washbee/speedrun/mwexperiments"
subject_id = '201818'
annotation = 'aparc.a2009s'
hemi = 'lh'

# Step 1: Convert annotation to label files
label_dir = os.path.join(subjects_dir, subject_id, 'label')
os.makedirs(label_dir, exist_ok=True)
run_freesurfer_command(f"mri_annotation2label --subject {subject_id} --hemi {hemi} --annotation {annotation} --outdir {label_dir} --label 0")

# Step 2: Create a binary mask from the medial wall label file
pial_path = os.path.join(subjects_dir, subject_id, 'surf', f'{hemi}.pial')
pial_surface = nib.freesurfer.io.read_geometry(pial_path)
white_path = os.path.join(subjects_dir, subject_id, 'surf', f'{hemi}.white')
white_surface = nib.freesurfer.io.read_geometry(white_path)

medial_wall_label_path = os.path.join(label_dir, f'{hemi}.Unknown.label')  # Adjust if necessary
if not os.path.exists(medial_wall_label_path):
    raise FileNotFoundError(f"Medial wall label file not found: {medial_wall_label_path}")

medial_wall_mask = create_binary_mask(medial_wall_label_path, pial_surface[0].shape[0])


# Function to save vertices to a PLY file
def save_vertices_to_ply(vertices, file_path):
    vertex_array = np.array([(vertex[0], vertex[1], vertex[2]) for vertex in vertices],
                            dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4')])
    el = PlyElement.describe(vertex_array, 'vertex')
    PlyData([el]).write(file_path)

# Function to save vertices to a pickle file
def save_vertices_to_pickle(vertices, file_path):
    with open(file_path, 'wb') as pkl_file:
        pickle.dump(vertices, pkl_file)


# Step 3: Modify the lh.pial surface by removing faces associated with medial wall
vertices, faces = pial_surface
mw_faces = [face for face in faces if np.any(medial_wall_mask[face])]

# Extract unique vertices from mw_faces
unique_vertex_indices = np.unique(np.array(mw_faces).flatten())
mw_vertices = vertices[unique_vertex_indices]


# Save medial wall vertices to PLY and pickle files
ply_path = os.path.join(subjects_dir, subject_id, 'surf', f'{hemi}.pial.medial_wall.ply')
pkl_path = os.path.join(subjects_dir, subject_id, 'surf', f'{hemi}.pial.medial_wall.pkl')

save_vertices_to_ply(mw_vertices, ply_path)
save_vertices_to_pickle(mw_vertices, pkl_path)

print(f"Medial wall vertices saved to {ply_path} and {pkl_path}")

# Step 3: Modify the lh.pial surface by removing faces associated with medial wall
vertices, faces = white_surface
mw_faces = [face for face in faces if np.any(medial_wall_mask[face])]

# Extract unique vertices from mw_faces
unique_vertex_indices = np.unique(np.array(mw_faces).flatten())
mw_vertices = vertices[unique_vertex_indices]


# Save medial wall vertices to PLY and pickle files
ply_path = os.path.join(subjects_dir, subject_id, 'surf', f'{hemi}.white.medial_wall.ply')
pkl_path = os.path.join(subjects_dir, subject_id, 'surf', f'{hemi}.white.medial_wall.pkl')

save_vertices_to_ply(mw_vertices, ply_path)
save_vertices_to_pickle(mw_vertices, pkl_path)

print(f"Medial wall vertices saved to {ply_path} and {pkl_path}")

