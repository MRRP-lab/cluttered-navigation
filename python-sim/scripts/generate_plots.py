import pandas as pd
import numpy as np
import seaborn as sns
from index_gen import query_index, fetch_sim_file

import math
from scipy.stats import wasserstein_distance, kurtosis, probplot, shapiro, skew
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

    if slices is None:
        slice_amt = 5
        gridnum_slice_diff = (run["gridnum"]) / slice_amt 
        slices = [math.floor(slice * gridnum_slice_diff) for slice in range(slice_amt+1)]

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
    #g.set(xlim=(0, run["gridnum"]))
    # passing color=None to refline() uses the hue mapping
    g.refline(y=0, linewidth=2, linestyle="-", color=None, clip_on=False)


    # Define and use a simple function to label the plot in axes coordinates
    def label(x, color, label):
        ax = plt.gca()
        ax.text(0, .2, label, fontweight="bold", color=color,
                ha="left", va="center", transform=ax.transAxes)


    g.map(label, "y")

    # Set the subplots to overlap
    g.figure.subplots_adjust(hspace=-0.6, bottom=0.2)
    g.figure.text(0.08, 0.4, 'X-coordinate', 
              va='center', rotation='vertical', fontsize=18)
    g.set_axis_labels(x_var="Y-coordinate", y_var="X-coordinate", fontsize=18)

    # Remove axes details that don't play well with overlap
    g.set_titles("")
    g.set(yticks=[], ylabel="")
    g.despine(bottom=True, left=True)
    plt.suptitle(title)
    g.tick_params(axis='x', labelsize=18)
    plt.show(block=False)
    basic_stats_qqplot(distribution[distribution["x_slice"] == slices[-1]], title)

#This does the same thing but acts on a series of runs, averaging the distributions first.
def avg_distribution_ridge_plot(runs, title, slices=None):
    sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})
    distributions = []
    gridnum = runs.iloc[0]["gridnum"]
    for idx, run in runs.iterrows():
        playback = fetch_sim_file(run["simulation_id"], PLAYBACK)
        gridnum_slice_diff = (run["gridnum"]) / 10
        if slices is None:
            #slices = [math.floor(slice * gridnum_slice_diff) for slice in range(11)]
            slices = [0, run["gridnum"]]
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
    print(title)
    for x in slices:
        subset = distribution[distribution["x_slice"] == x]["y"]
        print(f"x={x} variance={np.var(subset):.3f} n={len(subset)}")

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
    
    fig, ax = plt.subplots()
    last_slice = distribution["x_slice"].max()
    last_dist = distribution[distribution["x_slice"] == last_slice]["y"]
    sns.histplot(last_dist, stat="count", ax=ax)
    plt.title(title + " (final slice histogram)")
    plt.show(block=False)
    basic_stats(last_dist, title)


# Produce a heatmap from runs where the x dimension is the row spacing and the y dimension is the pin spacing.
# The heatmap is in reference to a default normal distribution because we're interested in seeing how our parameters make our robots deviate from the norm      "experiment-name": "bug2.
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

# Produces a heatmap where x is obstacle noise, y is robot density
def density_noise_heatmap(runs):
    records = []
    for _, run in runs.iterrows():
        id = run["simulation_id"]
        analytics = fetch_sim_file(id, ANALYTICS)
        records.append({
            "noise": run["noise"],
            "density": run["density"],
            "makespan": analytics["makespan"]
        })
    df = pd.DataFrame(records)
    makespans = df.pivot_table(index="density", columns="noise", values="makespan", aggfunc="mean")
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(makespans, annot=True, fmt=".1f", linewidths=.5, cmap="viridis")
    plt.xlabel("Obstacle noise")
    plt.ylabel("Robot density")
    plt.title("Density vs Noise (mean makespan)")
    plt.tight_layout()
    plt.show()

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

# report basic stats as well as a Q-Q plot against the normal distribution.
# seaborn doesn't have qq plots
def basic_stats_qqplot(distribution, title):
    plt.figure()
    (osm, osr), (slope, intercept, r) = probplot(distribution["y"], dist="norm")

    font = {'size': 18}

    plt.rc('font', **font)
    plt.rc('xtick', labelsize=18)
    plt.rc('ytick', labelsize=18)
    plt.scatter(osm, osr, alpha=0.5, s=10)
    plt.plot(osm, slope * np.array(osm) + intercept, 'r--', linewidth=2)
    plt.xlabel("Theoretical Quantiles", size=18)
    plt.ylabel("Sample Quantiles", size=18)
    plt.tight_layout()
    plt.show(block=False)

    print(f"{title}: ")
    stat, p = shapiro(distribution["y"])
    print(f"Shapiro-Wilk: W={stat:.4f}, p={p:.4f}")
    basic_stats(distribution["y"], title)

# report stats for centralized with noise (without noise is the same run every time)
def centralized_stats(runs, title):
    # collect makespan distribution, report mean + variance
    makespan_distr = []

    # collect path lengths,
    # count which ones didn't finish
    not_finished = 0

    path_length_distr = []
    for idx, run in runs.iterrows():
        analytics = fetch_sim_file(run["simulation_id"], ANALYTICS)
        makespan_distr.append(analytics["makespan"])

        # Don't include the path length of robots that don't finish because it can skew the 
        # mean downwards when we don't want that.
        for path in analytics["traversal"]:
            if path["time"] < 0:
                not_finished += 1
                continue
            path_length_distr.append(path["path_len"])

    # report stats.
    print(f"survival rate: {len(path_length_distr) / (len(path_length_distr) + not_finished) * 100:.3f}%")
    basic_stats(makespan_distr, title + " Makespan")
    basic_stats(path_length_distr, title + " Path length")

