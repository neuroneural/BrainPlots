import pyvista as pv
import numpy as np

# File paths for the pial and white meshes
pial_files = [
    "deepcsr_200008_CA_lh_pial_distanceMesh.vtk",
    "deepcsr_200008_CA_rh_pial_distanceMesh.vtk"
]
white_files = [
    "deepcsr_200008_CA_lh_white_distanceMesh.vtk",
    "deepcsr_200008_CA_rh_white_distanceMesh.vtk"
]

# Load the pial and white meshes
pial_meshes = [pv.read(file) for file in pial_files]
white_meshes = [pv.read(file) for file in white_files]

# Combine all meshes for global min/max scaling
all_meshes = pial_meshes + white_meshes

# Calculate the global 99.5th percentile for the color scale
all_distances = np.concatenate([mesh.point_data['Distance'] for mesh in all_meshes])
percentile_99_5 = np.percentile(all_distances, 99.5)

# Plotter setup for interactive visualization
plotter = pv.Plotter(shape=(4, 2), off_screen=True)
plotter.set_background('white')  # Set the background color to white

# Function to add meshes to a subplot
def add_meshes_to_subplot(plotter, subplot_idx, meshes, view_orientation):
    for mesh in meshes:
        mesh.set_active_scalars('Distance')
        plotter.add_mesh(mesh, cmap='inferno_r', clim=[all_distances.min(), percentile_99_5])
    getattr(plotter, f'view_{view_orientation}')()
    # Add a scalar bar for each subplot
    # plotter.add_scalar_bar(title="Distance", vertical=True, 
    #                        title_font_size=20, label_font_size=20, 
    #                        color='black', background_color='white')

# Define the orientations for the subplots
orientations = ['xy', 'xz', 'yx', 'yz']

# Add meshes to each subplot based on the defined orientations
for row, orientation in enumerate(orientations):
    plotter.subplot(row, 0)
    add_meshes_to_subplot(plotter, row*2, pial_meshes, orientation)
    plotter.subplot(row, 1)
    add_meshes_to_subplot(plotter, row*2+1, white_meshes, orientation)

# Save the visualization as a PNG file
output_png = "mesh_visualization.png"
plotter.screenshot(output_png)

# Show the interactive plotter window
plotter.show()
