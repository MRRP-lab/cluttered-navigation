import pandas as pd
import os
import sys
import subprocess

DATA_ROOT = "../python-sim/data/"
RUNS = "runs/"
INDEX = "index.csv"
INDEXER = "index_gen.py"

PLAYBACK = "playback.csv"

def main():
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

    sim_ids = index_data["simulation_id"]
    print("Generating analytics for each simulation.")
    for sim_id in sim_ids:
        playback_path = os.path.join(DATA_ROOT, RUNS, sim_id, PLAYBACK)
        if not os.path.exists(playback_path):
            print(f"Could not read {sim_id}. Skipping.")
        else:
            data = compute_analytics(playback_path)

def compute_analytics(playback_file):
    raw_playback_data = pd.read_csv(playback_file)
    # Compute Wasserstein EMD (all time steps? which EMD?)
    # Makespan
    # Traversal

# Entry and exit times per drone.
def compute_traversal():
    pass

# Earth movers distance per timestep
def compute_EMD():
    pass

# Single number, the finishing makespan
def compute_makespan():
    pass

if __name__ == "__main__":
    main()
