import numpy as np
import pygame
import pandas as pd
import os
import glob
import sys

from robots import Robots
from demo_parser import parse_args

########################## PARAMETERS ###########################################
args = parse_args(sys.argv)

FPS = args.FPS
time_seconds = args.time_seconds
sim_time = time_seconds * FPS
gridnum = args.gridnum
cell_size = args.cell_size
ss = args.cell_size * gridnum
N = args.N
seed = args.seed
strategy = args.strategy

SAVE_VID = True
VIZGRID = True
vid_name = "test.mp4"
tag = "" # replace with informative parameters
viddir = './videos'

#parse arguments
args = parse_args(sys.argv)

start_line = 1
finish_line = gridnum-1
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
screen = pygame.display.set_mode([ss,ss], pygame.SRCALPHA)
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
robots = Robots(N, gridnum, seed, start_line, finish_line)
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

    # Draw the start and finish Lines:
    for row in range(gridnum):
        for square in range(gridnum):
            if env.is_startLine(square, row):
                rect = pygame.Rect(square * cell_size, row * cell_size, 
                                   cell_size, cell_size)
                pygame.draw.rect(screen, (255, 255, 0), rect)
            elif env.is_finishLine(square, row):
                rect = pygame.Rect(square * cell_size, row * cell_size, 
                                   cell_size, cell_size)
                pygame.draw.rect(screen, (0, 255, 0), rect)
    
    # Draw obstacles:
    for row in range(gridnum):
        for square in range(gridnum):
            if env.obstacles[row,square] == 1:
                rect = pygame.Rect(square * cell_size, row * cell_size, 
                                   cell_size, cell_size)
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


    centering_offset = np.array([cell_size / 2, cell_size / 2]) + np.array([1, 1])
    # update robot positions
    for r in range(robots.num):

        c = robots.coords[r,time] * cell_size
        pygame.draw.circle(screen, (0,0,255), np.ceil(c) + centering_offset, max(cell_size/2 - 1, 2))


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
