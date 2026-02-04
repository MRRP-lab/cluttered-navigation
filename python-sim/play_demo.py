from multiprocessing import connection
import numpy as np
import pygame
import random
import pandas as pd
import os
import glob

import utils
from robots import *
from environment import *

########################## PARAMETERS ###########################################

SAVE_VID = True
VIZGRID = True
FPS = 55
vid_name = "test.mp4"
tag = "" # replace with informative parameters
viddir = './videos'

# TODO: convert the below to be command-line arguments
time_seconds = 20
sim_time = time_seconds*FPS
ss = 500 # screen size
N = 10
v = 1
gridnum = 10 # grid cells on each side

# import the data from generate_demo
sim_data = pd.read_csv("data/demo.csv",dtype=object)

# set up environment
env = Environment(ss, gridnum)


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
    theta_list.append(list(map(float,sim_data['theta'][i][1:-1].replace(" \n", "").split())))


########################## MAIN  ###########################################3

# init robots
robots = Robots(N, v, ss, gridnum)

robots.coords = np.array([x_list,y_list]).T
robots.angles = np.array(theta_list)

running = True

# sim loop
framenum = 0
env.initRobotsPer()
env.initPrevRobotsPer()
env.initPrevShade()
env.initFading()

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
        env.robotUpdates(c)

    for cell in env.robotsPer.keys():
            fade = 10

            concentration = env.robotsPer[cell]
            shade = 255 - (5*concentration)
            if shade < 0:
                shade = 0

            # find way to make it stop fading, if robot enters again

            interval = env.ss/env.grid_num

            boxes = env.grid_num**2
            xHold = boxes%env.grid_num
            yHold = boxes//env.grid_num

            x = xHold*interval
            y = yHold*interval

            pygame.draw.rect(screen, (255, shade, 255), (x,y,interval,interval), 0)

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

            for points2 in range(env.grid_num):
                corner = int(cornerNum + (inter/interval))
                pygame.draw.circle(screen, (255, 0, 0), (pt, inter), 3)

                img = font.render(str((points2*env.grid_num)+points), True, (255, 0, 0))
                screen.blit(img, (pt +5 , inter +5))
                cornerNum += 1
                inter += interval
            #extra row on the far right
            pygame.draw.circle(screen, (255, 0, 0), (env.ss, pt), 3)
    ############################################################################



    # update robot positions
    for r in range(robots.num):

        c = robots.coords[r,time]

        # draw a solid blue circle in the center
        pygame.draw.circle(screen, (0,0,1), np.ceil(c), 5)

        # draw a line to show orientation
        pygame.draw.line(screen, (0,0,1), np.ceil(c), np.ceil(c+15*np.array([np.cos(robots.angles[time,r]),np.sin(robots.angles[time,r])])), 3)


    clock.tick(60)

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
