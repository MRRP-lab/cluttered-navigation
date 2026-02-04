# Pygame for robotics simulation

## Dependencies

- yaml
- pygame ([docs here](https://www.pygame.org/docs/))
- numpy
- pylab
- pandas


## Getting started

Run `python generate_demo.py`, then run `python play_demo.py`. The second
command should cause a box to pop up, visualizing the simulation. `play_demo.py`
will also save a video to the `videos` folder.

We have separated generation of the simulation (`generate_demo.py`) from
visualization of the simulation (`play_demo.py`). While pygame is pretty
efficient, at larger numbers of agents, the simulation cannot render in real
time while also solving for the physics and interactions involved. This also
allows us to always log simulation information for replay later, useful for
computing new statistics on old runs of the simulator.

## Design Choices

We've included trails to see where robots have been and a pointer to show robot
orientation.
