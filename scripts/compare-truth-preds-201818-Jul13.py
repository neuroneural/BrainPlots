#!/usr/bin/env python
# coding: utf-8

# Importing necessary libraries
import os
import pyvista as pv
from pyvista import examples
from collections import defaultdict

# Setting pyvista global theme to have a transparent background
pv.global_theme.transparent_background = True

# Setting up the directory of the data and the models' names
pre = '/Users/mialu/Documents/Course22Fall/TReNDS/neuroneural/BrainPlots/data/201818/all201818'
models1 = ['cortexode', 'corticalflow','deepcsr','pialnn','vox2cortex']
models2 = ['cortexode', 'corticalflow','deepcsr','topofit','vox2cortex']

# Function to organize files
def org_files(surf, models, pre = pre):
    preds = []
    gts = []
    # Loop through each model
    for m in models:
        # Loop through each file in the directory
        for f in os.listdir(pre):
            # Checking if the file belongs to the model and surface 
            if m in f and surf in f:
                # Special handling for certain models
                if m in ['corticalflow', 'deepcsr', 'vox2cortex']:
                    if 'transformed' in f and '-rm-' in f:
                        if 'gt' not in f:
                            preds.append(os.path.join(pre,f))
                        else:
                            gts.append(os.path.join(pre,f))
                else:
                    if '-rm-' in f:
                        if 'gt' not in f:
                            preds.append(os.path.join(pre,f))
                        else:
                            gts.append(os.path.join(pre,f))
    return preds, gts

# Calling the function for 'pial' surface and models1
surf = 'pial'
models = models1
preds1, gts1 = org_files(surf,models)

# Calling the function for 'white' surface and models2
surf = 'white'
models = models2
preds2, gts2 = org_files(surf,models)

# Create the plotter object
plotter = pv.Plotter(shape=(2, len(models1)))

files1,file_truths1, files2, file_truths2 = preds1, gts1, preds2, gts2

# Adding the models to the first row of subplots
for idx in range(len(models1)):
    mesh1, mesh2 = pv.read(files1[idx]), pv.read(file_truths1[idx])
    plotter.subplot(0, idx)
    plotter.add_text(models1[idx], position='lower_edge', font_size=12)
    plotter.add_mesh(mesh1)
    plotter.add_mesh(mesh2, color='b', opacity=0.7)  

# Adding the models to the second row of subplots
for idx in range(len(models1)):
    mesh1, mesh2 = pv.read(files2[idx]), pv.read(file_truths2[idx])
    plotter.subplot(1, idx)
    plotter.add_text(models2[idx], position='upper_edge',font_size=12)
    plotter.add_mesh(mesh1)
    plotter.add_mesh(mesh2, color = 'b', opacity=0.7)   

# Link the camera position of all subplots
plotter.link_views()

# Render the plot
print('Grey is predicted pial. \nBlue is their respective ground truth. \n\n1st row: transformed [vox2cortex,deepcsr,corticalflow]. \n\n2nd row, the 3 are not transformed.')
plotter.show()


