import numpy as np
import pandas as pd
import os
import sys

# custom imports
from robots import Robots
from demo_parser import parse_args

from data_logger import DataLogger

########################## PARAMETERS ###########################################

#variables for saving data
sim_data = []
datadir = './data'
if not os.path.exists(datadir):
    os.mkdir(datadir)

#parse arguments
sim_args = parse_args(sys.argv)

#assign variables from arguments
FPS = sim_args.FPS
time_seconds = sim_args.time_seconds
sim_time = time_seconds*FPS
gridnum = sim_args.gridnum
N = sim_args.N
seed = sim_args.seed
strategy = sim_args.strategy

spawnpoint = (sim_args.X, sim_args.Y)
spawn_density = sim_args.density

boundary = sim_args.boundary
boundary_angle = sim_args.boundary_angle
boundary_offset = sim_args.boundary_offset

start_line = 1
finish_line = gridnum-1


# Loggers:
logger_sp = DataLogger(sim_args)
logger_ms = DataLogger(sim_args)

drone_entry_times = {} # Create a dictionary to store drone's entry times.
                     # That way we can store drone's entry & exit times on one line.

############################### MAIN ##############################################

### Load Configs

robots = Robots(N, spawnpoint, spawn_density, gridnum, seed, start_line, finish_line, boundary, boundary_angle, boundary_offset)

group_list = [np.zeros(robots.num)]

### Simulation Loop

for t in range(sim_time):
    robots.update_movement()

    sim_data.append([robots.coords[:,0].copy(), robots.coords[:,1].copy()])
    
    # not ideal to do low-level logic in high level logic like this.
    # better to handle the logic inside a handler within the logger after passing it all the
    # relevant robot data.
    for r in range(len(robots.coords)):
        x = robots.coords[r,0]
        y = robots.coords[r,1]
        logger_sp.log_spatial(r, t, x, y)

        if x == start_line:
            drone_entry_times.update({r: t})
        elif x == finish_line:
            entryTime = drone_entry_times.get(r, -1) # Return negative 1 if the drone
            exitTime = t                           # did not cross the start line.
            logger_ms.log_makespan(r, entryTime, exitTime)

data = pd.DataFrame(data = sim_data, columns = ["x","y"])

outdat = os.path.join(datadir, "demo.csv")

data.to_csv(outdat, lineterminator = "")

logger_sp.export_data()
logger_ms.export_data()

