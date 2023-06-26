# -*- coding: utf-8 -*-
# the corticalflow file paths: 
# /data/users2/llu13/CalcDistance/corticalflow/cfpp/jun16/pial/201818_lh_pial_Df2.pial_converted.stl
# /data/users2/llu13/CalcDistance/corticalflow/cfpp/jun16/white/201818_lh_white_Df2.white_converted.stl
# the code should be run with SLURM. 

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import os
import sys
import time
import pickle
import argparse
from copy import deepcopy

import torch
import torch.nn as nn
import torch.autograd as autograd
import numpy as np
import tqdm

import trimesh
import pyrender
from mesh_intersection.bvh_search_tree import BVH
import csv

try:
    input = raw_input
except NameError:
    pass

def main():
    device = torch.device('cuda')

    parser = argparse.ArgumentParser()
    parser.add_argument('mesh_fn', type=str,
                        help='A mesh file path(.obj, .ply, e.t.c.) to be checked' +
                        ' for collisions')
    parser.add_argument('--max_collisions', default=8, type=int,
                        help='The maximum number of bounding box collisions')

    args, _ = parser.parse_known_args()
    mesh_fn = args.mesh_fn
    max_collisions = args.max_collisions

    dic = []


    input_mesh = trimesh.load(mesh_fn)
    vertices = torch.tensor(input_mesh.vertices,dtype=torch.float32, device=device)
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

    # Save collisions.
    collision_fname = os.path.basename(mesh_fn) + '-collision.pickle'
    with open(collision_fname, 'wb') as f:
        pickle.dump(collisions, f)
        

if __name__ == "__main__":
    main()

