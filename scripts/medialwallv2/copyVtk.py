import os
import shutil

# Define the list of project folders
project_folders = sorted([
    'pialnn', 'topofit',
    'cortexode_rk4', 'deepcsr',
    'cortexode_euler', 'corticalflow','corticalflow++', 'freesurfer',
    'vox2cortex'
])

# Define the target folder where you want to copy the VTK files
target_folder = './distanceMeshes/'

# Define the subject ID you are looking for
subject_id = '201818'

# Iterate through each project folder
for folder in project_folders:
    # Iterate through files in the project folder
    for filename in os.listdir(folder):
        # Check if the file contains the subject ID and is a VTK file
        if subject_id in filename and filename.endswith('.vtk'):
            # Create the full path to the VTK file
            vtk_file_path = os.path.join(folder, filename)
            
            # Modify filename if it's from 'cortexode_rk4' or 'cortexode_euler' folder
            if folder in ['cortexode_rk4', 'cortexode_euler']:
                # Remove 'cortexode_' if it's present in the filename
                new_filename = filename.replace('cortexode_', '')
                # Prefix with the folder name
                new_filename = folder + '_' + new_filename
            else:
                new_filename = filename

            # Define the target file path
            target_file_path = os.path.join(target_folder, new_filename)

            # Copy the VTK file to the target folder with the new name
            shutil.copy(vtk_file_path, target_file_path)
