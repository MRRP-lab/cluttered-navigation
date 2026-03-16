import sys

# custom imports
from src.robots import Robots
from src.environment import Environment
from src.arg_parser import parse_args

from src.data_logger import DataLogger

########################## PARAMETERS ###########################################
sim_args = parse_args(sys.argv)

# TODO add experiment name parameter
playback_log = DataLogger(sim_args)

############################### MAIN ##############################################

### Load Configs
env = Environment(sim_args.gridnum, sim_args.seed,
                  sim_args.boundary, sim_args.boundary_angle, sim_args.boundary_offset)
robots = Robots(sim_args.num, sim_args.density, sim_args.seed)
robots.set_environment(env)

### Simulation Loop

no_progress = 0
while no_progress < 10:
    progress = robots.update_movement()
    if (not progress):
        no_progress += 1
    else:
        no_progress = 0
    playback_log.add_data([robots.coords[:,0].copy(), robots.coords[:,1].copy()])

playback_log.export_data()
