import pandas as pd
import seaborn as sns
from index_gen import query_index, fetch_sim_file

from scipy.stats import wasserstein_distance
import matplotlib.pyplot as plt

# TODO
# Distribution
# - ridge plot for measuring distribution at each row of obstacles. (where is the spreading concentrated?)
# - Quantile tracking swarm percentile x positions over time.
# - Throughput curve (just sort robots by finish time)

# Phase diagrams
# - Robot density x obstacle noise, colored by collision rate or makespan. (can we find a jamming transition?)
# - Boundary angle x noise, colored by EMD?

# Throughput curves
# - Overlaid throughput curves for different strategies on the same plot. Calculate area between as a cost of a certain strategy.
# - Throughput curves for increasing robot density

# Things to watch for:
# - The jamming transition
# - The price of decentralized


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


# Generates a ridge plot for a single run.
# This ridge plot shows how the distribution of robots
# evolves as the robots traverse the field.
# Along the super-y axis (each individual distribution) is the x-coordinate slice that each distribution is along.
# Inside each distribution: We measure the distribution of robots entering this x slice at the y-coordinates.
# Optional slices parameter is at which x slices to take distributions at.
def distribution_ridge_plot(run, title, slices=None):
    sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})
    run_id = run["simulation_id"]
    playback = fetch_sim_file(run_id, PLAYBACK)
    print(run["gridnum"])
    if slices is None:
        slices = [x for x in range(0, run["gridnum"], 10)]

    distribution = []
    frames = []
    for x in slices:
        #At each slice, count the rows at each y value.
        at_slice = playback[playback["x"] == x]
        first_entries = at_slice.groupby("id")["time"].idxmin()

        y_values = at_slice.loc[first_entries, "y"].reset_index(drop=True)

        frames.append(pd.DataFrame({"x_slice": x, "y": y_values}))

    distribution = pd.concat(frames, ignore_index=True)

    # Initialize the FacetGrid object
    pal = sns.cubehelix_palette(10, rot=-.25, light=.7)
    g = sns.FacetGrid(distribution, row="x_slice", hue="x_slice", aspect=15, height=0.5, palette=pal)

    # Draw the densities in a few steps
    g.map(sns.kdeplot, "y",
          bw_adjust=.5, clip_on=False,
          fill=True, alpha=1, linewidth=1.5)
    g.map(sns.kdeplot, "y", clip_on=False, color="w", lw=2, bw_adjust=.5)
    g.set(xlim=(0, run["gridnum"]))
    # passing color=None to refline() uses the hue mapping
    g.refline(y=0, linewidth=2, linestyle="-", color=None, clip_on=False)


    # Define and use a simple function to label the plot in axes coordinates
    def label(x, color, label):
        ax = plt.gca()
        ax.text(0, .2, label, fontweight="bold", color=color,
                ha="left", va="center", transform=ax.transAxes)


    g.map(label, "y")

    # Set the subplots to overlap
    g.figure.subplots_adjust(hspace=-0.5)

    # Remove axes details that don't play well with overlap
    g.set_titles("")
    g.set(yticks=[], ylabel="")
    g.despine(bottom=True, left=True)
    plt.suptitle(title)
    plt.show(block=False)

#This does the same thing but acts on a series of runs, averaging the distributions first.
def avg_distribution_ridge_plot(runs, title, slices=None):
    sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})
    distributions = []
    gridnum = runs.iloc[0]["gridnum"]
    for idx, run in runs.iterrows():
        playback = fetch_sim_file(run["simulation_id"], PLAYBACK)
        if slices is None:
            slices = [x for x in range(0, run["gridnum"], 10)]

        frames = []
        for x in slices:
            #At each slice, count the rows at each y value.
            at_slice = playback[playback["x"] == x]
            first_entries = at_slice.groupby("id")["time"].idxmin()

            y_values = at_slice.loc[first_entries, "y"].reset_index(drop=True)
            frames.append(pd.DataFrame({"x_slice": x, "y": y_values}))

        distributions.append(pd.concat(frames, ignore_index=True))
    
    # Now, we average the distribution on each x_slice (can we just add them together)
    distribution = pd.concat(distributions, ignore_index=True)
    # Initialize the FacetGrid object
    pal = sns.cubehelix_palette(10, rot=-.25, light=.7)
    g = sns.FacetGrid(distribution, row="x_slice", hue="x_slice", aspect=15, height=0.5, palette=pal)

    # Draw the densities in a few steps
    g.map(sns.kdeplot, "y",
          bw_adjust=.5, clip_on=False,
          fill=True, alpha=1, linewidth=1.5)
    g.map(sns.kdeplot, "y", clip_on=False, color="w", lw=2, bw_adjust=.5)
    g.set(xlim=(0, gridnum))
    # passing color=None to refline() uses the hue mapping
    g.refline(y=0, linewidth=2, linestyle="-", color=None, clip_on=False)


    # Define and use a simple function to label the plot in axes coordinates
    def label(x, color, label):
        ax = plt.gca()
        ax.text(0, .2, label, fontweight="bold", color=color,
                ha="left", va="center", transform=ax.transAxes)


    g.map(label, "y")

    # Set the subplots to overlap
    g.figure.subplots_adjust(hspace=-0.5)

    # Remove axes details that don't play well with overlap
    g.set_titles("")
    g.set(yticks=[], ylabel="")
    g.despine(bottom=True, left=True)
    plt.suptitle(title)
    plt.show(block=False)



