class DataLogger():

    def __init__(self, outputFilepath):
        self.outputFilepath = outputFilepath
        self.data = []
    
    def log_line(self, droneID: int, timestep: int, xPos: int, yPos: int):
        line = str(droneID) + "," + str(timestep) + "," + str(xPos) + "," + str(yPos)
        self.data.append(line)
    
    def export_data():
        pass