# PLINKO DRONES

A simulation of drones in a plinko environment with rudimentary object avoidance.
Open this file folder in GODOT (Ideally GODOT 4.4)

## The Drones:

The drones move forward at a customizeable speed.
When encountering an obstacle, they move either left or right with a customizeable probability.
Drones switch direction if about to collide with an obstacle from the side.
Obstacles can include other drones.

Drone count & directional weighting is configured in the inspector.

NOTE: like real life plinko, drones can get stuck.

## The Obstacle Field

Obstacles are plinko-style & can be configured in either a triangle or rectangle shape.
This is configured in the simulator.

## The Logger:

Logs entry/exit data as well as motionpath data for the drones.
Also logs some metadata.
Change the filename of the desired output files in the simulators inspector.
