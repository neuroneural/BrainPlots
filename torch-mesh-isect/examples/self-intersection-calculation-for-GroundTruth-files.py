# -*- coding: utf-8 -*-
# Contact: llu13@gsu.edu; pku600gt@gmail.com

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import sys
import os

import time
import pickle
import argparse

try:
    input = raw_input
except NameError:
    pass

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



if __name__ == "__main__":
    

    device = torch.device('cuda')

    parser = argparse.ArgumentParser()
    parser.add_argument('mesh_filefolder', type=str,
                        help='A mesh file (.obj, .ply, e.t.c.) to be checked' +
                        ' for collisions')
#     parser.add_argument('idx', type=str,
#                         help='A csv file name to store the numbers of triangles and collisions.')
    parser.add_argument('--max_collisions', default=8, type=int,
                        help='The maximum number of bounding box collisions')

    args, _ = parser.parse_known_args()

#     idx = args.idx
    prefix = args.mesh_filefolder if args.mesh_filefolder[-1]=='/' else args.mesh_filefolder+'/'
    dic = []
    LEN = len('200008_lh.pial')
    tmp_files = os.listdir(prefix)
    tmp_files.sort()
    
    # for LH Pial of GTruth, some samples have CUDA error, should be exlucded. 
    excluded = [10,19,66]
    
#     with open('SelfIntersectionGTruthOutputs.csv', 'a') as f:
#         writer = csv.writer(f)
#         writer.writerow(['file_idx', 'file_name', 'selfIntersections','triangles'])
    
    START = 67
    for i,mesh_fn in enumerate(tmp_files[START:]):
#         if i not in excluded and mesh_fn[-3:]=='stl':
        i += START
        if mesh_fn[-3:] == 'stl':
            max_collisions = args.max_collisions
            input_mesh = trimesh.load(prefix + mesh_fn)
            vertices = torch.tensor(input_mesh.vertices,
                                    dtype=torch.float32, device=device)
            faces = torch.tensor(input_mesh.faces.astype(np.int64),
                                 dtype=torch.long,
                                 device=device)

            batch_size = 1
            triangles = vertices[faces].unsqueeze(dim=0)

            m = BVH(max_collisions=max_collisions)

            torch.cuda.synchronize()
            
            outputs = m(triangles)
            torch.cuda.synchronize()

            outputs = outputs.detach().cpu().numpy().squeeze()

            collisions = outputs[outputs[:, 0] >= 0, :]
    
#             # Save the mesh.
#             tmp = prefix.split('/')[-2]
#             trimesh.exchange.export.export_mesh(input_mesh, mesh_fn[:LEN]+'input_mesh.'+ mesh_fn[-3:])
#             # Save collisions.
#             with open(mesh_fn[:LEN]+'collisions.pickle', 'wb') as f:
#                 pickle.dump(collisions, f)

            # Write data to csv.
            with open('SelfIntersectionGTruthOutputs.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow([i, mesh_fn, collisions.shape[0],triangles.shape[1]])
