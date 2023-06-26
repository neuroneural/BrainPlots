# -*- coding: utf-8 -*-
# Contact: llu13@gsu.edu; pku600gt@gmail.com

from __future__ import absolute_import, print_function, division

import sys
import os
import time
import pickle
import argparse
import torch
import torch.nn as nn
import torch.autograd as autograd
from copy import deepcopy
import numpy as np
import tqdm
import trimesh
import pyrender
from mesh_intersection.bvh_search_tree import BVH
import csv
import pickle

try:
    input = raw_input
except NameError:
    pass

def main():
    
    
    
    device = torch.device('cuda')

    parser = argparse.ArgumentParser()
    parser.add_argument('mesh_filefolder', type=str, help='A mesh file (.obj, .ply, .stl etc.) to be checked for collisions')
    parser.add_argument('modelname', type=str, help='model name such as freesurfer')
    parser.add_argument('modelname2', type=str, help='model name such as pial or white')
    parser.add_argument('--max_collisions', default=8, type=int, help='The maximum number of bounding box collisions')

    args, _ = parser.parse_known_args()
    max_collisions = args.max_collisions
    prefix = args.mesh_filefolder if args.mesh_filefolder[-1] == '/' else args.mesh_filefolder + '/'
    tmp_files = os.listdir(prefix)
    tmp_files.sort()

    modelname =args.modelname
    modelname2 = args.modelname2
#     excluded = [10, 19, 66]  # Samples to be excluded for LH Pial, FreeSurfer (cortexode truth)
#     excluded = [36,58,62] # pialNN # index
    excluded = [0] # cortexODE lh pial # index
    START = 78
    for i, mesh_fn in enumerate(tmp_files[START:]):
        sample_idx = i + START
        if mesh_fn[-3:] in ['stl','ply','obj']:
            print(sample_idx,mesh_fn)
            input_mesh = trimesh.load(prefix + mesh_fn)
            vertices = torch.tensor(input_mesh.vertices, dtype=torch.float32, device=device)
            faces = torch.tensor(input_mesh.faces.astype(np.int64), dtype=torch.long, device=device)
            
            triangles = vertices[faces].unsqueeze(dim=0)

            m = BVH(max_collisions=max_collisions)

            torch.cuda.synchronize()
            outputs = m(triangles)
            torch.cuda.synchronize()

            outputs = outputs.detach().cpu().numpy().squeeze()

            collisions = outputs[outputs[:, 0] >= 0, :]
            
#             fn = 'collision_data_csv/allCollisions/' + modelname + '/' +  str(sample_idx) + '-' + mesh_fn + '-collisions.pkl'

#             data = collisions
#             data = outputs

#             with open(fn, 'wb') as f:
#                 pickle.dump(data, f)
            
            # Write data to csv.
            with open('collision_data_csv/SelfIntersection-rmMedialWall.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow([sample_idx, modelname, modelname2, collisions.shape[0], triangles.shape[1], mesh_fn])
                
                

if __name__ == "__main__":
    main()

