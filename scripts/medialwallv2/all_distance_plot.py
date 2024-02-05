import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import matplotlib as mpl
import numpy as np
import math

# Directories of the projects, sorted alphabetically
project_folders = sorted([
    'pialnn', 'topofit', 'cortexode_rk4', 'deepcsr',
    'cortexode_euler', 'corticalflow', 'corticalflow++', 'freesurfer', 'vox2cortex'
])

# Initialize an empty DataFrame to store all data
all_data = pd.DataFrame()

# Iterate over each project folder and read the data
for project in project_folders:
    file_path = os.path.join(project, 'distances.csv')
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df['Project'] = project  # Add a column for the project name
        all_data = pd.concat([all_data, df], ignore_index=True)
    else:
        print(f"File not found: {file_path}")

# Set plot aesthetics
sns.set(style="whitegrid")
plt.figure(figsize=(12, 8))

# Define a list of marker styles
markers = ["o", "s", "^", "P", "*", "X", "D", "v", "h"] 

# Create a dictionary to map each project to a marker style
marker_map = {project: marker for project, marker in zip(project_folders, markers)}

# Filter for LH Pial data
lh_pial_data = all_data[(all_data['Hemisphere'] == 'lh') & (all_data['Surface Type'] == 'pial')]

# Filter for RH Pial data
rh_pial_data = all_data[(all_data['Hemisphere'] == 'rh') & (all_data['Surface Type'] == 'pial')]

# Filter for LH White data
lh_white_data = all_data[(all_data['Hemisphere'] == 'lh') & (all_data['Surface Type'] == 'white')]

# Filter for RH White data
rh_white_data = all_data[(all_data['Hemisphere'] == 'rh') & (all_data['Surface Type'] == 'white')]

# Create subplots for LH Pial, RH Pial, LH White, and RH White
subplots = {
    'LH Pial': lh_pial_data,
    'RH Pial': rh_pial_data,
    'LH White': lh_white_data,
    'RH White': rh_white_data
}

# Set global font size using rcParams
mpl.rcParams.update({'font.size': 16})

# Define subplot size and aspect ratio
subplot_height = 5
subplot_aspect = 1.2

# Create figure and axes for subplots
fig, axes = plt.subplots(2, 2, figsize=(2 * subplot_aspect * subplot_height, 2 * subplot_height))

# Create a fixed palette for all projects
fixed_palette = sns.color_palette("husl", len(project_folders))

# Create a dictionary to map each project to a color
color_map = {project: color for project, color in zip(project_folders, fixed_palette)}


for i, (title, data) in enumerate(subplots.items()):
    ax = axes[i // 2, i % 2]

    if not data.empty:
        # Plot scatter plot for each project in the current subplot
        for project in project_folders:
            project_data = data[data['Project'] == project]
            if not project_data.empty:
                sns.scatterplot(data=project_data, x='Chamfer Distance', y='Hausdorff Distance', 
                                label=project, ax=ax, color=color_map[project], marker=marker_map[project])

        ax.set_title(f'{title} - Hausdorff vs Chamfer Distance')
        ax.set_xlabel('Chamfer Distance (log scale)')
        ax.set_ylabel('Hausdorff Distance (log scale)')
        ax.set_xscale('log')
        ax.set_yscale('log')

    # Set x-ticks and y-ticks for logarithmic scale if needed

# Set legend outside the plot area
handles, labels = ax.get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=len(project_folders))

plt.tight_layout()

# Save the plot as PNG
plt.savefig('all_surface_types_hausdorff_chamfer_scatter.png')

# Also save the plot as SVG for higher quality vector graphics
plt.savefig('all_surface_types_hausdorff_chamfer_scatter.svg')

# Close the plot to free up resources
plt.close()
