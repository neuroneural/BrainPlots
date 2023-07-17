#!/usr/bin/env python
# coding: utf-8

# # get files

# In[44]:


import os
import colorcet as cc
from colour import Color

from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import matplotlib as mpl

import numpy as np

import pymeshlab as ml

import pyvista as pv
from pyvista import examples


from collections import defaultdict

from colorspacious import cspace_converter
pv.global_theme.transparent_background = True


# In[45]:


def calc_distance():
    """
    return mesh with distance as an attribute
    """
    ms = ml.MeshSet()
    ms.load_new_mesh(file_truth)
    ms.load_new_mesh(file)
    ms.compute_scalar_by_distance_from_another_mesh_per_vertex()
    ms.compute_color_from_scalar_per_vertex()
    return ms

def calc_hausdorff_distance(file_truth, file):
    """
    return Hausdorff distance.
    """
    ms = ml.MeshSet()
    ms.load_new_mesh(file_truth)
    ms.load_new_mesh(file)
    d = ms.get_hausdorff_distance()
    return d 

def get_hdd(files,file_truths):
    """
    return Hausdorff Distance for multiple files.
    """
    tmps = []
    for i in range(len(files)):
        file_truth = file_truths[i]
        file = files[i]
        d = calc_hausdorff_distance(file_truth, file)
        tmps.append(d)
    return tmps

def calculate_tmp(tmp, d, attr,way='william'):
    """
    normalize the distance values by percentage of attr ('diag_mesh0')
    """
    if way=='william':
        return [abs(j)/d[attr]*100 for j in tmp] # normalize with diag_mesh distance
    return [abs(j) for j in tmp]


def truncate_tmp(tmp,lower_percentile=5, higher_percentile = 95):  
    """
    remove the 'outliers' in distance
    """
    print('max of distance before truncation is : ',max(tmp))
    minz = np.percentile(tmp, lower_percentile)
    maxz = np.percentile(tmp, higher_percentile)
    # truncate it between minz and maxz
    tmp = [max(max(i, minz),min(i,maxz)) for i in tmp]
    return tmp

def maximize_tmp(mses, tmps, maximize=True, MAX_VALUE = 1.8):
    """
    modify mesh distance values to include the same MAX_VALUE as its max_value
    """
    if maximize:
        for i in range(len(tmps)):
            # modify tmp value to include the same MAX_VALUE as its max_value
            tmps[i] = [min(j, MAX_VALUE) for j in tmps[i]]
            idx = tmps[i].index(max(tmps[i]))
            tmps[i][idx] = MAX_VALUE
            # assign tmp values to mesh
            mses[i]['values'] = tmps[i]
    return mses, tmps
    

def getit(files,file_truths,d,attr,MAX_VALUE=4.5):
    """
    main function
    """
    tmps = []
    mses = []
    for i in range(len(files)):
#         plt.subplot(5,1,i+1)
        file_truth = file_truths[i]
        file = files[i]
        ms2 = ml.MeshSet()
        ms2.load_new_mesh(file_truth)
        ms2.load_new_mesh(file)
        ms2.compute_scalar_by_distance_from_another_mesh_per_vertex()
        ms2.compute_color_from_scalar_per_vertex()
        ms2.apply_color_inverse_per_vertex()

        tmp = list(ms2[1].vertex_scalar_array())
        tmp = calculate_tmp(tmp,d[i], attr)
        tmp = truncate_tmp(tmp)
        tmps.append(tmp)
        
        mesh = pv.read(file)
        mses.append(mesh)
        
    mses,tmps = maximize_tmp(mses,tmps)
    distance = tmps
    return mses, distance


# In[47]:


pre = '/Users/mialu/Documents/Course22Fall/TReNDS/neuroneural/BrainPlots/data/201818/all201818'

models1 = ['cortexode', 'corticalflow','deepcsr','pialnn','vox2cortex']
models2 = ['cortexode', 'corticalflow','deepcsr','topofit','vox2cortex']

def org_files(surf, models, pre = pre):
    preds = []
    gts = []
    for m in models:
        for f in os.listdir(pre):
            if m in f and surf in f:
                if m in ['corticalflow', 'deepcsr', 'vox2cortex']:
                    if 'transformed' in f and '-removed-' in f:
                        if 'gt' not in f:
                            preds.append(os.path.join(pre,f))
                        else:
                            gts.append(os.path.join(pre,f))
                else:
                    if '-removed-' in f:
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


# In[54]:


cmap = mpl.colormaps['inferno'].reversed()
exp_date = 'Jul16'

def visualize_brain(files1, file_truths1, surf, models, scale = 6, cmap = cmap):
    d1 = get_hdd(files1,file_truths1)
    attr = 'diag_mesh_0'
    mses, tmps1 = getit(files1,file_truths1,d1,attr)
    for i in range(len(models)):
#         print(models[i])
        viewup1 = [1,0,0]
        viewup2 = [0,0,1]
        mesh = mses[i]
        pl = pv.Plotter()
        actor = pl.add_mesh(mesh,cmap=cmap)

        pl.set_background('white', all_renderers=False)
        pl.remove_scalar_bar()

        pl.view_yz()
        pl.set_viewup(viewup1)

        pl.set_viewup(viewup2)

        pl.remove_legend()
        pl.remove_floors()
        pl.remove_bounding_box()
        pl.remove_bounds_axes()
        pl.update_bounds_axes()
        pl.show()
        pl.screenshot(models[i] + f'-{surf}.png', transparent_background=True, return_img=True, scale=scale)
        
# -------------note--------------
# scale bar : confirmed correct for both pial and white on Jul 16. 


# In[56]:


visualize_brain(preds2, gts2, 'white', models1)


# In[55]:


visualize_brain(preds1, gts1, 'pial', models1)


# # Get Legend Plot

# In[57]:


cmap = mpl.colormaps['inferno'].reversed()
viewup1 = [1,0,0]
pv.global_theme.font.color = 'black'
mesh = mses1[0]
pl = pv.Plotter()
actor = pl.add_mesh(mesh,cmap=cmap)

pl.set_background('white', all_renderers=False)
# pl.remove_scalar_bar()

pl.view_yz()
pl.set_viewup(viewup1)
# pl.remove_actor(actor)
# pl.remove_legend()
pl.remove_floors()
pl.remove_bounding_box()
# pl.remove_bounds_axes()
# pl.update_bounds_axes()
pl.show()
# pl.screenshot('legend.png', transparent_background=True, return_img=False, scale=6)


# In[42]:





# In[ ]:




