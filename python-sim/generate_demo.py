import numpy as np
import pandas as pd
import os

# custom imports
from robots import Robots
from params import Params
from data_logger import DataLogger

########################## PARAMETERS ###########################################

#variables for saving data
sim_data = []
datadir = './data'
if not os.path.exists(datadir):
    os.mkdir(datadir)

# TODO: convert the below to be command-line arguments
FPS = Params.FPS
time_seconds = Params.time_seconds
sim_time = time_seconds*FPS
ss = Params.ss  # screen size
N = Params.N
v = Params.v  # velocity
gridnum = Params.gridnum
seed = Params.seed

startLine = Params.startLine
finishLine = Params.finishLine

# Loggers:
loggerSp = DataLogger("Spatial")
loggerMs = DataLogger("Makespan")

droneEntryTimes = {} # Create a dictionary to store drone's entry times.
                     # That way we can store drone's entry & exit times on one line.

############################### MAIN ##############################################

### Load Configs

robots = Robots(N, v, ss, gridnum, seed, startLine, finishLine)

group_list = [np.zeros(robots.num)]

### Simulation Loop

for t in range(sim_time):

    for r in range(robots.num):
        c = robots.coords[r].copy() # save previous position in case of collision
        # update robot positions
        robots.plinko_movement_policy(r)

        # returns true if there was a collision
        # and moves robot back to original position and reorients

        # Log data to the data logger.        
        loggerSp.log_spatial(r, t, c[0], c[1])

        if c[0] == Params.startLine:
            droneEntryTimes.update({r: t})
        elif c[0] == Params.finishLine:
            entryTime = droneEntryTimes.get(r, -1) # Return negative 1 if the drone
            exitTime = t                           # did not cross the start line.
            #print("Entry time for drone " + str(r) + ": " + str(entryTime) + ". Exit time: " + str(exitTime))
            loggerMs.log_makespan(r, entryTime, exitTime)



    sim_data.append([robots.coords[:,0].copy(), robots.coords[:,1].copy()])

data = pd.DataFrame(data = sim_data, columns = ["x","y"])

outdat = os.path.join(datadir, "demo.csv")

data.to_csv(outdat, lineterminator = "")

# DataLogger data -Madden :
loggerSp.export_data()
loggerMs.export_data()