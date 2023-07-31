# Import the Png2Svg class from png2svglinlin module. This class will be used to convert PNG images to SVG format.
from png2svglinlin import Png2Svg

# Import the os module which provides functions for interacting with the operating system.
import os

# List all files and directories in the 'new-data/' directory.
os.listdir('new-data/')

# Loop over each file in the 'new-data/' directory.
for f in os.listdir('new-data/'):
    
    # Construct the full file path by joining the directory name 'new-data/' and the file name.
    png_file = os.path.join('new-data', f)
    
    # Construct the full save path for the new SVG file. 
    # We use the original file name (f[:-3] removes the original extension) and add 'svg' as the new extension.
    save_to = os.path.join('data-layout-meshes-v2/', f[:-3] + 'svg')
    
    # Call the Png2Svg class and pass in the paths of the PNG file and where to save the SVG file.
    Png2Svg(png_file, save_to)


