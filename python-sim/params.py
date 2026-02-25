import math

class Params:
    FPS = 55
    time_seconds = 10
    sim_time = time_seconds*FPS
    gridnum = 25 # num of grid cells along one side of the window
    cell_size = 20 # Size of a grid cell in px
    ss = gridnum * cell_size  # screen size (px)
    N = 1
    v = 1  # velocity
    seed = 1

    # TODO: Add reflecting boundary angle here:
    reflectingBoundaryAngle = math.pi / 8

    startLine = 1
    finishLine = 23

    # Variables need to be set for logging purposes because
    # AngleFixed/CountFixed or Centralized/Decentralized cannot be
    # inferred from the sim parameters as they pertain to multiple simulations.

    # These values will be converted directly to the filepaths
    # so spelling & capitalization are important.
    strategy = "Decentralized"   # "Centralized" or "Decentralized"
    experimentType = "BothFixed" # "AngleFixed", "CountFixed", or "BothFixed"
    filename = "ExampleFileName" # TODO: determine what this is to be.   
