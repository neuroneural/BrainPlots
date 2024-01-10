import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Load real data
csv_file = 'surface_distances_normalized.csv'
real_data = pd.read_csv(csv_file)

# Transpose and reshape real_data to match the format for plotting
melted_real_data = real_data.melt(id_vars=['subject_id', 'Project'], var_name='Surface_Measure', value_name='Value')
melted_real_data[['Surface', 'Measure']] = melted_real_data['Surface_Measure'].str.rsplit('_', n=1, expand=True)
melted_real_data.drop(columns='Surface_Measure', inplace=True)

# Find min and max values in the real data for scaling
real_data_min = melted_real_data['Value'].min()
real_data_max = melted_real_data['Value'].max()

# Generate scaled dummy data for other projects
np.random.seed(0)
data = []
num_patients = 107
num_projects = 7
measures = ['hausdorff', 'assd', 'chamfer']
surfaces = ['lh_pial', 'lh_white', 'rh_pial', 'rh_white']

for project in range(1, num_projects):
    for surface in surfaces:
        for measure in measures:
            # Generate random data in the range 0 to 1, then scale to real data range
            values = np.random.rand(num_patients) * (real_data_max - real_data_min) + real_data_min
            for value in values:
                data.append([surface, project, measure, value])

dummy_df = pd.DataFrame(data, columns=['Surface', 'Project', 'Measure', 'Value'])

# Combine real data with dummy data
combined_df = pd.concat([melted_real_data, dummy_df])

# [Rest of the plotting code remains the same]



# Plotting with logarithmic scale
fig, axes = plt.subplots(nrows=1, ncols=4, figsize=(20, 5), constrained_layout=True)
handles, labels = None, None

for i, surface in enumerate(surfaces):
    ax = axes[i]
    surface_data = combined_df[combined_df['Surface'] == surface]
    bp = sns.boxplot(x='Project', y='Value', hue='Measure', data=surface_data, ax=ax, palette='Set2')
    ax.set_yscale('log')  # Set y-axis to logarithmic scale
    ax.set_title(f'Surface: {surface}')
    ax.set_xlabel('Project')
    ax.set_ylabel('Value (log scale)')
    ax.legend_.remove()
    if i == 0:
        handles, labels = ax.get_legend_handles_labels()

fig.legend(handles, labels, loc='lower center', ncol=3, title='Measure', bbox_to_anchor=(0.5, -0.1))
plt.suptitle('Comparison of Measures Across Projects and Surfaces (Log Scale)', fontsize=16)
plt.savefig('surface_distances_plot_log_scale.png', format='png', bbox_inches='tight')
plt.savefig('surface_distances_plot_log_scale.svg', format='svg', bbox_inches='tight')
plt.show()
