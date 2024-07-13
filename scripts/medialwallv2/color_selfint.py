import trimesh
import pyvista as pv
import numpy as np

def color_and_save_mesh(mesh_path, output_path):
    # Load the mesh using trimesh for intersection analysis
    tm_mesh = trimesh.load_mesh(mesh_path)
    
    # Check for self-intersections - this will return a mesh where the intersecting areas are duplicated
    intersection_mesh = tm_mesh.copy()
    intersecting_faces_index = trimesh.repair.broken_faces(intersection_mesh)
    if len(intersecting_faces_index) == 0:
        print("No self-intersecting faces found.")
        return
    
    # Convert trimesh back to PyVista mesh for coloring and saving
    pv_mesh = pv.PolyData(tm_mesh.vertices, np.hstack([np.full((len(tm_mesh.faces), 1), 3), tm_mesh.faces]).ravel())

    # Initialize all faces with a default color (white)
    # face_colors = np.full((pv_mesh.n_faces, 3), [253, 184, 19])  
    face_colors = np.full((pv_mesh.n_faces, 3), [255, 0, 0])  
    #RGB: (253, 184, 19)

    # Color the intersecting faces red
    face_colors[intersecting_faces_index] = [255, 0, 0]  # RGB red

    # Update the mesh with the colored faces
    pv_mesh.cell_data['rgb'] = face_colors

    # Save the colored mesh as a VTK file
    pv_mesh.save(output_path)


# Paths to the meshes
mesh_paths = ['/data/users2/washbee/speedrun/mwexperiments/BrainPlots/scripts/medialwallv2/pialnn/pialnn_223929_C_mwrm_lh_pial.stl',
              '/data/users2/washbee/speedrun/mwexperiments/BrainPlots/scripts/medialwallv2/corticalflow/corticalflow_209329_C_mwrm_lh_pial.stl']  # Update these paths
output_paths = ['pialnn_223929_sint.vtk', 'corticalflow_209329_sint.vtk']  # Update these paths as needed

# Process each mesh
for mesh_path, output_path in zip(mesh_paths, output_paths):
    color_and_save_mesh(mesh_path, output_path)
