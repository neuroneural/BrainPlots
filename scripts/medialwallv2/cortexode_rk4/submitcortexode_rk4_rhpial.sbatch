#!/bin/bash
#SBATCH -n 1
#SBATCH -c 2
#SBATCH --mem=5g
#SBATCH -p qTRDGPU
#SBATCH -t 1-00:00
#SBATCH -J mwrmctoderp
#SBATCH -e jobs/error%A_%a.err
#SBATCH -o jobs/out%A_%a.out
#SBATCH -A psy53c17
#SBATCH --mail-type=ALL
#SBATCH --mail-user=washbee1@student.gsu.edu
#SBATCH --oversubscribe

# Path to the Conda environment
conda_env_path="/data/users2/washbee/anaconda3/envs/mwrm"

# Initialize Conda and activate the environment
source /data/users2/washbee/anaconda3/etc/profile.d/conda.sh
conda activate "$conda_env_path"

subjects_dir="/data/users2/washbee/speedrun/topofit-data"

# Read test_subject_ids.txt into an array
mapfile -t subject_ids < "${subjects_dir}/"test_subject_ids.txt

# Retrieve subject id using SLURM_ARRAY_TASK_ID
# Make sure SLURM_ARRAY_TASK_ID is 0-based. If it's 1-based, subtract 1 from it.
subject_id=${subject_ids[$SLURM_ARRAY_TASK_ID]}

source /data/users2/washbee/freesurfer/SetUpFreeSurfer.sh

# Execute the Python script with the required arguments
python ../cortexode_all.py --subjects_dir "$subjects_dir" --subject_id "$subject_id" --hemi "rh" --surfType "pial" --project "cortexode" --project_gt_base_path "/speedrun/cortexode-data-rp/test" --project_pred_base_path "/data/users2/washbee/speedrun/CortexODE_fork/ckpts/experiment_6_A100/result"
