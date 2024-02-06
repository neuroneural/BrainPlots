import pyvista as pv
import numpy as np
import os
import itertools

# Base directory where the files are located
base_dir = '.'  # Update this with the actual path

# List of all project names
projects = ['cortexode_euler', 'cortexode_rk4', 'corticalflow', 'corticalflow++', 'deepcsr', 'pialnn', 'topofit', 'vox2cortex']

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
percentile_High = np.percentile(all_distances, 99.5)
percentile_Low = np.percentile(all_distances, .5)

# Custom function to set the camera for specific views
def set_custom_view(plotter, orientation):
    if orientation == 'positive':
        plotter.camera_position = [(0, 0, 335), (0, 0, 0), (0, 1, 0)]
    elif orientation == 'negative':
        plotter.camera_position = [(0, 0, -385), (0, 0, 0), (0, -1, 0)]
    plotter.camera.fov = 30

# Updated function to add combined meshes to a subplot, set camera view, and optionally add a scalar bar and label
def add_combined_meshes_to_subplot(plotter, project, surface, orientation, row_idx, col_idx, with_labels=True):
    mesh_key = (project, surface)
    label = ""  # Initialize label variable

    if mesh_key in meshes:
        actor = plotter.add_mesh(meshes[mesh_key], cmap='inferno_r', clim=[percentile_Low, percentile_High])
        set_custom_view(plotter, orientation)
        if with_labels:
            plotter.add_scalar_bar(title="Distance", label_font_size=10, title_font_size=12, color='black')
        # Update the orientation label based on with_labels flag
        if with_labels:
            orientation_label = "Superior Axial" if orientation == 'positive' else "Inferior Axial"
            label = f"{project}\n{surface.capitalize()} ({orientation_label})"
    else:
        if (project == 'pialnn' and surface == 'white') or (project == 'topofit' and surface == 'pial'):
            label = f"{project}\ndid not\nsupport\n{surface.capitalize()}\nsurfaces\nat time of\ntheir\nPaper."
        else:
            label = f"{project}\n{surface.capitalize()} ({orientation})"
    
    if with_labels:
        label_position = 'upper_right' if col_idx % 2 == 0 else 'upper_left'
        plotter.add_text(label, position=label_position, font_size=10, color='black')
    elif mesh_key not in meshes:
        label_position = 'upper_right' if col_idx % 2 == 0 else 'upper_left'
        plotter.add_text(label, position=label_position, font_size=16, color='red')

# Function to create and save plots
def create_and_save_plots(with_labels):
    plotter = pv.Plotter(shape=(len(surface_types) * len(orientations), len(projects)), off_screen=True)
    plotter.set_background('white')

    for row_idx, (surface, orientation) in enumerate(itertools.product(surface_types, orientations)):
        for col_idx, project in enumerate(projects):
            plotter.subplot(row_idx, col_idx)
            add_combined_meshes_to_subplot(plotter, project, surface, orientation, row_idx, col_idx, with_labels)

    output_file = f"expanded_multi_project_mesh_visualization_{'with_labels' if with_labels else 'without_labels'}.png"
    plotter.screenshot(output_file)
    plotter.show()

# Create and save plots with and without labels
create_and_save_plots(with_labels=True)
create_and_save_plots(with_labels=False)

# Print the 99.5th percentile and the minimum value
print(f"High Scale Max: {percentile_High}, Low Scale Minimum: {percentile_Low}")
# Print the global maximum and minimum distance values
print(f"GlobalMax: {all_distances.max()}, GlobalMin: {all_distances.min()}")
