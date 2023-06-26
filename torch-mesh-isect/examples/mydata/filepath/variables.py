# sample file folders
models = ["freesurfer", 'cortexode', 'corticalflow', 'deepcsr', 'vox2cortex', 'pialnn', 'topofit']

freesurfer = {
    "lh_pial": "/data/users2/llu13/output/cortexode/truth/samples/converted/lh_pial/",
    "lh_white": "/data/users2/llu13/output/cortexode/truth/samples/converted/lh_white/",
}

cortexode = {
    "lh_pial": "/data/users2/llu13/output/cortexode/pred/lh_pial",
    "lh_white": "/data/users2/llu13/output/cortexode/pred/lh_white",
}

corticalflow = {
    "lh_pial": "/data/users2/llu13/output/corticalflow/cfpp/lh_pial",
    "lh_white": "/data/users2/llu13/output/corticalflow/cfpp/lh_white",
}

deepcsr = {
    "lh_pial": "/data/users2/washbee/speedrun/outputdirs/deepcsr-output_dir-timing/checkpoints/test-set/lh_pial",
    "lh_white": "/data/users2/washbee/speedrun/outputdirs/deepcsr-output_dir-timing/checkpoints/test-set/lh_white",
}

pialnn = {"lh_pial": "/data/users2/washbee/speedrun/PialNN_fork/ckpts/eval_bak/lh_pial"}

topofit = {"lh_white": "/data/users2/llu13/output/topofit/truth/pred/lh_white"}

vox2cortex = {
    "lh_pial": "/data/users2/washbee/speedrun/Vox2Cortex_fork/experiments/hcp/test_template_42016_DATASET_NAME/meshes/lh_pial/epoch81",
    "lh_white": "/data/users2/washbee/speedrun/Vox2Cortex_fork/experiments/hcp/test_template_42016_DATASET_NAME/meshes/lh_white/epoch81",
}
