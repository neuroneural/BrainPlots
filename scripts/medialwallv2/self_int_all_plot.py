import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import os
import math

# Directories of the projects, sorted alphabetically
project_folders = sorted([
    'pialnn', 'topofit', 'cortexode_rk4', 'deepcsr',
    'cortexode_euler', 'corticalflow', 'corticalflow++', 'freesurfer', 'vox2cortex'
])

# Load outliers
outliers_df = pd.read_csv('mw_outliers.csv')
excluded_subject_ids = outliers_df['subject_id'].unique()

# Aggregate data from all projects
all_data = pd.DataFrame()

for project in project_folders:
    file_path = os.path.join(project, 'distances.csv')
    df = pd.read_csv(file_path)
    df = df[~df['subject_id'].isin(excluded_subject_ids)]
    df['Project'] = project
    all_data = pd.concat([all_data, df], ignore_index=True)

# Define a list of marker styles
markers = ["o", "s", "^", "P", "*", "X", "D", "v", "h"]

# Create a dictionary to map each project to a marker style
marker_map = {project: marker for project, marker in zip(project_folders, markers)}

# Set plot aesthetics
sns.set(style="whitegrid")
mpl.rcParams.update({'font.size': 16})

# Define subplot size and aspect ratio
subplot_height = 5
subplot_aspect = 1.2

# Determine the global max and min values for setting a consistent scale
global_max = all_data['Self-Intersection C_mwrm'].max()
global_min = all_data['Self-Intersection C_mwrm'][all_data['Self-Intersection C_mwrm'] > 0].min()  # Avoid log(0) issue

# Adjust global max for annotation space
global_max_adjusted = global_max * 1.1  # Increase slightly for annotation

# Create figure and axes for subplots
fig, axes = plt.subplots(2, 2, figsize=(2 * subplot_aspect * subplot_height, 2 * subplot_height))

# Create a fixed palette for all projects
fixed_palette = sns.color_palette("husl", len(project_folders))

# Mapping project names to numerical values for y-axis
project_mapping = {name: i for i, name in enumerate(project_folders)}

# Filter and plot data for each subplot
for i, (hemisphere, surface_type) in enumerate([('LH', 'pial'), ('RH', 'pial'), ('LH', 'white'), ('RH', 'white')]):
    ax = axes.flatten()[i]
    data = all_data[(all_data['Hemisphere'] == hemisphere.lower()) & (all_data['Surface Type'] == surface_type.lower())]

    if not data.empty:
        # Calculate and annotate the maximum value for each project
        for project in project_folders:
            project_data = data[data['Project'] == project]
            if not project_data.empty:
                jittered_y = project_mapping[project] + (np.random.rand(len(project_data)) - 0.5) * 0.5
                max_value = project_data['Self-Intersection C_mwrm'].max()
                ax.scatter(project_data['Self-Intersection C_mwrm'], jittered_y,
                           s=15, alpha=0.6, label=project,
                           color=fixed_palette[project_folders.index(project)],
                           marker=marker_map[project])
                
                # Annotate max value
                ax.text(max_value, project_mapping[project], f'{max_value:.2f}',
                        color='black', ha='left', va='center', fontsize=9)

    ax.set_title(f'{hemisphere} {surface_type.capitalize()} - Self Intersections')
    ax.set_xscale('log')
    ax.set_xlim(left=global_min, right=global_max_adjusted)  # Apply global scale with adjustment for annotation
    ax.set_xlabel('Self-Intersection C_mwrm (log scale)')
    ax.set_yticks(range(len(project_folders)))
    ax.set_yticklabels(project_folders)
    ax.set_ylabel('Project')

plt.tight_layout()
plt.savefig('self_intersections_scatter.png')
plt.savefig('self_intersections_scatter.svg')
plt.close()
