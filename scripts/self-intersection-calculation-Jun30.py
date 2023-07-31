# Import necessary libraries and modules
import os
import torch
import torch.nn as nn
import torch.autograd as autograd
import numpy as np
import trimesh
import csv
import argparse
from mesh_intersection.bvh_search_tree import BVH

# Main function to calculate self-intersections for full mesh
def main():
    # Define the command-line arguments parser
    parser = argparse.ArgumentParser()
    parser.add_argument('mesh_filefolder', type=str, help='mesh file folder')
    parser.add_argument('modelname2', type=str, help='Second model name such as pial or white')
    parser.add_argument('modelname', type=str, help='First model name such as freesurfer')
    parser.add_argument('--max_collisions', default=8, type=int, help='Maximum number of bounding box collisions')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Set up CUDA device for GPU acceleration
    device = torch.device('cuda')

    # List the files in the given folder
    prefix = os.path.join(args.mesh_filefolder, '')
    file_list = sorted(os.listdir(prefix))

    start_idx = 0

    # Process each file
    for idx, file_name in enumerate(file_list[start_idx:]):
        sample_idx = idx + start_idx
        print(sample_idx, file_name)

        # Load the mesh file
        input_mesh = trimesh.load(prefix + file_name)
        
        # Transfer vertices and faces data to PyTorch tensors
        vertices = torch.tensor(input_mesh.vertices, dtype=torch.float32, device=device)
        faces = torch.tensor(input_mesh.faces.astype(np.int64), dtype=torch.long, device=device)

        # Arrange vertices into triangles
        triangles = vertices[faces].unsqueeze(dim=0)

        # Build the BVH tree for collision detection
        bvh_tree = BVH(max_collisions=args.max_collisions)

        # Calculate the intersection
        torch.cuda.synchronize()
        outputs = bvh_tree(triangles)
        torch.cuda.synchronize()

        # Process the outputs and identify the collisions
        outputs = outputs.detach().cpu().numpy().squeeze()
        collisions = outputs[outputs[:, 0] >= 0, :]

        # Set up the CSV file for storing the output data
        fname = 'examples/mydata/collision_data_csv/Jun30/SelfIntersection-{}-{}.csv'.format(args.modelname,args.modelname2)
        
        # Write the output data to the CSV file
        with open(fname, 'a') as f:
            writer = csv.writer(f)
            writer.writerow([sample_idx, args.modelname, args.modelname2, collisions.shape[0], triangles.shape[1], file_name])

# Entry point of the script
if __name__ == "__main__":
    main()
