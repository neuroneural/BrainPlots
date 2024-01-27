import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import matplotlib as mpl
import numpy as np
import math

# Directories of the projects, sorted alphabetically
project_folders = sorted([
    'pialnn','topofit',
    'cortexode_rk4', 'deepcsr',
    'cortexode_euler', 'corticalflow', 'freesurfer',
    'vox2cortex'
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

# Set global font size using rcParams
mpl.rcParams.update({'font.size': 16})

# Define subplot size and aspect ratio
subplot_height = 5
subplot_aspect = 1.2

# Create separate subplots for LH Pial, RH Pial, LH White, and RH White with logarithmic y-axis scale
fig, axes = plt.subplots(2, 2, figsize=(2 * subplot_aspect * subplot_height, 2 * subplot_height))

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

# Initialize a list to store maximum values for each subplot
max_values = []

# Create a fixed palette for all projects
fixed_palette = sns.color_palette("husl", len(project_folders))

# Create a dictionary to map each project to a color
color_map = {project: color for project, color in zip(project_folders, fixed_palette)}

for i, (title, data) in enumerate(subplots.items()):
    ax = axes[i // 2, i % 2]

    # Filter projects that have data for this specific subplot
    relevant_projects = data['Project'].unique()

    if not data.empty:
        max_values_per_project = []

        for project in relevant_projects:
            project_data = data[data['Project'] == project]
            project_max = project_data['Self-Intersection C_mwrm'].max()
            if math.isfinite(project_max):
                max_values_per_project.append(project_max)
                ax.text(relevant_projects.tolist().index(project), project_max, f'{project_max:.2f}', 
                        color=color_map[project], ha='center', va='bottom')

        if max_values_per_project:
            max_data = max(max_values_per_project)
            max_values.append(max_data)

        # Plot using the color map
        sns.stripplot(data=data, x='Project', y='Self-Intersection C_mwrm', jitter=0.55, dodge=True, 
                      palette=[color_map[project] for project in relevant_projects], ax=ax)
        ax.set_title(f'{title} - Self Intersections')
        ax.set_ylabel('Self Intersections (log scale)')
        ax.set_xlabel('Project')
        ax.set_yscale('log')

        # Set x-ticks for only relevant projects
        ax.set_xticks(np.arange(len(relevant_projects)))
        ax.set_xticklabels(relevant_projects, rotation=25, ha='right')


# Calculate the global maximum as the maximum of all max_data values
global_max = max(max_values)

# Add a value of 10^5 to the global max
global_max += 1e5

# Set the same y-axis limits for all subplots using the global maximum for the logarithmic scale
for ax in axes.flatten():
    ax.set_ylim(1, global_max)

plt.tight_layout()

# Save the plot
plt.savefig('all_surface_types_self_intersection_log_scale_scatter_plot.png')
plt.close()