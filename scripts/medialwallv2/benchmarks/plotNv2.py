import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.ticker import ScalarFormatter

def process_project(project_name, project_path):
    memory_usage_path = f"{project_path}/memory_usage_success.csv"
    gpu_memory_usage_path = f"{project_path}/gpu_memory_usage_log.csv"
    
    read_csv_kwargs = {'on_bad_lines': 'skip'}
    
    memory_usage = pd.read_csv(memory_usage_path, header=None, skiprows=1, names=["Timestamp", "Memory_MB", "Seconds"], **read_csv_kwargs)
    memory_usage = memory_usage.drop(columns="Timestamp")
    memory_usage['Memory_MB'] = pd.to_numeric(memory_usage['Memory_MB'], errors='coerce')
    memory_usage['Seconds'] = pd.to_numeric(memory_usage['Seconds'], errors='coerce')
    memory_usage.dropna(inplace=True)
    
    min_memory_required = memory_usage['Memory_MB'].min()
    execution_times = memory_usage['Seconds'].tolist()
    
    gpu_memory_usage = pd.read_csv(gpu_memory_usage_path, **read_csv_kwargs)
    gpu_memory_usage['GPU Memory Usage (MiB)'] = pd.to_numeric(gpu_memory_usage['GPU Memory Usage (MiB)'], errors='coerce')
    gpu_memory_usage.dropna(inplace=True)
    
    max_gpu_memory = gpu_memory_usage['GPU Memory Usage (MiB)'].max()
    
    return min_memory_required, execution_times, max_gpu_memory

def group_projects(project_stats, project_names):
    grouped_stats = {}
    for name, stats in zip(project_names, project_stats):
        base_name = name.rsplit('_', 1)[0]
        suffix = name.rsplit('_', 1)[-1] if '_' in name else 'both'
        if base_name not in grouped_stats:
            grouped_stats[base_name] = {}
        grouped_stats[base_name][suffix] = stats
    return grouped_stats

def plot_grouped_project_statistics(grouped_stats):
    sns.set(style="whitegrid")
    fig, axs = plt.subplots(1, 3, figsize=(24, 6), dpi=100)

    for idx, metric in enumerate(['MinMemory', 'ExecutionTimes', 'MaxGPU']):
        data = []
        labels = []
        colors = []
        legend_labels = {'pial': False, 'white': False, 'both': False, 'all': False}
        for project_name, data_dict in grouped_stats.items():
            for surface_type, values in data_dict.items():
                if metric == 'ExecutionTimes':
                    for time in values[1]:
                        data.append(time)
                        labels.append(f"{project_name}_{surface_type}")
                else:
                    data.append(values[0] if metric == 'MinMemory' else values[2])
                    labels.append(f"{project_name}_{surface_type}")
                if 'all' in project_name or 'all' in surface_type:  # 'all' projects
                    colors.append('red')
                elif 'both' in project_name or 'both' in surface_type:  # 'both' projects
                    colors.append('orange')
                elif surface_type == 'pial':
                    colors.append('skyblue')
                elif surface_type == 'white':
                    colors.append('lightgreen')
                else:
                    colors.append('grey')
        
        if metric == 'ExecutionTimes':
            sns.boxplot(ax=axs[idx], data=pd.DataFrame({ "Execution Time": data, "Project": labels }), x='Project', y='Execution Time', palette=colors, showfliers=False)
            axs[idx].set_xticklabels(axs[idx].get_xticklabels(), rotation=45, ha="right")
            axs[idx].set_title('Execution Times')
            axs[idx].set_yscale('log')  # Set log scale for y-axis
            axs[idx].set_ylim(10, 150)  # Set y-axis limits
            axs[idx].yaxis.set_major_formatter(ScalarFormatter())
            axs[idx].set_yticks([10,20,30,40,100])  # Set y-axis ticks
            
        else:
            sns.barplot(ax=axs[idx], x=labels, y=data, palette=colors)
            axs[idx].set_xticklabels(labels, rotation=45, ha="right")
            axs[idx].set_title('Minimum Memory Required (MB)' if metric == 'MinMemory' else 'Maximum GPU Memory Used (MiB)')
        
        axs[idx].set_ylabel(metric)

        # Add legend for the first plot
        if metric == 'MinMemory':
            handles, labels = axs[idx].get_legend_handles_labels()
            unique_labels = list(set(labels))
            unique_handles = [handles[labels.index(label)] for label in unique_labels]
            # Create custom legend for surface types
            surface_legend_labels = {
                'pial': 'Pial',
                'white': 'White',
                'both': 'Both',
                'all': 'All'
            }
            surface_legend_patches = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=label) for color, label in zip(['skyblue', 'lightgreen', 'orange', 'red'], surface_legend_labels.values())]
            axs[idx].legend(handles=unique_handles + surface_legend_patches, labels=unique_labels + list(surface_legend_labels.values()), loc='upper right')

    plt.tight_layout()
    plt.savefig('grouped_benchmarks_corrected.png')
    plt.savefig('grouped_benchmarks_corrected.svg')

# Example project folders list
project_folders = [
    ("cortexode_euler_lh_both", "/data/users2/washbee/speedrun/CortexODE_fork/singularity/benchmarks/euler"),
    ("cortexode_rk4_lh_both", "/data/users2/washbee/speedrun/CortexODE_fork/singularity/benchmarks/rk4"),
    ("deepcsr_all_both", "/data/users2/washbee/speedrun/DeepCSR-fork/singularity/benchmarks/allsurf"),
    ("corticalflow_lh_pial", "/data/users2/washbee/speedrun/corticalflow_fork/singularity/benchmarks/cf/pial"),
    ("corticalflow_lh_white", "/data/users2/washbee/speedrun/corticalflow_fork/singularity/benchmarks/cf/white"),
    ("corticalflow++_lh_pial", "/data/users2/washbee/speedrun/corticalflow_fork/singularity/benchmarks/cfpp/pial"),
    ("corticalflow++_lh_white", "/data/users2/washbee/speedrun/corticalflow_fork/singularity/benchmarks/cfpp/white"),
    ("vox2cortex_all_both", "/data/users2/washbee/speedrun/Vox2Cortex_fork/singularity/benchmarks"),
    ("topofit_lh_white", "/data/users2/washbee/speedrun/topofit/singularity/benchmarks"),
    ("pialnn_lh_pial", "/data/users2/washbee/speedrun/PialNN_fork/singularity/benchmarks"),
]

# Process each project
project_stats = []
project_names = []
for name, path in project_folders:
    stats = process_project(name, path)
    project_stats.append(stats)
    project_names.append(name)

# Group projects by name, separating pial and white where applicable
grouped_stats = group_projects(project_stats, project_names)

# Plot the statistics for grouped projects
plot_grouped_project_statistics(grouped_stats)
