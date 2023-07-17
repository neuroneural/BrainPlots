#!/usr/bin/env python
# coding: utf-8

# In[2]:


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
import svgutils.transform as sg
import sys 

from colorspacious import cspace_converter
pv.global_theme.transparent_background = True


# In[7]:


#create new SVG figure
figure = sg.SVGFigure("90cm", "45cm")

# load matpotlib-generated figures

# models = models1

start = 150
x0 = 100 + start
xend = 1000 + start
xpos = list(np.linspace(x0,xend,6))

plots = []
txts = []

modelnames = ['CortexODE','CorticalFlow','DeepCSR','PialNN','Vox2Cortex']
models = ['cortexode','corticalflow','deepcsr','pialnn','vox2cortex']
scale = .046

prefix = './data-layout-meshes-v2/'
for i in range(5):
    filename = os.path.join(prefix, 'pial', f'{models[i]}-pial.svg')
    fig = sg.fromfile(filename)
    plot = fig.getroot()
    plot.rotate(90)
    plot.moveto(xpos[i], 0, scale, scale)
    plots.append(plot)
    

models = ['cortexode','corticalflow','deepcsr','topofit','vox2cortex']
for i in range(5):
    filename = os.path.join(prefix, 'white', f'{models[i]}-white.svg')
    fig = sg.fromfile(filename)
    plot = fig.getroot()
    plot.rotate(90)
    plot.moveto(xpos[i], 200, scale, scale)
    plots.append(plot)


sgh = 240
delta = -150

xpos = list(np.linspace(x0,xend+20,6))

txts = []
for i in range(5):
    if i!=3:
        txts.append(sg.TextElement(xpos[i] + delta,sgh, modelnames[i], size=12, weight="bold"))
        
txts.append(sg.TextElement(xpos[3] + delta,sgh-10, modelnames[3]+'*', size=12, weight="bold"))
txts.append(sg.TextElement(xpos[3] + delta,sgh+10, 'Topofit*', size=12, weight="bold"))


rotate = 270

txt1 = sg.TextElement(0, 0, 'Pial', size=12, weight="bold")
txt1.rotate(rotate)
txt1.moveto(50,150)
txt2 = sg.TextElement(0, 0, 'White', size=12, weight="bold")
txt2.rotate(rotate)
txt2.moveto(50,350)

txts.append(txt1)
txts.append(txt2)

# legend

scale = .4
x = 560
y = 440
fig = sg.fromfile('./data-layout-meshes/legend.svg')
plot = fig.getroot()
plot.moveto(x, y,scale,scale)
plots.append(plot)
txts.append(sg.TextElement(x+140 , y - 10 , 'Vertex Distance / Mesh Diag (%)', size=12))

# append plots and labels to figure
figure.append(txts)
figure.append(plots)


# save generated SVG files
figure.save("fig_final03.svg")

