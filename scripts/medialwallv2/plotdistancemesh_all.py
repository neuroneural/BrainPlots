import pyvista as pv
import numpy as np
import os
import itertools

# Base directory where the files are located
base_dir = '.'  # Update this with the actual path

# List of all project names
projects = ['cortexode_euler', 'cortexode_rk4', 'corticalflow', 'deepcsr', 'pialnn', 'topofit', 'vox2cortex']

# Define surface types and orientations
surface_types = ['pial', 'white']
orientations = ['positive', 'negative']

def generate_file_paths(project, surface, hemisphere):
    subject_id = '201818'
    return f"{project}_{subject_id}_CA_{hemisphere}_{surface}_distanceMesh.vtk"

# Load the meshes into a structured dictionary
meshes = {}
distance_arrays = []
for project in projects:
    for surface in surface_types:
        combined_mesh = None
        for hemisphere in ['lh', 'rh']:
            file_path = os.path.join(base_dir, generate_file_paths(project, surface, hemisphere))
            if os.path.exists(file_path):
                mesh = pv.read(file_path)
                combined_mesh = mesh if combined_mesh is None else combined_mesh + mesh
                distance_arrays.append(mesh.point_data['Distance'])

        if combined_mesh:
            meshes[(project, surface)] = combined_mesh

# Concatenate all distances and calculate percentile
all_distances = np.concatenate(distance_arrays)
percentile_99_5 = np.percentile(all_distances, 99.5)

# Custom function to set the camera for specific views
def set_custom_view(plotter, orientation):
    if orientation == 'positive':
        plotter.camera_position = [(0, 0, 550), (0, 0, 0), (0, 1, 0)]
    elif orientation == 'negative':
        plotter.camera_position = [(0, 0, -550), (0, 0, 0), (0, -1, 0)]
    plotter.camera.fov = 30

# Create the plotter with the expanded grid size
plotter = pv.Plotter(shape=(len(surface_types) * len(orientations), len(projects)), off_screen=True)
plotter.set_background('white')

# Function to add combined meshes to a subplot and label them
def add_combined_meshes_to_subplot(plotter, project, surface, orientation, row_idx, col_idx):
    mesh_key = (project, surface)
    if mesh_key in meshes:
        plotter.add_mesh(meshes[mesh_key], cmap='inferno_r', clim=[0, percentile_99_5])
        set_custom_view(plotter, orientation)
        label = f"{project}\n{surface.capitalize()} ({orientation})"
    else:
        # If the mesh is missing, add a label indicating this
        label = f"{project}\n{surface.capitalize()} surface\nmissing ({orientation})"
    
    # Determine label position
    label_position = 'lower_right' if col_idx % 2 == 0 else 'upper_left'
    plotter.add_text(label, position=label_position, font_size=10, color='black')

# Add the combined meshes and labels to the plotter
for row_idx, (surface, orientation) in enumerate(itertools.product(surface_types, orientations)):
    for col_idx, project in enumerate(projects):
        plotter.subplot(row_idx, col_idx)
        add_combined_meshes_to_subplot(plotter, project, surface, orientation, row_idx, col_idx)

# Save and show the plot
output_png = "expanded_multi_project_mesh_visualization.png"
plotter.screenshot(output_png)
plotter.show()
