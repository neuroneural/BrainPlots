import pyvista as pv
import remove_medial_wall as rmw
import numpy as np


# Load the original and transformed bunny STL files
source_mesh = pv.read('stanford_bunny_original.stl')
target_mesh = pv.read('stanford_bunny_transformed.stl')

# Align the source mesh (transformed bunny) to the target mesh (original bunny)
aligned_source_mesh, _T_array = rmw.alignMeshesWithInitialGuess(target_mesh, source_mesh)

output_path = 'AB_mesh.stl'
aligned_source_mesh.save(output_path)
print(f"Saved transformed mesh to {output_path}")

# Load your mesh
source_mesh = pv.read('stanford_bunny_original.stl')  # Replace with your transformed bunny file path
target_mesh = pv.read('stanford_bunny_transformed.stl')  # Replace with your original bunny file path

# Suppose you have the translation_matrix and icp_matrix from the alignment process
# Apply transformations
source_mesh = rmw.apply_transformations(source_mesh, _T_array)

# Save the transformed mesh as an STL file
output_path = "AB2_mesh.stl"
source_mesh.save(output_path, binary=True)
print(f"Saved transformed mesh to {output_path}")

########################################################

# Load the original and transformed bunny STL files
source_mesh = pv.read('stanford_bunny_transformed.stl')  # Replace with your transformed bunny file path
target_mesh = pv.read('stanford_bunny_original.stl')  # Replace with your original bunny file path

# Align the source mesh (transformed bunny) to the target mesh (original bunny)
aligned_source_mesh, _T_array = rmw.alignMeshesWithInitialGuess(target_mesh, source_mesh)

# Now, scaled_source_mesh is the transformed bunny, aligned and scaled to match the original bunny
# You can visualize, analyze, or save the scaled mesh
output_path = 'BA_mesh.stl'
aligned_source_mesh.save(output_path)
print(f"Saved transformed mesh to {output_path}")

# Load your mesh
source_mesh = pv.read('stanford_bunny_transformed.stl')  # Replace with your transformed bunny file path
target_mesh = pv.read('stanford_bunny_original.stl')  # Replace with your original bunny file path

# Suppose you have the translation_matrix and icp_matrix from the alignment process
# Apply transformations
source_mesh = rmw.apply_transformations(source_mesh, _T_array)

# Save the transformed mesh as an STL file
output_path = "BA2_mesh.stl"
source_mesh.save(output_path, binary=True)
print(f"Saved transformed mesh to {output_path}")