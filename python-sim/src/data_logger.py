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

        self.directory = os.path.join("./data/runs/", self.simulation_id)
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        parameter_path = os.path.join(self.directory, "params.yaml")
        with open(parameter_path, "w") as f:
            yaml.safe_dump(self.sim_args, f)

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
        param_string = json.dumps(params, sort_keys=True).encode("utf-8")
        return hashlib.sha256(param_string).hexdigest()
