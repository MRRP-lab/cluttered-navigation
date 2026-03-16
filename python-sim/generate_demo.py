import os
import sys

# custom imports
from robots import Robots
from environment import Environment
from arg_parser import parse_args

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

spawn_density = sim_args.density

boundary = sim_args.boundary
boundary_angle = sim_args.boundary_angle
boundary_offset = sim_args.boundary_offset

start_line = 1
finish_line = gridnum-1


# Loggers:
# TODO add experiment name parameter
playback_log = DataLogger(sim_args)

############################### MAIN ##############################################

### Load Configs
env = Environment(gridnum, seed, start_line, finish_line, boundary, boundary_angle, boundary_offset)
robots = Robots(N, spawn_density, seed)
robots.set_environment(env)

### Simulation Loop

for t in range(sim_time):
    robots.update_movement()
    playback_log.add_data([robots.coords[:,0].copy(), robots.coords[:,1].copy()])

playback_log.export_data()
