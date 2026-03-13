import math

class Params:
    FPS = 10
    time_seconds = 10
    sim_time = time_seconds*FPS

    gridnum = 50 # num of grid cells along one side of the window
    cell_size = 10 # Size of a grid cell in px
    ss = gridnum * cell_size  # screen size (px)
    N = 1
    v = 1  # velocity
    seed = 1
    strategy = "decentralized"

    boundary_angle = math.pi / 8
