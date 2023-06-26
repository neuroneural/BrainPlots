# -*- coding: utf-8 -*-

# Max-Planck-Gesellschaft zur Förderung der Wissenschaften e.V. (MPG) is
# holder of all proprietary rights on this computer program.
# You can only use this computer program if you have closed
# a license agreement with MPG or you get the right to use the computer
# program from someone who is authorized to grant you that right.
# Any use of the computer program without a valid license is prohibited and
# liable to prosecution.
#
# Copyright©2019 Max-Planck-Gesellschaft zur Förderung
# der Wissenschaften e.V. (MPG). acting on behalf of its Max Planck Institute
# for Intelligent Systems and the Max Planck Institute for Biological
# Cybernetics. All rights reserved.
#
# Contact: ps-license@tuebingen.mpg.de

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
    parser.add_argument('mesh_fn', type=str,
                        help='A mesh file (.obj, .ply, e.t.c.) to be checked' +
                        ' for collisions')
    parser.add_argument('idx', type=str,
                        help='A csv file name to store the numbers of triangles and collisions.')
    parser.add_argument('--max_collisions', default=8, type=int,
                        help='The maximum number of bounding box collisions')

    args, _ = parser.parse_known_args()

    idx = args.idx
    prefix = args.mesh_fn if args.mesh_fn[-1]=='/' else args.mesh_fn+'/'
    dic = []
    
    for i,mesh_fn in enumerate(os.listdir(args.mesh_fn)):
        if mesh_fn[-3:]=='stl' and mesh_fn[:2]==idx:
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
    
            # Save the mesh.
            tmp = prefix.split('/')[-2]
            trimesh.exchange.export.export_mesh(input_mesh, mesh_fn[:2]+'input_mesh.'+ mesh_fn[-3:])
            # Save collisions.
            with open(mesh_fn[:2]+'collisions.pickle', 'wb') as f:
                pickle.dump(collisions, f)
        
