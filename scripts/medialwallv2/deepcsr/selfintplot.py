import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl

# Set global font size using rcParams
mpl.rcParams.update({'font.size': 16})  # Adjust this value as needed

# Load the data
df = pd.read_csv('distances.csv')

# Define subplot size and aspect ratio
subplot_height = 5  # Adjust height
subplot_aspect = 1.2  # Adjust aspect ratio

# Create a FacetGrid for the subplots
g = sns.FacetGrid(df, col='Hemisphere', row='Surface Type', sharex=True, sharey=False, height=subplot_height, aspect=subplot_aspect)

# Plot using strip plot for 'Self-Intersection C_mwrm' to add jitter
g.map_dataframe(sns.stripplot, x='Project', y='Self-Intersection C_mwrm', jitter=0.05, dodge=True)

# Adjust the layout
g.set_xticklabels(rotation=15, ha='right')  # Adjusting tick labels for all subplots

# Adjusting subplot titles, axis labels, and font size
for ax in g.axes.flatten():
    ax.set_title(ax.get_title(), fontsize=14)  # Adjust title font size
    ax.set_ylabel('Self Intersections', fontsize=14)  # Set y-axis label and font size
    ax.set_xlabel(ax.get_xlabel(), fontsize=14)  # Set x-axis label and font size

plt.tight_layout()

# Save or display the plot
plt.savefig('self_intersection_scatter_plot.png')
# plt.show()  # Use this instead of savefig if you want to display the plot directly
