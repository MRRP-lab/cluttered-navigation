import sys

# custom imports
from src.arg_parser import parse_args
from src.sim_factory import prepare_simulation

from src.data_logger import DataLogger

########################## PARAMETERS ###########################################
sim_args = parse_args(sys.argv)

playback_log = DataLogger(sim_args)

############################### MAIN ##############################################

### Initialize things

simulation = prepare_simulation(sim_args)
simulation.run()

# Playback data consists of rows of the structure [time, robot id, x, y]
playback_log.extend_data(simulation.extract_data())
playback_log.export_data()
