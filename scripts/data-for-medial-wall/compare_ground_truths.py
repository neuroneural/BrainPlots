import remove_medial_wall as rmw
import pyvista as pv
import pickle as pkl

pial_fnames = {
    "cortexode": "201818/cortexode/gt.stl",
    "deepcsr": "201818/deepcsr/lh_pial_transformed.stl",
    "pialnn": "201818/pialnn/gt.obj",
    "corticalflow": "201818/corticalflow/gt.stl",
    "vox2cortex": "201818/vox2cortex/lh_pial_transformed.stl",
    "freesurfer": "201818/freesurfer/pial.stl"
    }

# first load freesurfer as our veridical truth
fs_pial = pv.read(pial_fnames["freesurfer"])


plotter = pv.Plotter(shape=(1, len(pial_fnames)))
idx = 0
for file in pial_fnames:
    print(f"working on {file}")
    generated_pial_fname = pial_fnames[file]
    generated_pial = pv.read(generated_pial_fname)
    if file == "pialnn":
        # **CRUCIAL STEP** for PIALNN 
        generated_pial = generated_pial.rotate_x(-90)
    generated_pial = rmw.alignMeshes(fs_pial, generated_pial)
    # Add mesh1 to the first subplot
    plotter.subplot(0, idx)
    plotter.add_text(file, position='upper_edge')
    plotter.add_mesh(generated_pial, color='white')
    plotter.add_mesh(fs_pial, color='g', opacity=0.8)    
    idx += 1
# Link the camera position of all subplots
plotter.link_views()
# Render the plot
plotter.show()
