import sys

# custom imports
from src.robots import Robots
from src.environment import Environment
from src.arg_parser import parse_args
from src.spawn_layout import SpawnLayout

from src.data_logger import DataLogger

########################## PARAMETERS ###########################################
sim_args = parse_args(sys.argv)

# TODO add experiment name parameter
playback_log = DataLogger(sim_args)

############################### MAIN ##############################################

### Initialize things
start_line = 0

spawn_layout = SpawnLayout(sim_args.seed, sim_args.num, sim_args.density,
                           sim_args.gridnum, start_line
                           )
env = Environment(sim_args.gridnum, sim_args.seed,
                  sim_args.boundary, sim_args.boundary_angle, spawn_layout.boundary_line_y_offset,
                  sim_args.row_gap, sim_args.pin_gap, sim_args.noise
                  )
robots = Robots(sim_args.num, sim_args.seed, spawn_layout.offsets)
robots.set_environment(env)

# In the case of a centralized strategy, it drives itself and produces stats all at once.
# We'd have to give the java program information about both the robots and environment. Regardless, we should still be starting in this file. The robot class should set itself up based on the strategy. Abstract the strategy into another class. Decentralized gets a robot controller, and the centralized one gets a robot controller.
# The thing is, decentralized currently doesn't drive itself, and stats are collected from the outside.
# The centralized strategy will drive itself and the stats are collected from the outside and published back via protobuf.
# It feels to me like we need another architecture rework. It won't be too big, the relevant code isn't very much. Maybe i should just make them behave similarly. Change the decentralized stuff to produce its stats all at once instead of piece by piece. I like this idea.
# Also make it appear to drive itself from the outside. It's probably important for the outside to drive everything.
# All of this also calls into question the greater structuring of the project... this is the python simulator but we're deferring to a java solution. Also this python version is turning into the main project. It feels like we're slowly losing the plot in terms of organization. I placed the submodules in some places that don't make much sense when you think about it.

no_progress = 0
time = 0

while no_progress < 10:
    progress = robots.update_movement()
    if (not progress):
        no_progress += 1
    else:
        no_progress = 0

    coordinate_data = robots.get_coordinate_data()
    coordinate_data = [[time] + row for row in coordinate_data]

    playback_log.extend_data(coordinate_data)
    time += 1
playback_log.export_data()
