# -*- coding: utf-8 -*-
# -- Linlin --
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import trimesh
import pyvista as pv

import os
from csv import writer

import warnings
warnings.filterwarnings("ignore")
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    
from vtkmodules.vtkCommonCore import vtkLogger
vtkLogger.SetStderrVerbosity(vtkLogger.VERBOSITY_OFF)

import sys
import time
import argparse

try:
    input = raw_input
except NameError:
    pass


if __name__ == "__main__":

    def get_pairs(prepial, prewhite):
        if prepial[-1] != '/':
            prepial += '/'
        if prewhite[-1] != '/':
            prewhite += '/'
        return [[prepial + f1, prewhite + f2] for f1, f2 in zip(os.listdir(prepial),os.listdir(prewhite))]


    parser = argparse.ArgumentParser()
    parser.add_argument('idx', type=int,
                        help='the file idx of deepcsr samples (from 0 - 106)')
    args, _ = parser.parse_known_args()

    idx = args.idx 

    
    dcsr_pial = '/data/users2/washbee/speedrun/outputdirs/deepcsr-output_dir-timing/checkpoints/test-set/lh_pial/'
    dcsr_white = '/data/users2/washbee/speedrun/outputdirs/deepcsr-output_dir-timing/checkpoints/test-set/lh_white'

    prepial, prewhite = dcsr_pial, dcsr_white
    filepairs = get_pairs(prepial, prewhite)

    f1, f2 = filepairs[idx]
    s1, s2 = pv.read(f1), pv.read(f2)
    intersection, _, _ = s1.intersection(s2)

    data = [idx, f1, len(intersection.points), len(s1.points)]

    with open('deepcsrWtPlCollision.csv', 'a') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(data)
        f_object.close()