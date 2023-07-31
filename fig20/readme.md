This is a Python script designed for visualizing and analyzing surface-based brain morphometry. The script is particularly useful for comparing different surface reconstruction models.

The program calculates the self-intersection ratio as a metric of comparison between the truth and predicted brain surfaces. The results are plotted in a strip plot, providing an easy comparison across different models.

## Dependencies
The script requires Python and the following Python packages:

matplotlib
seaborn
pandas
numpy
pickle
os
warnings
Data
The data used in this program includes a pickle file ('df.pkl') that contains subjects and surface reconstruction model details.

## Running the Program
To run the program, make sure you have the required data file and Python dependencies. Once everything is set up, you can simply run the script with your Python interpreter. The program will load the data, calculate the metrics, and plot the results.

## Output
The output of the program includes strip plots for different surface models under different conditions (pial, white, and their variants with the medial wall removed). The plots will be saved as .png and .svg files.

## Interpretation
The plots provide an easy comparison across different models in terms of the self-intersection ratio.

## Contributing
If you wish to contribute to this project, feel free to fork the repository, make your changes, and open a pull request. Please ensure your pull request includes a description of the changes and their motivations.

## License
Please see the provided license file for licensing information. If no license file is provided, please contact the repository owner.
