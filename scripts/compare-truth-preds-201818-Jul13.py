#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os


import pyvista as pv
from pyvista import examples


from collections import defaultdict

pv.global_theme.transparent_background = True


# In[5]:


pre = '/Users/mialu/Documents/Course22Fall/TReNDS/neuroneural/BrainPlots/data/201818/all201818'
models1 = ['cortexode', 'corticalflow','deepcsr','pialnn','vox2cortex']
models2 = ['cortexode', 'corticalflow','deepcsr','topofit','vox2cortex']


# In[6]:


def org_files(surf, models, pre = pre):
    preds = []
    gts = []
    for m in models:
        for f in os.listdir(pre):
            if m in f and surf in f:
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

surf = 'pial'
models = models1
preds1, gts1 = org_files(surf,models)

surf = 'white'
models = models2
preds2, gts2 = org_files(surf,models)


# In[7]:


plotter = pv.Plotter(shape=(2, len(models1)))

files1,file_truths1, files2, file_truths2 = preds1, gts1, preds2, gts2

for idx in range(len(models1)):
    mesh1, mesh2 = pv.read(files1[idx]), pv.read(file_truths1[idx])
    plotter.subplot(0, idx)
    plotter.add_text(models1[idx], position='lower_edge', font_size=12)
    plotter.add_mesh(mesh1)
    plotter.add_mesh(mesh2, color='b', opacity=0.7)  


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

