import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import matplotlib as mpl
import numpy as np
import math

# Directories of the projects, sorted alphabetically
project_folders = sorted([
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
    file_path = os.path.join(project, 'white_pial_intersections.csv')
    df = pd.read_csv(file_path)
    df = df[~df['subject_id'].isin(excluded_subject_ids)]
    df['Project'] = project  # Add a column to identify the project
    all_data = pd.concat([all_data, df])

# Global font size and subplot settings
mpl.rcParams.update({'font.size': 16})
subplot_height = 5
subplot_aspect = 1.2

# Creating a happy color palette
palette = sns.color_palette("husl", len(project_folders))

# Find the global maximum for 'Intersections White-Pial'
global_max = all_data['Intersections White-Pial'].max()

# Create a FacetGrid for the subplots, one for each Hemisphere
g = sns.FacetGrid(all_data, col='Hemisphere', sharex=True, sharey=True, height=subplot_height, aspect=subplot_aspect)
g.set(ylim=(0, global_max))

# Plot using strip plot for 'Intersections White-Pial' with happy colors and jitter
g.map_dataframe(sns.stripplot, x='Project', y='Intersections White-Pial', jitter=0.55, dodge=True, palette=palette)

# Adjust the layout
g.set_xticklabels(rotation=25, ha='right')
for ax, hemisphere in zip(g.axes.flatten(), ['lh', 'rh']):
    if hemisphere == 'lh':
        ax.set_title("Left Hemisphere", fontsize=14)
    else:
        ax.set_title('Right Hemisphere', fontsize=14)
    ax.set_ylabel('Intersections White-Pial', fontsize=14)
    ax.set_xlabel('Project', fontsize=14)

    # Getting the positions of the x-ticks (projects)
    xticks = [tick.get_text() for tick in ax.get_xticklabels()]
    
    # Annotating each project's maximum for the respective hemisphere above its scatter plot
    for project in project_folders:
        project_data = all_data[(all_data['Project'] == project) & (all_data['Hemisphere'] == hemisphere)]
        if not project_data.empty:
            project_max = project_data['Intersections White-Pial'].max()
            # Check if the maximum value is finite and valid
            if math.isfinite(project_max):
                # Find the position to place the text
                pos = xticks.index(project)
                ax.text(pos, project_max, f'{project_max:.2f}', color=palette[project_folders.index(project)], ha='center', va='bottom')

plt.tight_layout()

# Save the plot
plt.savefig('combined_white_pial_intersections_scatter_plot.png')
plt.close()
