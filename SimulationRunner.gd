extends Node2D
class_name SimulationRunner

# Creates and runs simulations. Also handles the logging.

# filepath to the simulation we wish to run
var simulation = preload("res://scenes/field.tscn")

# offset variables to make sure the simulators don't run into each other.
# can run approx. 2.8 * 10^16 simulations before they run into each other.
var offset: int = 650 ## distance in y position of the simulators.
var current_pos: int = -1 ## position number of the furthest sim.

# to be used for the function 
const TRIANGLE = "triangle"
const RECTANGLE = "rectangle"

const CENTRALIZED = "Centralized"
const DECENTRALIZED = "Decentralized"

# default parameters:
var default_parameters = [RECTANGLE, 6, 6, 60, 50, 1.0, DECENTRALIZED, 30, true, 60.0]

## returns a list of the currently running simulations
func get_running_simultations():
	return get_children()

## creates & returns a configured simulation
func create_sim(obstacle_shape: String, obstacle_width: int, obstacle_depth: int, obstacle_spacing: int, obstacle_randomization: int, obstacle_scale: float, control: String, drone_num: int, weighted_direction: bool, max_angle: float):
	var sim = simulation.instantiate() # create a new simulation
	
	# configures parameters
	sim.obstacle_shape = obstacle_shape
	sim.obstacle_width = obstacle_width
	sim.obstacle_depth = obstacle_depth
	sim.obstacle_spacing = obstacle_spacing
	sim.obstacle_randomization = obstacle_randomization
	sim.obstacle_scale = obstacle_scale
	sim.control = control
	sim.droneNum = drone_num
	sim.Maximum_Angle = max_angle
	
	# TODO: configure logging
	
	
	return sim

## creates a sim from an array of parameters.
func create_sim_from_array(parameters):
	var p = parameters
	return create_sim(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9])

## add simulation to the field
func add_sim(sim: Swarm_Sim):
	
	# configure position.
	sim.position.y = current_pos * offset
	current_pos += 1
	
	add_child(sim)

## Adds 3 running simulations to the field in order to test it.
func _ready() -> void:
	var sim = create_sim_from_array(default_parameters)
	add_sim(sim)
	
	sim = create_sim_from_array(default_parameters)
	add_sim(sim)
	
	sim = create_sim_from_array(default_parameters)
	add_sim(sim)
