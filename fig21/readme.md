# Collision Count Analysis
This repository contains Python code used to analyze the collision count for different models.

## Description
The python script reads pickled files grouped4.pkl and grouped5.pkl, which contain the data for analysis. The data is grouped and then plotted. The analysis includes a comparison between the models on the basis of a 'cut or no cut' scenario, in which the data is compared before and after the medial wall is removed.

The models used in the analysis are as follows:

- CortexODE
- CorticalFlow
- DeepCSR
- FreeSurfer
- Vox2Cortex
The script sorts the dataframe by model and whether a cut was made or not. It then uses seaborn to generate a stripplot and a boxplot to visualize the data.

## Libraries Used
- matplotlib
- seaborn
- pandas
- numpy
- pickle
- os

## Plot Description
The plot consists of a stripplot and a boxplot. Each boxplot is grouped by the model, and the stripplot points are categorized by whether the medial wall was removed or not.

The y-axis represents the cross-surface intersections in percentage, and each model's boxplot represents the statistical distribution of these values for that particular model.

Two data visualizations are saved, one in PNG format (FIG21.png) and another in SVG format (FIG21.svg).

## Instructions to Run
To run the script, you must have the appropriate libraries installed, as well as Python 3. You should be able to run it in a standard Python environment or a Jupyter notebook.

Note: Before running the script, make sure the grouped4.pkl and grouped5.pkl files are in the same directory as the script.

## Contact
For any questions or concerns about the script, please contact the repository owner.
