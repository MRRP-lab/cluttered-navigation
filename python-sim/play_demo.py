import numpy as np
import pygame
import pandas as pd
import os
import glob
import sys
from src.environment import Environment
from src.arg_parser import parse_args

########################## PARAMETERS ###########################################
sim_args = parse_args(sys.argv)

ss = sim_args.cell_size * sim_args.gridnum

# Either provide file, or specify parameters. If param not specified, use defaults.
# Search for the recorded simulation that matches exactly.
def find_simulation(params):
    if not os.path.exists("./data/index.csv"):
        raise FileNotFoundError("Index not found.")
    index = pd.read_csv("./data/index.csv")
    print(index)
    query = vars(params)
    print(query)
    cols = [key for key in query if key in index.columns]
    mask = (index[list(cols)] == pd.Series(query)[cols]).all(axis=1)
    result = index[mask]

    match_count = len(result)
    if (match_count == 0):
        raise FileNotFoundError("A simulation with the supplied parameters is not indexed.")
    elif (match_count > 1):
        # TODO shouldn't be a generic exception. couldnt be asked to deal with figuring it out.
        # we should make the user specify which one.
        raise Exception("Ambiguous parameter set, could be a few different simulations")
    else:
        return result.iloc[0]

SAVE_VID = True
VIZGRID = True
vid_name = "test.mp4"
tag = "" # replace with informative parameters
viddir = './videos'

# import the data from generate_demo
sim_data = find_simulation(sim_args)
run_directory = os.path.join("./data/runs/", sim_data["simulation_id"])

replay_data = pd.read_csv(os.path.join(run_directory, "playback.csv"),dtype=object)
########################## SETUP ##########################

if not os.path.exists(viddir):
    os.mkdir(viddir)
vid_out = os.path.join(viddir, vid_name)

# set up folder for saving frames
if SAVE_VID:
    try:
        os.makedirs(tag+"_frames")
    except OSError:
        pass

width = ss # for vid
height = ss # for vid

# set up env
pygame.init()
screen = pygame.display.set_mode([ss,ss], pygame.SRCALPHA)
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)

x_list = []
y_list = []
theta_list = []
for i in range(replay_data['x'].shape[0]):
    x_list.append(list(map(float,replay_data['x'][i][1:-1].replace(" \n", "").split())))
    y_list.append(list(map(float,replay_data['y'][i][1:-1].replace(" \n", "").split())))


########################## MAIN  ###########################################3

# init robots
env = Environment(sim_args.gridnum, sim_args.seed,
                  sim_args.boundary, sim_args.boundary_angle, sim_args.boundary_offset)

coords = np.array([x_list,y_list]).T

running = True

# sim loop
framenum = 0

for time in range(len(replay_data)):
    if(not running):
        break
    # did the user click the close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the background with white
    screen.fill((255,255,255))

    for r in range(sim_args.num):
        c = coords[r,time]

    # Draw the start and finish Lines:
    pygame.draw.rect(screen, (255, 255, 0),
                     pygame.Rect(sim_args.cell_size * env.start_line, 0, sim_args.cell_size, ss))

    pygame.draw.rect(screen, (0, 255, 0),
                     pygame.Rect(sim_args.cell_size * (env.finish_line - 1), 0, sim_args.cell_size, ss))

    # Draw obstacles:
    for row in range(sim_args.gridnum):
        for square in range(sim_args.gridnum):
            if env.obstacles[row,square] == 1:
                rect = pygame.Rect(square * sim_args.cell_size, row * sim_args.cell_size, 
                                   sim_args.cell_size, sim_args.cell_size)
                pygame.draw.rect(screen, (0, 0, 0), rect)

    # Draws all of the lines needed to make the grid, prints the box numbers (starting at 1)
    # and draws small dots at all of the intersections of the gridlines
    if VIZGRID:
        for points in range(env.grid_num):
            interval = ss/env.grid_num
            pt = float(points*interval)

            pygame.draw.line(screen, (255, 0, 0), (pt, 0), (pt, ss), width=1)
            pygame.draw.line(screen, (255, 0, 0), (0, pt), (ss, pt), width=1)

    ############################################################################


    centering_offset = np.array([sim_args.cell_size / 2, sim_args.cell_size / 2]) + np.array([1, 1])
    # update robot positions
    for r in range(sim_args.num):

        c = coords[r,time] * sim_args.cell_size
        pygame.draw.circle(screen, (0,0,255), np.ceil(c) + centering_offset, max(sim_args.cell_size/2 - 1, 2))


    clock.tick(sim_args.FPS)

    # save frame to disk
    if SAVE_VID:
        fname = tag + "_frames/%04d.png" % framenum
        pygame.image.save(screen, fname)
        framenum += 1

    # update the display
    pygame.display.flip()

# quit
pygame.quit()

########################## SAVE TO VID ###########################################

if SAVE_VID:
    cmd = str(f"ffmpeg -r {sim_args.FPS} -f image2 -i {tag}_frames/%04d.png -y -qscale 0 -s {width}x{height} {vid_out}")
    os.system(cmd)

    # remove frames when done: python should wait...
    # TODO switch to using subprocess lib
    # or maybe pathlib
    files = glob.glob('./'+tag+'_frames/*.png')
    for f in files:
        try:
            os.unlink(f)
        except OSError as e:
            print("Error: %s : %s" % (f, e.strerror))
            pass

    try:
        os.rmdir('./'+tag+'_frames')
    except OSError as e:
        pass
