import os
import glob
import pandas as pd
import yaml

# TODO: Centralize the names somewhere so we can do this programmatically instead. Parameters are very fragile this way.
indexed_columns = ["simulation_id", "experiment_name",
                   "num", "seed", "strategy", "gridnum",
                   "density",
                   "boundary", "boundary_angle", "boundary_offset", 
                   "row_gap", "pin_gap", "noise"]

path = os.path.dirname(__file__)
index_path = os.path.join(path, "index.csv")
runs_dir = os.path.join(path, "runs/")


def query_index(params):
    if not os.path.exists(index_path):
        raise FileNotFoundError("Index not found.")
    index = pd.read_csv(index_path)

    query = params
    if (type(params) != dict):
        query = vars(params)

    cols = [key for key in query if key in index.columns]
    mask = (index[list(cols)] == pd.Series(query)[cols]).all(axis=1)

    result = index[mask]
    return result

# Fetch a single simulation file.
# Depending on the file extension, will return different types.
# *.csv files will return a dataframe.
# *.yaml files will return a dictionary.
# kwargs are passed directly to the file parser.
def fetch_sim_file(sim_id, file, **kwargs):
    path = os.path.join(runs_dir, sim_id, file)
    if not os.path.exists(path):
        raise FileNotFoundError(f"File {file} does not exist for simulation {sim_id}.")
    else:
        _, ext = os.path.splitext(file)
        match(ext):
            case ".csv":
                return pd.read_csv(path, **kwargs)
            case ".yaml":
                with open(path) as f:
                    return yaml.safe_load(f)
            case _:
                raise Exception(f"Unsure how to read data for file {file} for simulation {sim_id}.")

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
