import pyvista as pv
from remove_medial_wall import * #should have _alignMeshesAndGetMatrix
import remove_medial_wall
# Assuming the files are in a format readable by PyVista, like .ply, .stl, etc.
source_mesh = pv.read('/data/users2/washbee/speedrun/deepcsr-preprocessed/201818/lh_white.stl')#transformed ground truth
save_mesh(source_mesh,"B.stl",'stl')

target_mesh = pv.read('/home/users/washbee1/mwexperiments/201818/surf/lh.white.stl')#Freesurfer
save_mesh(target_mesh,"A.stl",'stl')

centered_source, centering_matrix = alignCentersAndGetMatrix(target_mesh, source_mesh)

scaled_source, scaling_matrix = scaleToMatchBoundingBox(centered_source, target_mesh)

aligned_source, icp_matrix = remove_medial_wall._alignMeshesAndGetMatrix(target_mesh, scaled_source, rigid=False)#maybe needs to be True

print('aligned source type',type(aligned_source))

save_mesh(aligned_source,"BA.stl",'stl')


combined_transformation_matrix = icp_matrix @ scaling_matrix @ centering_matrix #correct order? 

third_mesh = pv.read('/data/users2/washbee/speedrun/outputdirs/deepcsr-output_dir/checkpoints/predict_debug/201818_lh_white.stl')
save_mesh(third_mesh,"C.stl",'stl')

transformed_third_mesh = third_mesh.copy().transform(combined_transformation_matrix)
save_mesh(aligned_source,"CA.stl",'stl')


# # Saving the matrix
# with open('transformation_matrix.pkl', 'wb') as f:
#     pkl.dump(combined_transformation_matrix, f)

# # Loading and applying the matrix to another mesh
# with open('transformation_matrix.pkl', 'rb') as f:
#     transformation_matrix = pkl.load(f)

# another_mesh = pv.read('path_to_another_mesh_file')
# transformed_another_mesh = another_mesh.copy().transform(transformation_matrix)

#'/home/users/washbee1/mwexperiments/201818/surf/lh.pial.medial_wall.ply'
meshA = pv.read('/data/users2/washbee/speedrun/outputdirs/deepcsr-output_dir/checkpoints/predict_debug/201818_lh_white.stl')  # Replace with the path to your mesh file

medial_wall = pv.read('/home/users/washbee1/mwexperiments/201818/surf/lh.white.medial_wall.ply')
medial_wall.save("mw_white.ply", binary=True)

transformed_medial_wall = medial_wall.copy().transform(np.linalg.inv(combined_transformation_matrix))
transformed_medial_wall.save("invmw.ply", binary=True)

# Recalculate the normals
# transformed_medial_wall.compute_normals(cell_normals=True, point_normals=False, inplace=True)

# Save the mesh
points = transformed_medial_wall.points

print('minuspatch start')
modified_mesh = minuspatch_optimized(meshA, points,K=60)
if isinstance(modified_mesh, pv.UnstructuredGrid):
    modified_mesh = modified_mesh.extract_surface()

modified_mesh.compute_normals(cell_normals=True, point_normals=False, inplace=True)

print('minuspatch end')

save_mesh(modified_mesh,"C_mwrm.stl",'stl')
