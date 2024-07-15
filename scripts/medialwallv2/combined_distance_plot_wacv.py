import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import matplotlib as mpl
import numpy as np
import math

# Directories of the projects, sorted alphabetically
project_folders = sorted([
    'pialnn', 'topofit', 'cortexode_rk4', 'deepcsr','csrf',
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

# Change 'csrf' project name to '*csrf (ours)'
all_data['Project'] = all_data['Project'].replace('csrf', '*csrf (ours)')

# Update the project folders list for correct labeling and color mapping
project_folders = sorted([
    'pialnn', 'topofit', 'cortexode_rk4', 'deepcsr','*csrf (ours)',
    'cortexode_euler', 'corticalflow', 'corticalflow++', 'freesurfer', 'vox2cortex'
])

# Set plot aesthetics
sns.set(style="whitegrid")
plt.figure(figsize=(12, 8))

# Create subplots for combined Pial and White
combined_pial_data = all_data[all_data['Surface Type'] == 'pial']
combined_white_data = all_data[all_data['Surface Type'] == 'white']

subplots = {
    'Combined Pial': combined_pial_data,
    'Combined White': combined_white_data
}

# Set global font size using rcParams
mpl.rcParams.update({'font.size': 32})

# Create figure and axes for subplots
fig, axes = plt.subplots(1, 2, figsize=(10, 5))  # Adjusted figure size to more standard proportions

# Create a fixed palette for all projects
fixed_palette = sns.color_palette("husl", len(project_folders))

# Create a dictionary to map each project to a color and marker
color_map = {project: color for project, color in zip(project_folders, fixed_palette)}
#marker_map = {project: marker for project, marker in zip(project_folders, ["o", "s", "^", "P", "*", "X", "D", "v", "h", "+"])}
marker_map = {project: marker for project, marker in zip(project_folders, ["D", "|", "_", ",", "+", "x", "d", "v", "h", "o"])}
msize = 4.0
for i, (title, data) in enumerate(subplots.items()):
    ax = axes[i]
    if not data.empty:
        # Plot scatter plot for each project in the current subplot
        for project in project_folders:
            project_data = data[data['Project'] == project]
            if not project_data.empty:
                sns.scatterplot(data=project_data, x='Chamfer Distance', y='Hausdorff Distance', 
                                label=project, ax=ax, color=color_map[project], marker=marker_map[project],s=msize)

        ax.set_title(f'{title} - Hausdorff vs Chamfer Distance')
        ax.set_xlabel('Chamfer Distance (log scale)')
        ax.set_ylabel('Hausdorff Distance (log scale)')
        ax.set_xscale('log')
        ax.set_yscale('log')

# Set legend outside the plot area
handles, labels = ax.get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=len(project_folders))

plt.tight_layout()

# Save the plot as PNG
plt.savefig('combined_surface_types_hausdorff_chamfer_scatter.png')

# Also save the plot as SVG for higher quality vector graphics
plt.savefig('combined_surface_types_hausdorff_chamfer_scatter.svg')

# Close the plot to free up resources
plt.close()
