import os
import pandas as pd

# Specify the directory where your CSV files are located
directory_path = '.'

# Specify the name of the output CSV file
output_file_name = 'concatenated.csv'

# List to hold data from each CSV file
data_frames = []

# Loop through all files in the directory
for filename in os.listdir(directory_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(directory_path, filename)
        # Read the CSV file and append it to the list
        df = pd.read_csv(file_path)
        data_frames.append(df)

# Concatenate all data frames
concatenated_df = pd.concat(data_frames, ignore_index=True)

# Save the concatenated DataFrame to a new CSV file
output_path = os.path.join(directory_path, output_file_name)
concatenated_df.to_csv(output_path, index=False)

print(f'All CSV files have been concatenated into {output_path}')
