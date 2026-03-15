import os
import math
import yaml
import pandas as pd

# Temporary until we generate simulation_ids
from datetime import datetime


class DataLogger():

    def __init__(self, sim_args):
        self.sim_args = sim_args
        print(sim_args)

        # set the filepath of the output data, coming up with an identifier by hashing the params.
        self.simulation_id = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        self.data = []

        # Generate filepath from the directory this file is in:
        # Isolate the relative path from the current working directory to the python-sim directory:

        self.directory = os.path.join("./data/runs/", self.simulation_id)
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        parameter_path = os.path.join(self.directory, "params.yaml")
        with open(parameter_path, "w") as f:
            yaml.safe_dump(vars(self.sim_args), f)

    def add_data(self, data):
        self.data.append(data)

    # Export data. Compute no additional calculations, as that is the job of the analytics script.
    def export_data(self):

        playback_path = os.path.join(self.directory, "playback.csv")

        sim_data = pd.DataFrame(data = self.data, columns = ["x","y"])
        sim_data.to_csv(playback_path, lineterminator = "")
