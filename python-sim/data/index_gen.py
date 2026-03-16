import os
import glob
import pandas as pd
import yaml

# TODO: Centralize the names somewhere so we can do this programmatically instead. Parameters are very fragile this way.
indexed_columns = ["simulation_id", "experiment_name",
                   "N", "seed", "strategy",
                   "density",
                   "boundary", "boundary_angle", "boundary_offset"]

path = os.path.dirname(__file__)
index_path = os.path.join(path, "index.csv")
runs_dir = os.path.join(path, "runs/")

def main():
    index = []

    for run_path in glob.glob(runs_dir + "/*"):
        with open(os.path.join(run_path, "params.yaml")) as f:
            run_parameters = yaml.safe_load(f)
            index.append(run_parameters)

    index = pd.DataFrame(data=index, columns=indexed_columns)

    index.to_csv(index_path, lineterminator="")



if __name__ == "__main__":
    main()
