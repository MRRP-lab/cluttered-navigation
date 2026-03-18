import os
import yaml
import pandas as pd
import numpy as np

from scipy.stats import wasserstein_distance
import matplotlib.pyplot as plt

ROOT_FOLDER = '/mnt/files/files/school/wwu/research/robotics/simulationSwarm/cluttered-navigation/plinko-drones/output-data/root'
MAKESPAN_DIR = 'Makespan'
SPATIAL_DIR = 'Spatial'
STRATEGIES = ['Centralized', 'Decentralized']
FOLDER_TYPES = ['BothFixed', 'AngleFixed', 'CountFixed']

# Plotting options
PLOT_COLORS = [
    "#6060ff", # [0]: data points in scatter plots, box color in boxplots
    "#ff2020", # [1]: best-fit line in scatter plots, median line in boxplots
    "#000000", # [2]: whiskers and caps in boxplots
    "#ffff60"  # [3]: outlier (flier) points in boxplots
]
FIGURE_SIZE = (7, 6)
BOX_WIDTH = 0.5
FONT_SIZE = 12

# Best-fit line degree (1=linear, 2=quadratic, 3=cubic, etc.)
BEST_FIT_DEGREE = 1
BEST_FIT_LABEL = {1: 'Linear Best Fit', 2: 'Quadratic Best Fit', 3: 'Cubic Best Fit'}

# Margin of error/confidence interval
CONFIDENCE_LEVEL = 0.95

# Title templates for all graphs (customize as needed)
TITLE_BARCHART_MAKESPAN_STRATEGY = 'Makespan by Strategy (Angle & Count Fixed)'
TITLE_BARCHART_TRAVERSAL_STRATEGY = 'Average Traversal Time by Strategy (Angle & Count Fixed)'
TITLE_BARCHART_EMD_STRATEGY = 'EMD by Strategy (Angle & Count Fixed)'
TITLE_MAKESPAN_DRONECOUNT_CENTRALIZED = 'Makespan vs. Drone Count for Centralized Strategy'
TITLE_TRAVERSAL_DRONECOUNT_CENTRALIZED = 'Average Traversal Time vs. Drone Count for Centralized Strategy'
TITLE_EMD_DRONECOUNT_CENTRALIZED = 'EMD vs. Drone Count for Centralized Strategy'
TITLE_MAKESPAN_DRONECOUNT_DECENTRALIZED = 'Makespan vs. Drone Count for Decentralized Strategy'
TITLE_TRAVERSAL_DRONECOUNT_DECENTRALIZED = 'Average Traversal Time vs. Drone Count for Decentralized Strategy'
TITLE_EMD_DRONECOUNT_DECENTRALIZED = 'EMD vs. Drone Count for Decentralized Strategy'
TITLE_MAKESPAN_ANGLE_CENTRALIZED = 'Makespan vs. Angle for Centralized Strategy'
TITLE_TRAVERSAL_ANGLE_CENTRALIZED = 'Average Traversal Time vs. Angle for Centralized Strategy'
TITLE_EMD_ANGLE_CENTRALIZED = 'EMD vs. Angle for Centralized Strategy'
TITLE_MAKESPAN_ANGLE_DECENTRALIZED = 'Makespan vs. Angle for Decentralized Strategy'
TITLE_TRAVERSAL_ANGLE_DECENTRALIZED = 'Average Traversal Time vs. Angle for Decentralized Strategy'
TITLE_EMD_ANGLE_DECENTRALIZED = 'EMD vs. Angle for Decentralized Strategy'

# Other settings
SHOW_MEANS = True
SHOW_LEGEND = True



# Given the playback data, add earth movers distance per timestep to data.
# TODO what distributions are we comparing???
def compute_EMD(playback, data, intermediate_data, params):
    
    pass

