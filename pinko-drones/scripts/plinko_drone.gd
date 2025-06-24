extends CharacterBody2D
class_name PlinkoDrone

# drone variables:
@export var move_speed: float

# float for turning left or right. Left is 0, Right is 1
@export_range(0, 1, 0.01, "suffix:%") var avoid_probability: float

# scanners for obstacles.
# detector one monitors if the drone is about to hit an obstacle.
# detector 2 makes sure the drone won't crash into the same obstacle again after avoiding it.
# detector 3 makes sure the drone won't crash going sideways
@onready var detector: Area2D = $detector
@onready var detector_2: Area2D = $detector2
@onready var detector_3: Area2D = $detector3
@onready var detector_4: Area2D = $detector4

# basic state machine for plinko-based drone control.
enum states {
	ADVANCING,
	AVOIDING
}

# state variables. These are the core of the state machine.
var current_state
var direction

# ----------------------------------------------------- #

# state that moves the drone towards the target.
func state_advancing_process(delta: float):
	
	# create a velocity vector to translate forward velocity
	# into x & y coordinates readable by the engine. Apply velocity.
	set_velocity(Vector2(move_speed, 0))
	
	# switch to avoiding if there is an obstacle.
	if obstacle_detected(detector):
		change_state_avoiding()

# state that avoids detected obstacles
func state_avoiding_process(delta: float):
	
	# switch directions if about to hit an obstacle from the side
	if obstacle_detected(detector_3):
		direction = 1
	if obstacle_detected(detector_4):
		direction = -1
	
	# set velocity according to direction
	set_velocity(Vector2(0, move_speed * direction))
	
	# switch to advancing if moved away from the obstacle.
	if not obstacle_detected(detector_2):
		change_state_advancing()

# -------------------------------------------------------------- #

# returns true if there is an object detected
# that isn't this drone.
func obstacle_detected(detector: Area2D) -> bool:
	for e in detector.get_overlapping_bodies():
		if e != self:
			return true
	return false

# change the state to advancing.
func change_state_advancing():
	print("advancing")
	current_state = states.ADVANCING

# change the state to avoiding.
func change_state_avoiding():
	print("avoiding")
	set_velocity(Vector2(0,0))
	
	# set a random direction based on the probability
	direction = 1 if randf() < avoid_probability else -1
	
	current_state = states.AVOIDING

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	current_state = states.ADVANCING

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	
	if current_state == states.ADVANCING:
		state_advancing_process(delta)
	elif current_state == states.AVOIDING:
		state_avoiding_process(delta)
	
	move_and_slide()
