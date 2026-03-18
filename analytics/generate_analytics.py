import pandas as pd
import yaml
import os
import sys
import subprocess

DATA_ROOT = "../python-sim/data/"
RUNS = "runs/"
INDEX = "index.csv"
INDEXER = "index_gen.py"

PLAYBACK = "playback.csv"
ANALYTICS = "analytics.yaml"
PARAMS = "params.yaml"

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

# Returns a dictionary of calculated metrics from the playback of a file.
# Includes: EMD for each time step.
# Traversal statistics for each drone.
# Finish line makespan
def compute_analytics(playback_path, params_path):
    playback_data = pd.read_csv(playback_path)
    with open(params_path) as f:
        params = yaml.safe_load(f)
    data = {}

    compute_traversal_stats(playback_data, params, data)
    compute_EMD(playback_data, data)
    return data

# Given the playback, params, and data, computes various statistics related to traversal and
# adds them to data.
def compute_traversal_stats(playback, params, data):
    compute_traversal(playback, data, params)
    compute_makespan(playback, data, params)
    pass
# Entry and exit times per drone. Helps with makespan
# {'entry': [start_time, y], 'exit': [finish_time, y]}
# Given the playback data, add traversal times for each drone to data.
def compute_traversal(playback, data, params):
    data["traversal"] = []
    starts = playback[playback["x"] == 0]
    finishes = playback[playback["x"] == params["gridnum"]]

    # Left join so we can detect when a robot starts but never finishes.
    merged = starts.merge(finishes, on="id", how="left", suffixes=("_entry", "_exit"))
    merged = merged.fillna(-1)
    data["traversal"] = [
            {
                "id": row.id,
                "entry": [row.time_entry, row.y_entry],
                "exit": [row.time_exit, row.y_exit]
            }
            for row in merged.itertuples()
     ]

# Single number, the finishing makespan
# Given the playback data and data containing traversal info, add the finish line makespan to data.
def compute_makespan(playback, data, num):
    pass

# Given the playback data, add earth movers distance per timestep to data.
def compute_EMD(playback, data):
    pass


if __name__ == "__main__":
    main()
