import pandas as pd

# Read the CSV file
filename = 'deepcsrWtPlCollision.csv'
df = pd.read_csv(filename, header=None, names=['idx', 'f name', 'collision', 'points'])

# Write the dataframe to an Excel file
df.to_excel('filename.xlsx', index=False)