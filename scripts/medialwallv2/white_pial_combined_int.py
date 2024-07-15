import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import matplotlib as mpl
import numpy as np
import math

# Assuming the correct paths for the datasets
outliers_df = pd.read_csv('mw_outliers.csv')
excluded_subject_ids = outliers_df['subject_id'].unique()

# Directories of the projects, sorted alphabetically
project_folders = sorted([
    'csrf', 'cortexode_rk4', 'deepcsr',
    'cortexode_euler', 'corticalflow', 'corticalflow++', 'freesurfer',
    'vox2cortex'
])

# Aggregate data from all projects
all_data = pd.DataFrame()

for project in project_folders:
    file_path = os.path.join(project, 'white_pial_intersections.csv')
    df = pd.read_csv(file_path)
    df = df[~df['subject_id'].isin(excluded_subject_ids)]
    df['Project'] = project
    all_data = pd.concat([all_data, df], ignore_index=True)

# Change 'csrf' project name to '*csrf (ours)'
all_data['Project'] = all_data['Project'].replace('csrf', '*csrf (ours)')

# Update the project folders list to include the renamed project
project_folders = sorted([
    '*csrf (ours)', 'cortexode_rk4', 'deepcsr', 'cortexode_euler',
    'corticalflow', 'corticalflow++', 'freesurfer', 'vox2cortex'
])

# Define reused color palette and markers
fixed_palette = sns.color_palette("husl", 10)
color_map = {
    '*csrf (ours)': fixed_palette[0],
    'pialnn': fixed_palette[1],
    'topofit': fixed_palette[2],
    'cortexode_rk4': fixed_palette[3],
    'deepcsr': fixed_palette[4],
    'cortexode_euler': fixed_palette[5],
    'corticalflow': fixed_palette[6],
    'corticalflow++': fixed_palette[7],
    'freesurfer': fixed_palette[8],
    'vox2cortex': fixed_palette[9]
}

marker_map = {
    '*csrf (ours)': "D", 
    'pialnn': "|", 
    'topofit': "_", 
    'cortexode_rk4': ",", 
    'deepcsr': "+",
    'cortexode_euler': "x", 
    'corticalflow': "d", 
    'corticalflow++': "v", 
    'freesurfer': "h", 
    'vox2cortex': "o"
}

# Global font size and subplot settings
mpl.rcParams.update({'font.size': 32})
subplot_height = 10  # Increase the subplot height
subplot_aspect = 1.7

# Find the global maximum for 'Intersections White-Pial'
global_max = all_data['Intersections White-Pial'].max()

# Initialize the figure and axis
plt.figure(figsize=( subplot_aspect * subplot_height, subplot_height))
ax = plt.gca()  # Get the current Axes instance

# Custom function to plot with markers and annotate max values
for project in project_folders:
    project_data = all_data[all_data['Project'] == project]
    if not project_data.empty:
        # Apply jitter to x-axis positions
        jittered_x = np.random.uniform(-0.2, 0.2, size=len(project_data)) + project_folders.index(project)
        # Plot each project with a custom marker
        ax.scatter(jittered_x, project_data['Intersections White-Pial'], 
                   alpha=0.6, marker=marker_map[project], 
                   color=color_map[project], s=80)
        # Annotate the maximum value with the same color as the marker
        max_value = project_data['Intersections White-Pial'].max()
        ax.text(project_folders.index(project), max_value, f'{max_value:.0f}', color=color_map[project], ha='center', va='bottom', fontsize=32)

# Set custom x-ticks to show project names
ax.set_xticks(range(len(project_folders)))
ax.set_xticklabels(project_folders, rotation=25, ha="right")

# Set the y-scale to logarithmic
ax.set_yscale("log")
ax.set_ylim(1, global_max * 1.1)

# Set axis labels and title
ax.set_xlabel("Project")
ax.set_ylabel("White-Pial Intersections")
ax.set_title("White-Pial Intersections - All Hemispheres")

plt.tight_layout()

# Save the plot
plt.savefig('combined_white_pial_intersections.png')
plt.savefig('combined_white_pial_intersections.svg')
plt.close()
