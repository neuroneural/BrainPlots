import pyvista as pv

# File paths for the meshes
files = [
    "deepcsr_200008_CA_lh_pial_distanceMesh.vtk",
    "deepcsr_200008_CA_rh_pial_distanceMesh.vtk",
    "deepcsr_200008_CA_lh_white_distanceMesh.vtk",
    "deepcsr_200008_CA_rh_white_distanceMesh.vtk"
]

# Load the meshes and store them in a list
meshes = [pv.read(file) for file in files]

# Find the global min and max across all meshes for consistent scaling
global_min = min([mesh.point_data['Distance'].min() for mesh in meshes])
global_max = max([mesh.point_data['Distance'].max() for mesh in meshes])

# Plotter setup for interactive visualization
plotter = pv.Plotter(shape=(2, 2), off_screen=False)

# Add each mesh to the plotter
for i, mesh in enumerate(meshes):
    # Apply the 'inferno' colormap based on the 'Distance' scalar
    scalar_bar_args = {'title': "Distance"} if i == 0 else {}
    mesh.set_active_scalars('Distance')
    plotter.subplot(i // 2, i % 2)
    plotter.add_mesh(mesh, cmap='inferno', clim=[global_min, global_max], scalar_bar_args=scalar_bar_args)

# Show the interactive plotter window
plotter.show()
