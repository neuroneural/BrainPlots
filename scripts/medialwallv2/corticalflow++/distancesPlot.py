import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl

# Set global font size using rcParams
mpl.rcParams.update({'font.size': 16})  # Adjust this value as needed

# Load the data
df = pd.read_csv('distances.csv')

# Prepare the data for plotting
df_melted = df.melt(id_vars=['Project', 'Hemisphere', 'Surface Type'], 
                    value_vars=['Hausdorff Distance', 'ASSD', 'Chamfer Distance'],
                    var_name='Metric', value_name='Value')

# Define a high-contrast color palette
palette = sns.color_palette("Set2", len(df_melted['Metric'].unique()))

# Create a FacetGrid for the subplots with specified size
g = sns.FacetGrid(df_melted, col='Hemisphere', row='Surface Type', hue='Metric', palette=palette, sharex=True, sharey=False, height=5, aspect=1.2)

# Plot using strip plot to add jitter
g.map_dataframe(sns.stripplot, x='Project', y='Value', jitter=0.05, dodge=True)

# Remove existing legends from each subplot, if present
for ax in g.axes.flatten():
    if ax.get_legend():
        ax.get_legend().remove()

# Adjust the layout
g.set_xticklabels(rotation=15, ha='right')  # Adjusting tick labels for all subplots

# Adjusting subplot titles and font size
for ax in g.axes.flatten():
    ax.set_title(ax.get_title(), fontsize=14)  # Adjust title font size

# Add a single, unified legend
# Get handles and labels from the first subplot
handles, labels = g.axes.flatten()[0].get_legend_handles_labels()
new_labels = ['Hausdorff' if label == 'Hausdorff Distance' else 'Chamfer' if label == 'Chamfer Distance' else label for label in labels]
# Add legend to the figure, slightly lower and to the right
leg = g.fig.legend(handles=handles, labels=new_labels, title='Metric', loc='upper right', bbox_to_anchor=(1, 0.8))
plt.setp(leg.get_title(), fontsize=14)  # Adjust legend title font size
plt.setp(leg.get_texts(), fontsize=12)  # Adjust legend text font size

plt.tight_layout()

# Save or display the plot
plt.savefig('distance_metrics_scatter_plot.png')
# plt.show()  # Use this instead of savefig if you want to display the plot directly
