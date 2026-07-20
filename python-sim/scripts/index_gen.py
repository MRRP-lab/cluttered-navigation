import os
import glob
import pandas as pd
import yaml

# TODO: Centralize the names somewhere so we can do this programmatically instead. Parameters are very fragile this way.
indexed_columns = ["simulation_id", "experiment_name",
                   "num", "seed", "strategy", "gridnum",
                   "density", "disable_collision",
                   "boundary", "boundary_angle",
                   "row_gap", "pin_gap", "noise"]

_here = os.path.dirname(__file__)
DATA_ROOT = os.path.join(_here, "../data/")
INDEX_PATH = os.path.join(DATA_ROOT, "index.csv")
RUNS_DIR = os.path.join(DATA_ROOT, "runs/")


def query_index(params):
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError("Index not found.")
    index = pd.read_csv(INDEX_PATH)

    query = params
    if (type(params) != dict):
        query = vars(params)
    valid_query = {k: v for k, v in query.items() if k in index.columns}
    
    if not valid_query:
        print("Queried columns must exist and be indexed.")
        return index.iloc[0:0]

    mask = pd.Series(True, index=index.index)
    for col, val in valid_query.items():
        mask &= (index[col] == val)
    return index[mask]

# Fetch a single simulation file.
# Depending on the file extension, will return different types.
# *.csv files will return a dataframe.
# *.yaml files will return a dictionary.
# kwargs are passed directly to the file parser.
def fetch_sim_file(sim_id, file, **kwargs):
    path = os.path.join(RUNS_DIR, sim_id, file)
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

    for run_path in glob.glob(RUNS_DIR + "/*"):
        with open(os.path.join(run_path, "params.yaml")) as f:
            run_parameters = yaml.safe_load(f)
            index.append(run_parameters)

    index = pd.DataFrame(data=index, columns=indexed_columns)

    index.to_csv(INDEX_PATH, lineterminator="")



if __name__ == "__main__":
    main()
