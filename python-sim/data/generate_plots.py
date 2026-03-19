import pandas as pd
import numpy as np
import seaborn as sns
from index_gen import query_index, fetch_sim_file

from scipy.stats import wasserstein_distance
import matplotlib.pyplot as plt

# PLOT IDEAS
# Main ideas: Compare centralized vs. decentralized.

# Makespan:
# Makespan vs. drone count (each strategy)
# Makespan vs. angle (each strategy)

# Traversal:
# Avg traversal time vs. drone count (violin or scatter?) (each strategy)
# Vs. angle (each strategy)

# EMD of one reference distribution compared to an interval of some other parameter.
#   (single vs. agg.?)
#   0 noise obstacles to lots of noise?

# So, compare metrics of each. Makespan (agg. vs. agg.), traversal (agg. vs. agg.).

PLAYBACK = "playback.csv"
ANALYTICS = "analytics.yaml"
PARAMS = "params.yaml"

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

# Other settings
SHOW_MEANS = True
SHOW_LEGEND = True

# Given the playback data, add earth movers distance per timestep to data.
# TODO what distributions are we comparing???
def compute_EMD():
    
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
    xValues, yValues = zip(*data)
    # Print stats for y-values (dependent variable)
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

def EMD_by_noise(reference_dist, other_dists):
    pass


if __name__ == "__main__":
    # Compute our plots.
    # The user should be able to specify a range of simulation parameters to aggregate data with and plot specific simulations/aggregations against each other using various plot types.
    # Makespan: We separate by buckets (centralized vs. decentralized), then aggregate over each.

    # wasserstein line plot?

    # Makespan vs. number for a fixed angle
    constants = {
            "experiment-name":
        }

    results = query_index(constants)
    


    # EMD
    # Matrix of graphs. Each graph is EMD of density x density for various levels of noise.
    # For each combination of obstacle density and drone density:
    #    plot the EMD between:
    #       The finish distribution of the robots at:
    #       0 noise, compared with increasing levels of noise.
    data = []

    for id in results["simulation_id"]:
        analytics = fetch_sim_file(id, ANALYTICS)
        params = fetch_sim_file(id, PARAMS)
        # playback = fetch_sim_file(id, PLAYBACK)
        data.append([analytics["makespan"], params["num"]])
        # finishes = playback[playback["x"] == params["gridnum"]]["y"]
        # finishes.plot(kind="hist", bins=20)


    data = pd.DataFrame(data=data, columns=["makespan", "num"]).sort_values("num")
    sns.lineplot(data=data, x="num", y="makespan",
                 estimator=None)
    

    plt.show()

