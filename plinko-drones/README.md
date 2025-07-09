# PLINKO DRONES

A simulation of drones in a plinko environment with rudimentary object avoidance.
Open this file folder in GODOT (Ideally GODOT 4.4)

## The Simulator:

The simulator runs the simulation & can be used to configure parameters, using the inspector panel.

## The Drones:

The drones move forward at a customizeable speed.
When encountering an obstacle, they move either left or right with a customizeable probability.
Drones switch direction if about to collide with an obstacle from the side.
Obstacles can include other drones.

Drones can also be configured to weight their probability using the angle to the goal location.
Drone count & directional weighting is configured in the inspector.

NOTE: like real life plinko, drones can get stuck.

## The Logger:

Logs entry/exit data as well as motionpath data for the drones.
Also logs some metadata.
Change the filename of the desired output files in the simulators inspector.

filename_ee is the name of the file to store entry/exit data.
filename_cont is the name of the file for continuous/motionpath data.

## Headless Usage

From the command line, you can run scripts with the following command:

```bash
/path/to/godot/headless --path /path/to/dir/containing/project.godot/ --headless --script scripts/run_sim_headless.gd
```

Only tested on WSL so far, next step is to figure out how to initialize the sim, then start a run with logging.

## Analysis

The analysis script can be used to analyze the data collected by the logger.
It processes data files to compute and visualize makespan and spatial statistics for comparing drone navigation strategies.