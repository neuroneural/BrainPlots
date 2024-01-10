import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Define the surfaces you're analyzing
surfaces = ['lh_pial', 'lh_white', 'rh_pial', 'rh_white']

# Load real data
csv_file = 'surface_distances_normalized.csv'
real_data = pd.read_csv(csv_file)

# Transpose and reshape real_data to match the format for plotting
melted_real_data = real_data.melt(id_vars=['subject_id', 'project'], var_name='Surface_Measure', value_name='Value')
melted_real_data[['Surface', 'Measure']] = melted_real_data['Surface_Measure'].str.rsplit('_', n=1, expand=True)
melted_real_data.drop(columns='Surface_Measure', inplace=True)

# Replicate 'deepcsr' data for all projects
num_projects = 7
replicated_data = []
for project in range(1, num_projects):
    project_data = melted_real_data.copy()
    project_data['project'] = f'project_{project}'  # Assign new project label
    replicated_data.append(project_data)

# Combine original 'deepcsr' data with replicated data
combined_df = pd.concat([melted_real_data] + replicated_data)

# Plotting with logarithmic scale
fig, axes = plt.subplots(nrows=1, ncols=4, figsize=(20, 5), constrained_layout=True)
handles, labels = None, None

for i, surface in enumerate(surfaces):
    ax = axes[i]
    surface_data = combined_df[combined_df['Surface'] == surface]
    bp = sns.boxplot(x='project', y='Value', hue='Measure', data=surface_data, ax=ax, palette='Set2')
    ax.set_yscale('log')  # Set y-axis to logarithmic scale
    ax.set_title(f'Surface: {surface}')
    ax.set_xlabel('Project')
    ax.set_ylabel('Value (log scale)')
    
    # Rotate x-axis labels
    ax.set_xticklabels(ax.get_xticklabels(), rotation=20)

    ax.legend_.remove()
    if i == 0:
        handles, labels = ax.get_legend_handles_labels()

fig.legend(handles, labels, loc='lower center', ncol=3, title='Measure', bbox_to_anchor=(0.5, -0.1))
plt.suptitle('Comparison of Measures Across Projects and Surfaces (Log Scale)', fontsize=16)
plt.savefig('surface_distances_plot_log_scale.png', format='png', bbox_inches='tight')
plt.savefig('surface_distances_plot_log_scale.svg', format='svg', bbox_inches='tight')
plt.show()
