#!/usr/bin/env python
# coding: utf-8

# In[3]:


from png2svglinlin import Png2Svg


# In[7]:


import os
os.listdir('new-data/')


# In[8]:


for f in os.listdir('new-data/'):
    png_file = os.path.join('new-data', f)
    save_to = os.path.join('data-layout-meshes-v2/', f[:-3] + 'svg')
    Png2Svg(png_file, save_to)

