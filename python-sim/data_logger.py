import os
from params import Params

class DataLogger():

    def __init__(self, logType):
        self.logType = logType
        self.data = []

        # Generate filepath from the directory this file is in:
        # Isolate the relative path from the current working directory to the python-sim directory:
        absolutecwd = os.getcwd()
        absoluteFilepath = os.path.dirname(__file__)
        relativeFilepath = "." + absoluteFilepath[len(absolutecwd):]

        # set the filepath of the output data:
        self.workingFilepath = os.path.join(relativeFilepath, "data", self.logType, Params.strategy, Params.experimentType)
        self.filename = Params.filename + ".txt"

        print("LOGGER: Working filepath to which data will be saved: " + self.workingFilepath)
    
    def log_line_spatial(self, droneID: int, timestep: int, xPos: int, yPos: int):
        line = [Params.strategy, str(Params.N), str(Params.reflectingBoundaryAngle), str(droneID), str(timestep), str(xPos), str(yPos)]
        self.data.append(line)
    
    def export_data(self):

        if not os.path.exists(self.workingFilepath):
            os.makedirs(self.workingFilepath)

        with open(os.path.join(self.workingFilepath, self.filename), "w") as file:
            for line in self.data:
                file.write(",".join(line) + "\n")
        