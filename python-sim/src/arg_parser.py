import argparse
from src.params import Params

def parse_args(raw_args):
    '''Desc: parses arguments for the play_demo.py and generate_demo.py files.
pre: raw_args is a string array
return: a namespace with parsed arguments'''
    parser = argparse.ArgumentParser(
            description="""Set parameters for cluttered-navigation python drone simulation. Override default values by passing arguments. Arguments can be given in the following syntax (using FPS as an example): -f 60 --fps 60 -f=60 --fps=60. In the case of --FPS and -N, they can also be written in all capitals.""",
            prog=raw_args[0])

    parser.add_argument("-f", "--FPS", "--fps", 
                        help="frames per second", 
                        type=int, default=Params.FPS)

    parser.add_argument("-g", "--gridnum", 
                        help="number of grid cells along one side of the window.", 
                        type=int, default=Params.gridnum)

    parser.add_argument("-N", "-n", "--num",
                        help="number of drones in simulation", 
                        type=int, default=Params.num)

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

    parser.add_argument("-B", "--boundary",
                        help="Include to add a reflecting boundary.",
                        default=Params.boundary, action="store_true")

    parser.add_argument("--disable-collision",
                        help="Include to disable robot-robot collision.",
                        default=Params.disable_collision, action="store_true")

    parser.add_argument("-a", "--boundary-angle", 
                        help="Positive and negative reflecting boundary angle in degrees", 
                        type=float, default=Params.boundary_angle)

    parser.add_argument("-d", "-D", "--density", 
                        help="Density of robot group spawn. 0-1, 1 represents perfect compression.",
                        type=float, default=Params.density)

    parser.add_argument("--experiment-name",
                        help="Name an experiment for easier filtering during analysis.",
                        type=str, default=Params.experiment_name)

    parser.add_argument("--pin-gap",
                        help="The horizontal distance between obstacles.",
                        type=int, default=Params.pin_gap)

    parser.add_argument("--row-gap",
                        help="The vertical distance between obstacles.",
                        type=int, default=Params.row_gap)

    parser.add_argument("--noise",
                        help="Max value for randomized x/y displacement of obstacles: noisiness of obstacles.",
                        type=int, default=Params.noise)
    
    parser.add_argument("--simulation-id",
                        help="Useful only when playing back data. When included, other parameters are ignored.",
                        type=str)

    #parse arguments 
    #and return namespace with arguments
    args = parser.parse_args(raw_args[1:])
    return args
