import pandas as pd
import numpy as np
import seaborn as sns
from index_gen import query_index, fetch_sim_file

from scipy.stats import wasserstein_distance
import matplotlib.pyplot as plt

# TODO
# Distribution
# - ridge plot for measuring distribution at each row of obstacles. (where is the spreading concentrated?)
# - Quantile tracking swarm percentile x positions over time.
# - Throughput curve (just sort robots by finish time)
# - Cell visitation heatmap?

# Phase diagrams
# - Heatmap with axes as row spacing x pin spacing colored by EMD or makespan.
# - Robot density x obstacle noise, colored by collision rate or makespan. (can we find a jamming transition?)
# - Boundary angle x noise, colored by final distribution entropy?

# Throughput curves
# - Overlaid throughput curves for different strategies on the same plot. Calculate area between as a cost of a certain strategy.
# - Throughput curves for increasing robot density

# Things to watch for:
# - The jamming transition
# - The price of decentralized
# - Does the output fit a normal distribution?
# - Effective diffusion coefficient, at each row compute the mean squared lateral displacement


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

# EMD
# for obstacle density levels present in runs
#     for drone density levels present in runs
#         locate reference distribution for 0 noise
#         for noise levels
#             extract final distribution
#             calculate EMD, join with runs
def EMD_by_noise(runs):
    result_list = []

    # Pre-load metrics
    data = {}
    for id in runs["simulation_id"]:
        data[id] = {
                "analytics": fetch_sim_file(id, "analytics.yaml")
                }

    # Select unique groupings of these parameters
    grouped = runs.groupby(["density", "row_gap"])

    for (density, row_gap), group in grouped:

        # There should only be one possible reference here.
        reference = group[group["noise"] == 0]

        if reference.empty:
            print(f"no 0 noise reference for density {density}, row_gap {row_gap}.")
            continue

        # DF to series to id to reference final distribution
        reference_id = reference.iloc[0]["simulation_id"]
        reference_analytics = data[reference_id]["analytics"]
        reference_distr = [tr["y_f"] for tr in reference_analytics["traversal"]]

        for _, row in group.iterrows():
            curr_analytics = data[row["simulation_id"]]["analytics"]
            curr_distr = [tr["y_f"] for tr in curr_analytics["traversal"]]
            emd = wasserstein_distance(reference_distr, curr_distr)
            result_list.append({
                "noise": row["noise"],
                "EMD": emd,
                "row_gap": row["row_gap"],
                "density": row["density"]
                })
    result = pd.DataFrame(result_list)
    print(result)
    g = sns.relplot(
        data=result,
        x="noise", y="EMD",
        row="row_gap", col="density",
        kind="line",
        height=2, aspect=1.5, legend=False,
    )
    g.fig.suptitle("Robot EMD Sensitivity Analysis", y=1.02)
    plt.show()

if __name__ == "__main__":

    # Compute our plots.
    # The user should be able to specify a range of simulation parameters to aggregate data with and plot specific simulations/aggregations against each other using various plot types.

    constants = {
            "experiment-name": "EMD calc",
        }

    results = query_index(constants)

    by_pin_gap = results.groupby("pin_gap")
    for pin_gap, group in by_pin_gap:
        print("pin gap: ", pin_gap)
        EMD_by_noise(group)

