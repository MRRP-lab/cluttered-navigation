import os
import yaml
import pandas as pd
import hashlib
import json

class DataLogger():

    def __init__(self, sim_args):
        self.sim_args = vars(sim_args)

        self.simulation_id = self.hash_params(self.sim_args)
        self.sim_args["simulation_id"] = self.simulation_id
        self.data = []

        # Generate filepath from the directory this file is in:
        # Isolate the relative path from the current working directory to the python-sim directory:
        # TODO: abort the actual simulation if the simulation_id already exists because that means we have the same parameters.
        # IDK what we should do if the experiment name differs though. Overwrite the params.yaml but don't go forward with the simulation?
        self.directory = os.path.join("./data/runs/", self.simulation_id)
        if not self.this_sim_exists():
            os.makedirs(self.directory)
        else:
            print("This simulation seems to exist already. Aborting")
            exit(0)

        parameter_path = os.path.join(self.directory, "params.yaml")
        with open(parameter_path, "w") as f:
            yaml.safe_dump(self.sim_args, f)

    def this_sim_exists(self):
        sim_dir = os.path.join("./data/runs/", self.simulation_id)
        return os.path.exists(sim_dir)

    # Add a single row of data
    def append_data(self, data):
        self.data.append(data)

    # Add many rows of data where each row is an element in data
    def extend_data(self, data):
        self.data.extend(data)

    # Export data. Compute no additional calculations, as that is the job of the analytics script.
    def export_data(self):

        playback_path = os.path.join(self.directory, "playback.csv")

        sim_data = pd.DataFrame(data = self.data, columns = ["time", "id", "x", "y"])
        sim_data.to_csv(playback_path, lineterminator = "")

    def hash_params(self, params):
        # Delete params that don't affect playback whatsoever to avoid duplicating data.
        copy = params.copy()
        del copy["FPS"]
        # del copy["experiment_name"] # TODO keeping it tentatively...
        del copy["cell_size"]

        param_string = json.dumps(copy, sort_keys=True).encode("utf-8")
        return hashlib.sha256(param_string).hexdigest()
