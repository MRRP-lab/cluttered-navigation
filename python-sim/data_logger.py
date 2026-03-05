import os
from params import Params

class DataLogger():

    def __init__(self, logType, strategy, angle, N):
        self.logType = logType
        self.strategy = strategy
        self.angle = str(angle)
        self.N = str(N)
        self.data = []

        # Generate filepath from the directory this file is in:
        # Isolate the relative path from the current working directory to the python-sim directory:
        absolutecwd = os.getcwd()
        absoluteFilepath = os.path.dirname(__file__)
        relativeFilepath = "." + absoluteFilepath[len(absolutecwd):]

        # set the filepath of the output data:
        self.workingFilepath = os.path.join(relativeFilepath, "data", self.logType, strategy)
        self.filename = self.logType + "_" + self.strategy + "_Angle" + self.angle + "_N" + self.N + ".txt"

        print("LOGGER: Working filepath to which data will be saved: " + self.workingFilepath)
    
    def log_spatial(self, droneID: int, timestep: int, xPos: int, yPos: int):
        line = [Params.strategy, str(Params.N), str(Params.reflectingBoundaryAngle), str(droneID), str(timestep), str(xPos), str(yPos)]
        self.data.append(line)
    
    def log_makespan(self, droneID, entryTime, exitTime):
        line = [Params.strategy, str(Params.N), str(Params.reflectingBoundaryAngle), str(droneID), str(entryTime), str(exitTime)]
        self.data.append(line)

    def export_data(self):

        if not os.path.exists(self.workingFilepath):
            os.makedirs(self.workingFilepath)

        with open(os.path.join(self.workingFilepath, self.filename), "w") as file:
            for line in self.data:
                file.write(",".join(line) + "\n")
