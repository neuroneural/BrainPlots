import os
import json
import subprocess


target_folder = '/Users/mialu/Documents/Course22Fall/TReNDS/neuroneural/BrainPlots/data/201818/'

cmd = f'scp -r llu13@arcdev19:/data/users2/llu13/FStutorial/Jul5/data-for-medial-wall/201818/all201818/ {target_folder}'
subprocess.run(cmd, shell=True, check=True)  # 运行命令



