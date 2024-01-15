import remove_medial_wall as rmw
import pyvista as pv
import pickle as pkl
import os

subjects_dir = "/data/users2/washbee/speedrun/mwexperiments"
subject_id = '201818'
hemi = 'lh'

fs_pial_path = os.path.join(subjects_dir, subject_id, 'surf', f'{hemi}.pial.stl')

pial_fnames = {
    "deepcsr": "/data/users2/washbee/speedrun/outputdirs/deepcsr-output_dir-timing/checkpoints/test-set/201818_lh_pial.stl",
    "pialnn": "/data/users2/washbee/speedrun/PialNN_fork/ckpts/eval_subj_id/pialnn_mesh_eval_lh_subject_201818.obj",
    "cortexode": "/data/users2/washbee/speedrun/CortexODE_fork/ckpts/reviewpapertest/adni_lh_201818.pial.stl",#adni worked best hcp didn't work. 
    "vox2cortex": "/data/users2/washbee/speedrun/Vox2Cortex_fork/experiments/hcp/test_template_42016_DATASET_NAME/meshes/lh_pial/201818_epoch76_struc2_meshpred.ply",
    "topofit": "/data/users2/washbee/speedrun/Vox2Cortex_fork/experiments/hcp/test_template_42016_DATASET_NAME/meshes/lh_pial/201818_epoch76_struc2_meshpred.ply",
    "freesurfer": fs_pial_path
}

mwall_points = '/data/users2/washbee/speedrun/mwexperiments/201818/surf/lh.pial.medial_wall.pkl'
K = 20  # Nearest neighbors to remove

fs_pial = pv.read(pial_fnames["freesurfer"])
with open(mwall_points, 'rb') as f:
    wall = pkl.load(f)

# Iterate over each pial file
for file, path in pial_fnames.items():
    print(f"Working on {file}")
    generated_pial = pv.read(path)
    if file == "pialnn":
        # **CRUCIAL STEP** for PIALNN
        generated_pial = generated_pial.rotate_x(-90)
    generated_pial = rmw.alignMeshes(fs_pial, generated_pial, scale=False)
    mwall_removed = rmw.minuspatch(generated_pial, wall, K=K)
    
    # Save the mesh without medial wall to the current working directory
    output_filename = os.path.join(os.getcwd(), f'{file}_no_medial_wall.ply')
    mwall_removed.save(output_filename)
    print(f"Saved mesh without medial wall to {output_filename}")
