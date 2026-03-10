import argparse
from params import Params

def parse_args(raw_args):
    '''Desc: parses arguments for the play_demo.py and generate_demo.py files.
pre: raw_args is a string array
return: a namespace with parsed arguments'''
    parser = argparse.ArgumentParser(
            description="""Set parameters for cluttered-navigation python drone simulation. Override default values by passing arguments.  Arguments can be given in the following syntax (using FPS as an example): -f 60 --fps 60 -f=60 --fps=60.  In the case of --FPS and -N, they can also be written in all capitals.  In the case of -N and -v, they do NOT have long-form counterparts.  """,
            prog=raw_args[0])

    parser.add_argument("-f", "--FPS", "--fps", 
                        help="frames per second", 
                        type=int, default=Params.FPS)

    parser.add_argument("-t", "--time-seconds", 
                        help="simulation runtime in seconds", 
                        type=int, default=Params.time_seconds)

    parser.add_argument("-g", "--gridnum", 
                        help="number of grid cells along one side of the window.", 
                        type=int, default=Params.gridnum)

    parser.add_argument("-N", "-n", 
                        help="number of drones in simulation", 
                        type=int, default=Params.N)

    parser.add_argument("-v", 
                        help="drone speed (velocity)", 
                        type=int, default=Params.v)

    parser.add_argument("-s", "--strategy", 
                        help="choose decentralized or centralized strategy", 
                        choices=["centralized", "decentralized"],
                        type=str, default = Params.strategy)

    parser.add_argument("-c", "--cell-size", 
                        help="size in pixels (px) of one grid cell", 
                        type=int, default=Params.cell_size)

    parser.add_argument("-r", "--seed", 
                        help="seed for randomized drone and obstacle placement.", 
                        type=int, default=Params.seed)

    #parse arguments 
    #and return namespace with arguments
    args = parser.parse_args(raw_args[1:])
    return args
