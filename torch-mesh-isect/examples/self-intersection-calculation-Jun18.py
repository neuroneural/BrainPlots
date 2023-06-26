# -*- coding: utf-8 -*-

import os
import torch
import torch.nn as nn
import torch.autograd as autograd
import numpy as np
import trimesh
import csv
import argparse
from mesh_intersection.bvh_search_tree import BVH


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mesh_filefolder', type=str, help='mesh file folder')
    parser.add_argument('modelname', type=str, help='Model name such as freesurfer')
    parser.add_argument('modelname2', type=str, help='Model name such as pial or white')
    parser.add_argument('--max_collisions', default=8, type=int, help='Maximum number of bounding box collisions')

    args = parser.parse_args()

    device = torch.device('cuda')

    prefix = os.path.join(args.mesh_filefolder, '')
    file_list = sorted(os.listdir(prefix))
    excluded = [0]  # cortexODE lh pial # index
    start_idx = 0

    for idx, file_name in enumerate(file_list[start_idx:]):
        sample_idx = idx + start_idx
        if file_name[-3:] in ['stl', 'ply', 'obj']:
            print(sample_idx, file_name)
            input_mesh = trimesh.load(prefix + file_name)
            vertices = torch.tensor(input_mesh.vertices, dtype=torch.float32, device=device)
            faces = torch.tensor(input_mesh.faces.astype(np.int64), dtype=torch.long, device=device)

            triangles = vertices[faces].unsqueeze(dim=0)

            bvh_tree = BVH(max_collisions=args.max_collisions)

            torch.cuda.synchronize()
            outputs = bvh_tree(triangles)
            torch.cuda.synchronize()

            outputs = outputs.detach().cpu().numpy().squeeze()
            collisions = outputs[outputs[:, 0] >= 0, :]

            with open('collision_data_csv/Jun18/SelfIntersection-{}-{}.csv'.format(args.modelname,args.modelname2), 'a') as f:
                writer = csv.writer(f)
                writer.writerow([sample_idx, args.modelname, args.modelname2, collisions.shape[0], triangles.shape[1], file_name])


if __name__ == "__main__":
    main()

