import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

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
        grouped_stats.setdefault(base_name, {}).update({suffix: stats})
    return grouped_stats

def plot_min_memory_required(grouped_stats):
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(18, 6), dpi=100)

    # Define colors for each category
    colors = {
        'pial': 'skyblue', 
        'white': 'lightgreen', 
        'both': 'grey',  # Default color for "Both"
        'all': 'orange'   # Special color for projects with "_all"
    }
    bar_width = 0.25

    sorted_projects = sorted(grouped_stats.keys())
    x_positions = np.arange(len(sorted_projects))

    # Legend tracking to ensure labels are added only once
    legend_labels = {'pial': False, 'white': False, 'both': False, 'all': False}

    for idx, project in enumerate(sorted_projects):
        project_data = grouped_stats[project]
        
        # Determine if the project is a special "_all" project
        is_all_project = 'all' in project
        is_pial_project = 'pial' in project
        is_white_project = 'white' in project
        is_both_project = 'both' in project
        color_for_all_or_both = colors['all'] if is_all_project else colors['both']

        for variant, stats in project_data.items():
            # Assign colors based on variant and whether it's a special "_all" project
            print(variant)
            bar_color = None
            if is_all_project:
                bar_color = colors['all']
            elif is_pial_project:
                bar_color = colors['pial']
            elif is_white_project:
                bar_color = colors['white']
            elif is_both_project:
                bar_color = colors['both']
                
            label = 'all' if is_all_project else variant.lower()
            
            # Adjust bar positions for 'pial' and 'white'; use the center position for 'both' or '_all'
            if variant in ['pial', 'white']:
                pos_offset = idx + (bar_width if variant == 'white' else -bar_width)/2.0
                ax.bar(pos_offset, stats[0], color=colors[variant], width=bar_width, edgecolor='black', label=label if not legend_labels[variant] else "")
                legend_labels[variant] = True
            elif is_all_project:
                ax.bar(idx, stats[0], color=colors['all'], width=bar_width*4.0, edgecolor='black', label=label if not legend_labels[label] else "")
                legend_labels[label] = True
            else:
                ax.bar(idx, stats[0], color=colors['both'], width=bar_width*2.0, edgecolor='black', label=label if not legend_labels[label] else "")
                legend_labels[label] = True

    ax.set_xticks(x_positions)
    ax.set_xticklabels(sorted_projects, rotation=45, ha="right")
    ax.set_title('Minimum Memory Required (MB)')

    # Create legend
    handles, labels = ax.get_legend_handles_labels()
    # Sort handles and labels to maintain a consistent order
    sorted_handles_labels = sorted(zip(handles, labels), key=lambda x: x[1])
    sorted_handles, sorted_labels = zip(*sorted_handles_labels)
    ax.legend(sorted_handles, sorted_labels, title="Type")

    plt.tight_layout()
    plt.show()
    plt.savefig('grouped_benchmarks_corrected.png')

# Define your project folders here
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
project_stats = [process_project(name, path) for name, path in project_folders]
project_names = [name for name, _ in project_folders]

# Group processed data for plotting
grouped_stats = group_projects(project_stats, project_names)

# Plot the minimum memory required with the corrected legend
plot_min_memory_required(grouped_stats)