# Produce a heatmap from runs where the x dimension is the row spacing and the y dimension is the pin spacing.
# The heatmap is in reference to a default normal distribution because we're interested in seeing how our parameters make our robots deviate from the norm.
def EMD_heatmap(runs):
    
    # Pre-load metrics
    data = {}
    for id in runs["simulation_id"]:
        data[id] = {
                "analytics": fetch_sim_file(id, ANALYTICS)
                }
    pass

# Produces a heatmap from the runs. x dimension is obstacle noise, y is robot amount.
# TODO aggregate makespans across seeds.
def makespan_heatmap(runs):
    # Pre-load metrics
    records = []
    for id in runs["simulation_id"]:
        analytics = fetch_sim_file(id, ANALYTICS)
        # we can just loop over itertuples instead so we don't need to do this.
        run = runs[runs["simulation_id"] == id].iloc[0]

        records.append({
            "noise": run["noise"],
            "num": run["num"],
            "makespan": analytics["makespan"]
        })
    df = pd.DataFrame(records)

    makespans = df.pivot_table(index="num", columns="noise", values="makespan", aggfunc="mean")

    # Draw a heatmap with the numeric values in each cell
    f, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(makespans, annot=True, fmt=".1f", linewidths=.5, ax=ax)
    plt.show(block=False)

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
                "analytics": fetch_sim_file(id, ANALYTICS)
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
            # Don't include the reference, it's a useless data point
            if row["noise"] == 0:
                continue
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
    
    print(result["EMD"].max())
    g = sns.relplot(
        data=result,
        x="noise", y="EMD",
        row="row_gap", col="density",
        kind="line",
        height=2, aspect=1.5, legend=False,
    )
    g.fig.suptitle("Robot EMD Sensitivity Analysis", y=1.02)
    plt.show(block=False)

if __name__ == "__main__":

    # Compute our plots.
    # The user should be able to specify a range of simulation parameters to aggregate data with and plot specific simulations/aggregations against each other using various plot types.
    #query = {
    #        "experiment-name": "Heatmap test",
    #        "boundary": True,
    #        "gridnum": 150,
    #        "density": 1,
    #    }

    #results = query_index(query)
    #makespan_heatmap(results)

    #query = {
    #        "experiment-name": "Gaussian test",
    #        "boundary": True,
    #        "num": 50,
    #        "gridnum": 50,
    #        "row_gap": 2,
    #        "pin_gap": 1,
    #    }
    #results = query_index(query)
    #print(results)
    #distribution_ridge_plot(results.iloc[0], "No collision")
    #distribution_ridge_plot(results.iloc[1], "Collision")

    #plt.show()
    # Does a lower spawn density cause the final distribution to be more bell-shaped? I think it does.
    # A higher spawn density causes more resistance to entering the middle.
    # in some cases, it's harder to tell. Like for seed 2. density is clearly further towards the center, but the furthest extent is the same.
    # Some distribution measurements (variance or quartiles) or kurtosis measurements would be perfect here to back up the claims.
    query = {
        "experiment-name": "Density Skewness",
    }
    results = query_index(query)
    print("results: ", results)
    for density, group in results.groupby(by="density", sort=True):
        avg_distribution_ridge_plot(group, f"Average over 10 seeds with density {density}")

        #for idx, result in results.iterrows():
    #    print(result["density"])
    #    distribution_ridge_plot(result, f"Density: {result['density']}")
    plt.show()
