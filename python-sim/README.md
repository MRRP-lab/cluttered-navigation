# Pygame for robotics simulation

## Dependencies

- pyyaml
- pygame ([docs here](https://www.pygame.org/docs/))
- numpy
- matplotlib (pylab)
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

## Data file organization

Data files are stored in uniquely named directories per-simulation, containing a few different files:
1. Playback data
2. Analytics data
3. Parameters used

Of course, with a structure like this it'd be hard to locate the data you're most interested in. Because of this, we include a python script used to index all of the experiments into one manifest so that they can be filtered by parameters for easy experiment aggregation.

To run simulations, there's an included bash script which can run parameter sweeps. To use it, set the sweep parameters and optionally set an experiment name to tag the data generated.
