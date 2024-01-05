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

medial_wall_label_path = os.path.join(label_dir, f'{hemi}.Unknown.label')  # Adjust if necessary
if not os.path.exists(medial_wall_label_path):
    raise FileNotFoundError(f"Medial wall label file not found: {medial_wall_label_path}")

medial_wall_mask = create_binary_mask(medial_wall_label_path, pial_surface[0].shape[0])

# Step 3: Modify the lh.pial surface by removing faces associated with medial wall
vertices, faces = pial_surface
new_faces = [face for face in faces if not np.any(medial_wall_mask[face])]

# Save the modified surface with removed faces
modified_pial_vertices = vertices.copy()  # Copy vertices as they are
modified_pial_faces = np.array(new_faces)  # New faces without medial wall
modified_pial_path = os.path.join(subjects_dir, subject_id, 'surf', f'{hemi}.pial_no_medial_wall')
nib.freesurfer.io.write_geometry(modified_pial_path, modified_pial_vertices, modified_pial_faces)

print(f"Modified surface saved to {modified_pial_path}")
