# PLINKO DRONES

A simulation of drones in a plinko environment with rudimentary object avoidance.
Open this file folder in GODOT (Ideally GODOT 4)

## The Drones:

The drones move forward at a customizeable speed.
When encountering an obstacle, they move either left or right with a customizeable probability.
Drones switch direction if about to collide with an obstacle from the side.
Obstacles can include other drones.

NOTE: like real life plinko, drones can get stuck.

## The Obstacles

The obstacles are static & just kind of sit there.

## The Scanner

Reads when drones enter its area. Optionally writes to a csv file with a given filename.
The scanner actually creates .txt files because godot throws errors when creating .csv files.
The data is still organized in csv format though.