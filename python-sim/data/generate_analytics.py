import pandas as pd
import yaml
import os
import sys
import subprocess


DATA_ROOT = "./"
RUNS = "runs/"
INDEX = "index.csv"
INDEXER = "index_gen.py"

PLAYBACK = "playback.csv"
ANALYTICS = "analytics.yaml"
PARAMS = "params.yaml"

# Unfortunately, we don't compute any statistics in here that
# come from comparing with another simulation, like earth mover's distance.

# TODO (Per-robot)
# Path length
#   count the amount of times the coodinate changes from one timestep to the next, until the finish.
# Number of collisions per robot(?)
# Number of waits
#   Number of times the coordinate for a single robot is the same in the next timestep, until the finish.

# TODO (Per-simulation)
# Throughput curve (just sort robots by finish time)
# Cell visitation heatmap?
# Entropy of final distribution?
# Skewness?

# Returns a dictionary of calculated metrics from the playback of a file.
# Includes: EMD for each time step.
# Traversal statistics for each drone.
# Finish line makespan
def compute_analytics(playback_path, params_path):
    playback = pd.read_csv(playback_path)
    with open(params_path) as f:
        params = yaml.safe_load(f)
    data = {}

    # Data that is useful for multiple calculations, but in the end we won't be keeping.
    intermediate_data = {}

    # Keep only the earliest start for each bot.
    intermediate_data["starts"] = (playback[playback["x"] == 0]
                                   .loc[lambda df: df.groupby("id")["time"].idxmin()])

    # TODO fix this jank. we need to subtract 1 because gridnum stores the amount of grid cells along the grid, but the value stored is an index.
    intermediate_data["finishes"] = playback[playback["x"] == (params["gridnum"]-1)]

    compute_traversal_stats(playback, data, intermediate_data, params)
    # compute_EMD(playback, data)
    return data

# Given the playback, params, and data, computes various statistics related to traversal and
# adds them to data.
def compute_traversal_stats(playback, data, intermediate_data, params):

    compute_traversal(playback, data, intermediate_data, params)
    compute_makespan(playback, data, intermediate_data, params)

# Entry and exit times per drone. Helps with makespan
# {'entry': [start_time, y], 'exit': [finish_time, y]}
# Given the playback data, add traversal times for each drone to data.
def compute_traversal(playback, data, intermediate_data, params):
    data["traversal"] = []

    # Compute path lengths, merge with other data
    finish_line = params["gridnum"]-1
    ids = playback["id"].unique()

    path_lengths = []

    # Per robot, count movement steps. compare curr and prev positions
    for id in ids:
        path = playback[playback["id"] == id].sort_values(by="time")
        prev = None
        total_len = 0
        for pos in path.itertuples():
            curr = (pos.x, pos.y)
            if prev is not None and curr != prev:
                total_len += 1
            elif pos.x > finish_line:
                break
            prev = curr
        path_lengths.append({"id": id, "path_len": total_len})

    path_len_df = pd.DataFrame(path_lengths)

    # Left join so we can detect when a robot starts but never finishes.
    merged = intermediate_data["starts"].merge(
            intermediate_data["finishes"],
            on="id", how="left", suffixes=("_entry", "_exit")
    ).merge(
        path_len_df,
        on="id", how="left"
    )

    # For each id, iterate over coords and check if it has moved. If so, add to path length.
    # Add to data[that robot's id]

    merged = merged.fillna(-1)
    data["traversal"] = [
            {
                "id": row.id,
                "time": row.time_exit - row.time_entry if row.time_exit > -1 else -1,
                "path_len": row.path_len,
                "y_i": row.y_entry,
                "y_f": row.y_exit
            }
            for row in merged.itertuples()
     ]


# Single number, the finishing makespan
# Given the playback data and data containing traversal info, add the finish line makespan to data.
def compute_makespan(playback, data, intermediate_data, params):
    #last finish time - first finish time
    finishes = intermediate_data["finishes"]["time"]

    # Drones that never finish get a time of -1
    finishes = finishes[finishes > -1]

    first_finish = intermediate_data["finishes"]["time"].min()
    last_finish = intermediate_data["finishes"]["time"].max()
    intermediate_data["last_finish"] = last_finish

    # PyYAML doesn't support numpy types when dumping to file.
    data["makespan"] = int(last_finish - first_finish)

def main():
    # Fetch index
    index = os.path.join(DATA_ROOT, INDEX)
    if not os.path.exists(index):
        print("Index does not exist. Generating...")
        cmd = [sys.executable, INDEXER]
        indexing_result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
                )
        if (indexing_result.returncode == 0):
            print("Simulation re-indexing successful.")
        else:
            print(f"Simulation re-indexing unsuccessful. Exit code: {indexing_result.returncode}")
            exit(1)

    index_data = pd.read_csv(index)
    
    # Compute analytics.yaml for each simulation
    sim_ids = index_data["simulation_id"]
    print("Generating analytics for each simulation.")
    for sim_id in sim_ids:
        SIM_ROOT = os.path.join(DATA_ROOT, RUNS, sim_id)
        playback_path = os.path.join(SIM_ROOT, PLAYBACK)
        params_path = os.path.join(SIM_ROOT, PARAMS)
        if not os.path.exists(playback_path):
            print(f"Could not read {sim_id}. Skipping.")
        else:
            data = compute_analytics(playback_path, params_path)
            analytics = os.path.join(SIM_ROOT, ANALYTICS)
            with open(analytics, "w") as f:
                yaml.safe_dump(data, f)
if __name__ == "__main__":
    main()
