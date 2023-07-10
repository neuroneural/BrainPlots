import remove_medial_wall as rmw
import pyvista as pv
import pickle as pkl

pial_fnames = {
    "cortexode": "201818/cortexode/pp.stl",
    "deepcsr": "201818/deepcsr/pp.stl",
    "corticalflow": "201818/corticalflow/pp.stl",
    "pialnn": "201818/pialnn/pp.stl",
    "vox2cortex": "201818/vox2cortex/pp.stl",
    "freesurfer": "201818/freesurfer/pial.stl"
    }
mwall_points = 'medialwall-points.pkl'
K = 20 # hearest neighbors to remove

fs_pial = pv.read(pial_fnames["freesurfer"])

with open(mwall_points,'rb') as f:
    wall = pkl.load(f)
fs_mwall_removed = rmw.minuspatch(fs_pial, wall, K=K)


heatmaps = {}
mindist = 10000000
maxdist = -10000000
for file in pial_fnames:
    print(f"working on {file}")
    generated_pial_fname = pial_fnames[file]
    generated_pial = pv.read(generated_pial_fname)
    if file == "pialnn":
        # **CRUCIAL STEP** for PIALNN
        generated_pial = generated_pial.rotate_x(-90)
    generated_pial = rmw.alignMeshes(fs_pial,
        generated_pial,
        scale=False)
    mwall_removed = rmw.minuspatch(generated_pial, wall, K=K)

    # Get the cell centers of both meshes
    centers_a = fs_mwall_removed.cell_centers().points
    centers_b = mwall_removed.cell_centers().points
    # Use a KDTree to quickly find the nearest point in mesh_a for each point in freesurfer mesh
    tree = rmw.KDTree(centers_a)
    distances, _ = tree.query(centers_b)
    # Add the distances to fs mesh as a field array
    mwall_removed["Distances"] = distances
    heatmaps[file] = mwall_removed
    mindist = min([mindist, distances.min()])
    maxdist = max([maxdist, distances.max()])

plotter = pv.Plotter(shape=(1, len(pial_fnames)))
idx = 0
for file in heatmaps:
    # Add mesh1 to the first subplot
    plotter.subplot(0, idx)
    plotter.add_text(file, position='upper_edge')
    plotter.add_mesh(heatmaps[file],
                     scalars="Distances",
                     cmap="inferno",
                     clim=[mindist,maxdist])
    idx += 1
# Link the camera position of all subplots Looks like this command
# also links the color limits and the elaborate procedire of
# identifying the global color limit may not be required.
plotter.link_views()
# Render the plot
plotter.show()
