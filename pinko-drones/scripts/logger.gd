extends Node
class_name Logger
## An updated system for logging drone information
## from the simulation. Can choose between enter/exit or continuous.

# export variables
@export var simulator: Swarm_Sim ## simulator
@export var drones: Node2D ## drone container
@export_enum("Decentralized", "Centralized") var strategy: String = "Decentralized" ## flag for what strategy the drones are using. Is passed to the output file.

# Area2D nodes we're using to monitor the drones.
var area_ee: Area2D   # enter/exit monitoring
var timer: Timer      # timer for continuous monitoring.

var motionplan_data_array = [["strategy", "droneCount", "droneID", "timeStamp", "x", "y"]]

const LOGGER_RECTANGLE_ENTER_EXIT = preload("res://resources/logger_rectangle_enter_exit.tres")

# --------- INITIALIZATION ------------ #

func _ready() -> void:
	
	# set up Area2D
	area_ee = Area2D.new()
	var c1 = CollisionShape2D.new()
	c1.shape = LOGGER_RECTANGLE_ENTER_EXIT
	
	# set up timer
	timer = Timer.new()
	
	# add nodes to the tree
	area_ee.add_child(c1)
	add_child(area_ee)
	add_child(timer)
	
	# connect signals
	area_ee.connect("body_entered", drone_entered)
	area_ee.connect("body_exited", drone_exited)
	timer.connect("timeout", timer_timeout)

## Sets up the timer with the inputted wait time in milliseconds & then starts it. 
func init_timer(time_ms: float):
	timer.set_wait_time(time_ms / 1000)
	timer.start()

# -------- ENTER / EXIT LOGGING --------- #

## save time entered data to the drones
var drone_entered = func(body: Node2D):
	if body is PlinkoDrone:
		body.time_entered = Time.get_ticks_msec()

## save time exited data to the drones
var drone_exited = func(body: Node2D):
	if body is PlinkoDrone:
		body.time_exited = Time.get_ticks_msec()

## log drone data to the specified files.
func log_data_ee(filepath: String):
	var file = FileAccess.open(filepath, FileAccess.WRITE) # open file
	
	file.store_csv_line(["strategy", "droneCount", "droneID", "entryTime", "exitTime"]) # write header
	
	for drone in drones.get_children(): # write data
		var log = PackedStringArray([strategy, simulator.droneNum, drone.get_instance_id(), drone.time_entered, drone.time_exited])
		file.store_csv_line(log)
	
	file.close() # prevent data leaks

# ------------ CONTINUOUS LOGGING -------------- #

## called every time the timer ticks. logs drone position/time data to an array.
func timer_timeout():
	for drone in drones.get_children(): # write data
		var log = PackedStringArray([strategy, simulator.droneNum, drone.get_instance_id(), Time.get_ticks_msec(), drone.position.x, drone.position.y])
		motionplan_data_array.append(log)

## writes continuous motionplan data to a specified output file.
func log_data_cont(filepath: String):
	var file = FileAccess.open(filepath, FileAccess.WRITE) # open file
	
	for e in motionplan_data_array: # write data
		var log = PackedStringArray(e)
		file.store_csv_line(log)
	
	file.close() # prevent data leaks
