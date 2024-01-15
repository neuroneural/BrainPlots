#!/bin/bash
#SBATCH -n 1
#SBATCH -c 6
#SBATCH --mem=15g
#SBATCH -p qTRDGPUH
#SBATCH -t 4-00:00
#SBATCH -J rsync
#SBATCH -e jobs/error%A_%a.err
#SBATCH -o jobs/out%A_%a.out
#SBATCH -A psy53c17
#SBATCH --mail-type=ALL
#SBATCH --mail-user=washbee1@student.gsu.edu
#SBATCH --oversubscribe


sleep 5s
echo "aa"
rsync -av --progress /data/old_users2/washbee /data/users2/washbee
sleep 5s
