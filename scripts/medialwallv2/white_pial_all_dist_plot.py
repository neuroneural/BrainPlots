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
    'cortexode_rk4', 'deepcsr',
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

# Global font size and subplot settings
mpl.rcParams.update({'font.size': 16})
subplot_height = 5
subplot_aspect = 1.2

# Creating a color palette
palette = sns.color_palette("husl", len(project_folders))

# Define a list of marker styles, one for each project
markers = ["o", "s", "^", "P", "*", "X", "D", "v"][:len(project_folders)]

# Find the global maximum for 'Intersections White-Pial'
global_max = all_data['Intersections White-Pial'].max()

# Initialize the FacetGrid
g = sns.FacetGrid(all_data, col="Hemisphere", sharex=False, sharey=True, height=subplot_height, aspect=subplot_aspect)
g.set(yscale="log")
g.set(ylim=(1, global_max * 1.1))

# Custom function to plot with markers and annotate max values
def plot_with_markers(data, **kwargs):
    ax = plt.gca()  # Get the current Axes instance on the current figure
    projects_displayed = []
    for i, project in enumerate(project_folders):
        project_data = data[data['Project'] == project]
        if not project_data.empty:
            projects_displayed.append(project)
            # Apply jitter to x-axis positions
            jittered_x = np.random.uniform(-0.2, 0.2, size=len(project_data)) + i
            # Plot each project with a custom marker
            ax.scatter(jittered_x, project_data['Intersections White-Pial'], 
                       alpha=0.6, marker=markers[i], 
                       color=palette[i], s=20)
            # Annotate the maximum value with the same color as the marker
            max_value = project_data['Intersections White-Pial'].max()
            ax.text(i, max_value, f'{max_value:.0f}', color=palette[i], ha='center', va='bottom', fontsize=12)

    # Set custom x-ticks to show project names
    ax.set_xticks(range(len(projects_displayed)))
    ax.set_xticklabels(projects_displayed, rotation=25, ha="right")

# Apply custom plotting function to each subplot in the FacetGrid
g.map_dataframe(plot_with_markers)

# Adjust axis labels and layout
g.set_axis_labels("Project", "White-Pial Intersections")

plt.tight_layout()

# Save the plot
plt.savefig('white_pial_intersections.png')
plt.savefig('white_pial_intersections.svg')
plt.close()
