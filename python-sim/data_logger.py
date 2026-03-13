import os
import math

class DataLogger():

    def __init__(self, sim_args):
        self.sim_args = sim_args
        self.angle_deg = math.degrees(sim_args.boundary_angle)
        self.data = []

        # Generate filepath from the directory this file is in:
        # Isolate the relative path from the current working directory to the python-sim directory:
        absolutecwd = os.getcwd()
        absoluteFilepath = os.path.dirname(__file__)
        relativeFilepath = "." + absoluteFilepath[len(absolutecwd):]

        # set the filepath of the output data:
        self.workingFilepath = os.path.join(relativeFilepath, "data", self.sim_args.strategy)
        self.filename = self.sim_args.strategy +\
        "_Angle" + str(self.angle_deg) +\
        "_N" + str(self.sim_args.N) + ".txt"

    def log_spatial(self, droneID: int, timestep: int, xPos: int, yPos: int):
        line = [self.sim_args.strategy,
                str(self.sim_args.N),
                str(self.angle_deg),
                str(droneID),
                str(timestep),
                str(xPos), str(yPos)]

        self.data.append(line)

    def log_makespan(self, droneID, entryTime, exitTime):
        line = [self.sim_args.strategy,
                str(self.sim_args.N),
                str(self.angle_deg),
                str(droneID),
                str(entryTime), str(exitTime)]
        self.data.append(line)

    def export_data(self):

        if not os.path.exists(self.workingFilepath):
            os.makedirs(self.workingFilepath)

        with open(os.path.join(self.workingFilepath, self.filename), "w") as file:
            for line in self.data:
                file.write(",".join(line) + "\n")
