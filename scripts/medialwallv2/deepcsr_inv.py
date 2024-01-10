import os
import numpy as np
import trimesh

def apply_inverse_transformation(mesh_file, transformation_file, output_file):
    # Load the mesh
    mesh = trimesh.load(mesh_file)

    # Load and invert the transformation matrix
    T = np.loadtxt(transformation_file)
    T_inv = np.linalg.inv(T)

    # Apply the inverse transformation
    # mesh.apply_transform(T_inv)

    # Experimental: Apply transform
    mesh.apply_transform(T)

    # Save the transformed mesh
    mesh.export(output_file)
    print(f"Transformed mesh saved as {output_file}")

# Specify the directory and file names
directory = '/data/users2/washbee/speedrun/deepcsr-preprocessed/201818/'  # Replace with your directory path
lh_pial_file = os.path.join(directory, 'lh_pial.stl')
transformation_file = os.path.join(directory, 'transform_affine.txt')
output_file = os.path.join(directory, 'lh_pial.orig.stl')

# Apply the inverse transformation and save the result
apply_inverse_transformation(lh_pial_file, transformation_file, output_file)
