import numpy as np
from scipy.spatial import cKDTree
import os
from plyfile import PlyData, PlyElement

def load_ply_points(ply_path):
    plydata = PlyData.read(ply_path)
    points = np.vstack([plydata['vertex']['x'], plydata['vertex']['y'], plydata['vertex']['z']]).T
    return points

def load_ply_mesh(ply_path):
    plydata = PlyData.read(ply_path)
    vertices = np.vstack([plydata['vertex']['x'], plydata['vertex']['y'], plydata['vertex']['z']]).T
    faces = np.vstack(plydata['face']['vertex_indices'])
    return vertices, faces

def apply_inverse_transform(vertices, transform_matrix):
    # Apply inverse transformation to each vertex
    return np.dot(vertices, transform_matrix[:3, :3].T) + transform_matrix[:3, 3]

def nearest_neighbor_faces(vertices, faces, points, num_faces_per_point):
    face_centroids = np.mean(vertices[faces], axis=1)
    kd_tree = cKDTree(face_centroids)

    face_indices = set()
    for point in points:
        _, indices = kd_tree.query(point, k=num_faces_per_point)
        face_indices.update(indices)

    # Filter out invalid indices
    valid_indices = set(index for index in face_indices if index != np.inf and index < len(faces))
    return valid_indices

def remove_faces(vertices, faces, face_indices_to_remove):
    return vertices, np.delete(faces, list(face_indices_to_remove), axis=0)

def save_ply_mesh(ply_path, vertices, faces):
    vertices_tuple = np.array([(vertex[0], vertex[1], vertex[2]) for vertex in vertices], dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4')])
    faces_tuple = np.array([(face,) for face in faces], dtype=[('vertex_indices', 'i4', (3,))])
    el_vert = PlyElement.describe(vertices_tuple, 'vertex')
    el_face = PlyElement.describe(faces_tuple, 'face')
    PlyData([el_vert, el_face], text=True).write(ply_path)

# Paths
subjects_dir = "/data/users2/washbee/speedrun/mwexperiments/201818"
transform_affine_path = "/data/users2/washbee/speedrun/Vox2Cortex_fork/CSR_data/201818/transform_affine.txt"
source_ply_path = os.path.join('/data/users2/washbee/speedrun/Vox2Cortex_fork/experiments/hcp/test_template_42016_DATASET_NAME/meshes/lh_pial/201818_epoch76_struc2_meshpred.ply')
medial_wall_ply_path = os.path.join(subjects_dir, 'surf', 'lh.medial_wall.ply')
output_path = os.path.join(subjects_dir, 'surf', 'lh_pial.v2c_modified.ply')

# Load transformation matrix and compute its inverse
transform_matrix = np.linalg.inv(np.loadtxt(transform_affine_path))

# Load PLY mesh and apply inverse transformation
vertices, faces = load_ply_mesh(source_ply_path)
vertices = apply_inverse_transform(vertices, transform_matrix)

# Load medial wall points from PLY file
medial_wall_points = load_ply_points(medial_wall_ply_path)

# Number of nearest neighbor faces per point
num_faces_per_point = 30  # Default value, adjust as needed

# Find nearest neighbor faces in the PLY mesh for medial wall points
face_indices_to_remove = nearest_neighbor_faces(vertices, faces, medial_wall_points, num_faces_per_point)

# Remove the identified faces from the PLY mesh
modified_vertices, modified_faces = remove_faces(vertices, faces, face_indices_to_remove)

# Save the modified PLY mesh
save_ply_mesh(output_path, modified_vertices, modified_faces)
print(f"Modified PLY mesh saved to {output_path}")
