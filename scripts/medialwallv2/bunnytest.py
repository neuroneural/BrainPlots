import open3d as o3d
import numpy as np

def create_and_save_bunny():
    # Load the Stanford Bunny mesh
    bunny = o3d.data.BunnyMesh()
    mesh = o3d.io.read_triangle_mesh(bunny.path)
    mesh.compute_vertex_normals()

    # Save the original mesh as STL
    original_stl_path = "stanford_bunny_original.stl"
    o3d.io.write_triangle_mesh(original_stl_path, mesh)

    # Apply non-uniform scaling
    scale_factors = np.array([1.5, 1.2, 1.3])  # Different scale factors for x, y, and z
    vertices = np.asarray(mesh.vertices)
    scaled_vertices = vertices * scale_factors
    mesh.vertices = o3d.utility.Vector3dVector(scaled_vertices)

    # Apply rotation
    rotation = mesh.get_rotation_matrix_from_xyz((np.pi / 6, np.pi / 6, np.pi / 6))
    mesh.rotate(rotation, center=mesh.get_center())

    # Compute normals again after transformation
    mesh.compute_vertex_normals()

    # Save the transformed mesh as STL
    transformed_stl_path = "stanford_bunny_transformed.stl"
    o3d.io.write_triangle_mesh(transformed_stl_path, mesh)

    return original_stl_path, transformed_stl_path

# Run the function and print the file paths
original_bunny, transformed_bunny = create_and_save_bunny()
print(f"Original Bunny Mesh saved to: {original_bunny}")
print(f"Transformed Bunny Mesh saved to: {transformed_bunny}")
