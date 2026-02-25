import os
from params import Params

class DataLogger():

    def __init__(self, logType):
        self.logType = logType
        self.data = []

        # Generate filepath from the directory this file is in:
        self.rootFilePath = os.path.dirname(__file__)
        self.workingFilepath = os.path.join(self.rootFilePath, "data", self.logType, Params.strategy, Params.experimentType)
        print(self.workingFilepath)
    
    def log_line_spatial(self, droneID: int, timestep: int, xPos: int, yPos: int):
        line = [Params.strategy, str(droneID), str(timestep), str(xPos), str(yPos)]
        self.data.append(line)
    
    def export_data(self):
        print("example data example data.")