def printDescriptiveStats(title, dataDict):
    """Print descriptive statistics for each group in a pretty way with a title."""
    # Print a formatted table of stats for each group (e.g., strategy)
    print(f"\n=== {title} ===")
    for group, values in dataDict.items():
        arr = np.array(values)
        if arr.size == 0:
            print(f"{group}: No data.")
            continue
        # Compute and print common descriptive statistics
        stats = {
            'Count': len(arr),
            'Mean': np.mean(arr),
            'Std': np.std(arr, ddof=1) if len(arr) > 1 else 0.0,
            'Min': np.min(arr),
            '25%': np.percentile(arr, 25),
            'Median': np.median(arr),
            '75%': np.percentile(arr, 75),
            'Max': np.max(arr)
        }
        print(f"{group}:")
        for k, v in stats.items():
            print(f"  {k:>6}: {v:>10.3f}" if isinstance(v, float) else f"  {k:>6}: {v}")

def plotScatter(data, title, xLabel, yLabel, xIntTicks=False):
    """Reusable scatter plot with best-fit line and descriptive stats."""
    # Early exit if no data
    if not data:
        print(f"No data for {title}"); return
    xValues, yValues = zip(*data)
    # Print stats for y-values (dependent variable)
    printDescriptiveStats(title, {yLabel: yValues})
    plt.figure(figsize=FIGURE_SIZE)
    plt.scatter(xValues, yValues, label='Data Points', color=PLOT_COLORS[0])  # Data points (same as box color)
    # Add best-fit line if more than one point
    if len(xValues) > 1:
        coeffs = np.polyfit(xValues, yValues, BEST_FIT_DEGREE)
        poly = np.poly1d(coeffs)
        xFit = np.linspace(min(xValues), max(xValues), 100)
        plt.plot(xFit, poly(xFit), color=PLOT_COLORS[1], label=BEST_FIT_LABEL.get(BEST_FIT_DEGREE, 'Best Fit'))  # Best-fit line (same as median)
    plt.title(title, fontsize=FONT_SIZE)
    plt.xlabel(xLabel, fontsize=FONT_SIZE)
    plt.ylabel(yLabel, fontsize=FONT_SIZE)
    # Set x-axis ticks for integer-based axes
    if xIntTicks:
        xMin, xMax = int(min(xValues)), int(max(xValues))
        if xLabel.startswith('Drone Count'):
            plt.xticks(np.arange(0, xMax+1, 5))
        else:
            step = 5 if xMax - xMin > 6 else 1
            plt.xticks(np.arange(xMin, xMax+1, step))
    if SHOW_LEGEND:
        plt.legend()
    plt.show()

def plotBox(samplesDict, title, yLabel):
    """Reusable boxplot with descriptive stats for each group (e.g., strategy)."""
    printDescriptiveStats(title, samplesDict)
    
    # Check if both strategies have data
    if 'Centralized' not in samplesDict or 'Decentralized' not in samplesDict:
        print(f"Skipping plot '{title}': Missing data for one or both strategies.\n")
        return
    
    # Check if both strategies have non-empty data
    if len(samplesDict['Centralized']) == 0 or len(samplesDict['Decentralized']) == 0:
        print(f"Skipping plot '{title}': One or both strategies have no data points.\n")
        return
    
    plt.figure(figsize=FIGURE_SIZE)
    plt.boxplot(
        [samplesDict['Centralized'], samplesDict['Decentralized']],
        tick_labels=['Centralized', 'Decentralized'],
        patch_artist=True,
        showmeans=SHOW_MEANS,
        meanprops={"marker":"o","markerfacecolor":"white","markeredgecolor":"black"},
        widths=BOX_WIDTH,
        boxprops=dict(color=PLOT_COLORS[0], facecolor=PLOT_COLORS[0]), # Box color (same as scatter data points)
        medianprops=dict(color=PLOT_COLORS[1]), # Median line (same as best-fit line)
        whiskerprops=dict(color=PLOT_COLORS[2]), # Whiskers
        capprops=dict(color=PLOT_COLORS[2]), # Caps
        flierprops=dict(markerfacecolor=PLOT_COLORS[3], marker='o') # Outliers
    )
    plt.title(title, fontsize=FONT_SIZE)
    plt.ylabel(yLabel, fontsize=FONT_SIZE)
    plt.xlabel('Strategy', fontsize=FONT_SIZE)
    plt.show()

if __name__ == "__main__":
    # Compute our plots
    pass