# Compares the runs with nonzero noise to the average distribution of the runs with 0 noise.
def EMD_stats(runs):
    # First, take the runs with 0 noise and average them
    no_noise = runs[runs["noise"] == 0]
    reference = []
    for idx, run in no_noise.iterrows():
        analytics = fetch_sim_file(run["simulation_id"], ANALYTICS)

        for path in analytics["traversal"]:
            if path["y_f"] < 0:
                continue
            reference.append(path["y_f"])
    

    # Then, produce distributions of EMDs for the other noise levels compared to the 0 average.
    records = []
    for noise, group in runs.groupby("noise", sort=True):
        if noise == 0:
            continue
        for idx, run in group.iterrows():
            analytics = fetch_sim_file(run["simulation_id"], ANALYTICS)
            dist = [p["y_f"] for p in analytics["traversal"] if p["y_f"] >= 0]
            if dist:
                records.append({
                    "noise": noise,
                    "emd": wasserstein_distance(reference, dist)
                })

    df = pd.DataFrame(records)

    fig, ax = plt.subplots()
    sns.boxplot(data=df, x="noise", y="emd", ax=ax)          # spread per noise level
    sns.stripplot(data=df, x="noise", y="emd", ax=ax,        # individual run dots
                  color="black", alpha=0.4, size=3)
    ax.set(xlabel="Perturbation Level", ylabel="EMD vs. 0-Perturbation Reference")
    plt.show()

def basic_stats(distribution, title):
    print(title)
    # Summary stats
    print(f"Samples: {len(distribution)}")
    print(f"Quartiles: {np.percentile(distribution, [25, 50, 75])}")
    print(f"Min/Max: {np.min(distribution)}/{np.max(distribution)}")

    print(f"Mean:     {np.mean(distribution):.4f}")
    print(f"Std:      {np.std(distribution):.4f}")
    print(f"Variance: {np.var(distribution):.4f}")
    print(f"Skewness: {skew(distribution):.4f}")  # want ~0
    print(f"Kurtosis: {kurtosis(distribution):.4f}")  # want ~0

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
    #        "experiment_name": "Gaussian 2",
    #        "disable_collision": False,
    #}
    #results = query_index(query)
    #print(results)

    #distribution_ridge_plot(results.iloc[0], "")
    #plt.show()







    # Does a lower spawn density cause the final distribution to be more bell-shaped? I think it does.
    # A higher spawn density causes more resistance to entering the middle.
    # in some cases, it's harder to tell. Like for seed 2. density is clearly further towards the center, but the furthest extent is the same.
    # Some distribution measurements (variance or quartiles) or kurtosis measurements would be perfect here to back up the claims.
    #query = {
    #    "experiment-name": "Density Skewness",
    #}
    #results = query_index(query)
    #print("results: ", results)
    #for density, group in results.groupby(by="density", sort=True):
    #    avg_distribution_ridge_plot(group, f"Average over 100 seeds with density {density}")

        #for idx, result in results.iterrows():
        #    print(result["density"])
        #    distribution_ridge_plot(result, f"Density: {result['density']}")





    # Compare the performance stats of the centralized runs in comparison to the decentralized run.
    #query = {
    #    "experiment-name": "Centralized test",
    #    "strategy": "centralized",
    #    "noise": 1
    #}
    #results = query_index(query)
    #print(results)
    #centralized_stats(results, "Centralized")
    #
    #query = {
    #    "experiment-name": "Centralized test",
    #    "strategy": "decentralized",
    #    "noise": 1
    #}
    #results = query_index(query)
    #print(results)
    #centralized_stats(results, "Decentralized")

    # Run time stats for centralized
    #basic_stats([374326 , 120657 , 438299 , 296348 , 964136 , 282419 , 91692 , 534769 , 359769 , 128978 , 440450 , 177579 , 319498 , 489990 , 206046 , 243233 , 147214 , 227039 , 167838 , 236991], "Run times")






    #query = {
    #    "experiment-name": "Boundary test",
    #    "noise": 1,
    #}
    #results = query_index(query)

    #for angle, group in results.groupby(by="boundary_angle", sort=True):
    #    avg_distribution_ridge_plot(group, f"Average over 100 seeds with angle {angle}")


    #query = {
    #    "experiment-name": "Boundary test",
    #    "noise": 0,
    #}
    #results = query_index(query)

    #for angle, group in results.groupby(by="boundary_angle", sort=True):
    #    avg_distribution_ridge_plot(group, f"Average over 100 seeds with angle {angle}")



    # First, take the average of the 0 noise. Use it as the baseline.
    # Then, take the EMD of all other EMD tests and plot as a line.
    #query = {
    #    "experiment-name": "EMD test"
    #}
    #results = query_index(query)
    #EMD_stats(results)

    query = {
        "strategy": "bug2",
    }
    results = query_index(query)
    print(results)
    centralized_stats(results, "Modified Bug 2")


    plt.show()
