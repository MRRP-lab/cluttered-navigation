from multiprocessing import connection
import numpy as np
import pygame
import pandas as pd
import os
import glob

from params import Params
from robots import Robots
from environment import Environment

########################## PARAMETERS ###########################################

SAVE_VID = True
VIZGRID = True
FPS = Params.FPS
vid_name = "test.mp4"
tag = "" # replace with informative parameters
viddir = './videos'

# TODO: convert the below to be command-line arguments
time_seconds = Params.time_seconds
sim_time = Params.sim_time
ss = Params.ss # screen size
N = Params.N # num of robots
v = Params.v
gridnum = Params.gridnum
seed = Params.seed

# import the data from generate_demo
sim_data = pd.read_csv("data/demo.csv",dtype=object)


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
screen = pygame.display.set_mode([ss,ss])
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)

x_list = []
y_list = []
theta_list = []
for i in range(sim_data['x'].shape[0]):
    x_list.append(list(map(float,sim_data['x'][i][1:-1].replace(" \n", "").split())))
    y_list.append(list(map(float,sim_data['y'][i][1:-1].replace(" \n", "").split())))


########################## MAIN  ###########################################3

# init robots
robots = Robots(N, v, ss, gridnum, seed)
env = robots.env

robots.coords = np.array([x_list,y_list]).T

running = True

# sim loop
framenum = 0

for time in range(sim_time):
    if(not running):
        break
    # did the user click the close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the background with white
    screen.fill((255,255,255))

    for r in range(robots.num):
        c = robots.coords[r,time]

    for row in range(gridnum):
        for square in range(gridnum):
            if env.obstacles[row,square] == 1:
                rect = pygame.Rect(square * Params.cell_size, row * Params.cell_size, 
                                   Params.cell_size, Params.cell_size)
                pygame.draw.rect(screen, (0, 0, 0), rect)

    # Draws all of the lines needed to make the grid, prints the box numbers (starting at 1)
    # and draws small dots at all of the intersections of the gridlines
    if VIZGRID:
        for points in range(env.grid_num):
            interval = env.ss/env.grid_num
            inter = 0
            cornerNum = 1
            pt = float(points*interval)
            font = pygame.font.SysFont(None, 15)

            pygame.draw.line(screen, (255, 0, 0), (pt, 0), (pt, env.ss), width=1)
            pygame.draw.line(screen, (255, 0, 0), (0, pt), (env.ss, pt), width=1)

    ############################################################################


    centering_offset = np.array([Params.cell_size / 2, Params.cell_size / 2])
    # update robot positions
    for r in range(robots.num):

        c = robots.coords[r,time] * Params.cell_size
        pygame.draw.circle(screen, (0,0,255), np.ceil(c) + centering_offset, max(Params.cell_size/2 - 1, 2))


    clock.tick(FPS)

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
    cmd = str(f"ffmpeg -r {FPS} -f image2 -i {tag}_frames/%04d.png -y -qscale 0 -s {width}x{height} {vid_out}")
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
