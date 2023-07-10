import numpy as np
import trimesh

# Load the STL/PLY mesh
mesh = trimesh.load_mesh("lh_pial.ply")

# Load the 4x4 affine transform matrix from file and invert it
affine_transform = np.loadtxt("transform_affine.txt")
inverse_transform = np.linalg.inv(affine_transform)

# Apply the inverse transform
mesh.apply_transform(affine_transform)

# Save the transformed mesh
mesh.export("lh_pial_transformed.stl")