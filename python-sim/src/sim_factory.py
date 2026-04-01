from src.strategies.plinko import PlinkoStrategy
from src.strategies.optimal import OptimalStrategy
from src.strategies.navstrategy import NavStrategy


from src.spawn_layout import SpawnLayout
from src.robots import Robots
from src.environment import Environment

# Prepares the proper NavStrategy given the parameters.
# All that will be left is to call run() on it with robots and an environment.
def prepare_simulation(params) -> NavStrategy:
    # TODO there are some parameters that don't really need to be parameters so they're set as magic numbers.
    start_line = 0

    spawn_layout = SpawnLayout(params.seed, params.num, params.density,
                               params.gridnum, start_line
                               )
    env = Environment(params.gridnum, params.seed,
                      params.boundary, params.boundary_angle, spawn_layout.boundary_line_y_offset,
                      params.row_gap, params.pin_gap, params.noise
                      )
    robots = Robots(params.num, spawn_layout.offsets)
    robots.set_environment(env)

    match params.strategy:
        case "decentralized":
            progress_timeout = 10
            return PlinkoStrategy(params.num, robots, env, params.seed, progress_timeout)

        # The centralized strategy assumes the java solver server is running. 
        case "centralized":
            return OptimalStrategy(robots, env)
        case _:
            raise ValueError(f"Unknown strategy: {params.strategy}")
