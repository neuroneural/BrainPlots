import os
import argparse 
import socket
from csv import writer
import meshlib.mrmeshpy as mrmesh
from tqdm import tqdm

hostname = socket.gethostname()

def write_intersections2csv(model_name,intersections=None,subject=None,f1=None, f2=None):
    base_path = '/data/users2/llu13/FStutorial/Jul12'
    filename = 'intersections.csv'
    filename = base_path + filename
    List = [model_name, intersections, hostname,subject, f1,f2]
    
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            print("File created.")

    with open(filename, 'a') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(List)

dic = dict()

model, p, w = 'deepcsr', 'lh_pial', 'lh_white'

dic[model] = {
    p: "/data/users2/washbee/speedrun/outputdirs/deepcsr-output_dir-timing/checkpoints/test-set/lh_pial",
    w: "/data/users2/washbee/speedrun/outputdirs/deepcsr-output_dir-timing/checkpoints/test-set/lh_white",
}

def get_white_from_pial(pialfile):
    # deepcsr
    return pialfile[:6]+'_lh_white.stl'

list1 = os.listdir(dic[model][p])
for i in tqdm(range(len(list1))):
    file1 = list1[i]
    pial_filepath = os.path.join(dic[model][p], file1)
    white_filepath = os.path.join(dic[model][w], get_white_from_pial(file1))

    # Load the meshes from the STL files
    mesh1 = mrmesh.loadMesh(pial_filepath)
    mesh2 = mrmesh.loadMesh(white_filepath)

    pairs = mrmesh.findCollidingTriangles(mrmesh.MeshPart(mesh1), mrmesh.MeshPart(mesh2))

    write_intersections2csv(f"{model}", len(pairs), file1[:6], pial_filepath, white_filepath)
