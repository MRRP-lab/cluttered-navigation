import math

class Params:
    # Params mainly for sim generation
    gridnum = 50 # num of grid cells along one side of the window
    N = 100
    seed = 1
    strategy = "decentralized"

    X = 0
    Y = math.floor(gridnum / 2)
    density = 1

    boundary = False
    boundary_angle = 22.5
    boundary_offset = -10

    # Params mainly for playback
    FPS = 10
    cell_size = 10 # Size of a grid cell in px
