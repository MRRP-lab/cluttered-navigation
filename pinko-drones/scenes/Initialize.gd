extends Node2D
class_name Swarm_Sim


@export_group("Obstacle Generation")
@export var obstacle_shape := "triangle"  ## Shape of the obstacle field, either 'triangle' or 'rectangle'
@export var obstacle_width := 4  ## Number of obstacles along the y-axis of the field. If triangular, the width of the base
@export var obstacle_depth := 4  ## Number of obstacles along the x-axis of the field. If triangular, this is ignored
@export var obstacle_spacing := 60  ## Spacing in pixels between obstacles
@export_range(0, 100, 1, "suffix:%") var obstacle_randomization: float  ## Maximum randomization offset, where 100% is the maximum range between obstacles without collisions
@export var obstacle_scale := 1.0  ## Scale of the obstacle image and collision circle

@export_group("Drone Properties")
@export var droneNum: int
@export_range(1, 180, 1, "suffix:°") var Minimum_Angle: float

@export_group("Nodes")
@export var start: Node2D
@export var end: Node2D
@export var obstacles: Node2D
@export var drones: Node2D

const OBSTACLE_SIZE = 32  # size in pixels of the obstacle image

# Optionally initialize the board.
func _ready() -> void:
	print("Hello World!")
	var start_point = obstacles.position + Vector2(140, 0)
	if obstacle_shape == "triangle":
		generate_triangle(start_point)
	else:
		generate_rectangle(start_point)
	
	# Initialize drones in start region based on the parameters.
	var drone = preload("res://scenes/plinko_drone.tscn")
	for i in range(droneNum):
		var newDrone = drone.instantiate()
		
		newDrone.name = str("drone_", i)
		newDrone.move_speed = 50
		
		var randOffset = Vector2(randf() * 50 - 25, randf() * 50 - 25)
		newDrone.position = start.position + randOffset
		
		drones.add_child(newDrone)
		print("Drone sprite texture:", newDrone.get_node("Sprite2D").texture)
		print("Drone position", newDrone.position)


## Generates obstacles in a triangular plinko formation
func generate_triangle(start_point: Vector2) -> void:
	print("Generating obstacles in a triangular plinko formation")
	
	var obstacle = preload("res://scenes/obstacle.tscn")
	for row in obstacle_width:
		for col in row + 1:
			var new_obstacle = obstacle.instantiate()
			new_obstacle.name = str("obstacle_", row, col)
			
			new_obstacle.position.x = start_point.x + (row * obstacle_spacing)
			new_obstacle.position.y = start_point.y + (col * obstacle_spacing) - (row * obstacle_spacing / 2)
			new_obstacle.apply_scale(Vector2(obstacle_scale, obstacle_scale))
			
			new_obstacle.position += randomize_position()
			
			obstacles.add_child(new_obstacle)

## Generates obstacles in a rectangular plinko formation
## The start vector corresponds to the middle of the first row of obstacles
func generate_rectangle(start_point: Vector2) -> void:
	print("Generating obstacles in a rectangular formation")
	
	var obstacle = preload("res://scenes/obstacle.tscn")
	for row in obstacle_depth:
		var width = obstacle_width
		if (row % 2):
			width -= 1
		
		for col in width:
			var new_obstacle = obstacle.instantiate()
			new_obstacle.name = str("obstacle_", row, col)
			
			new_obstacle.position.x = start_point.x + (row * obstacle_spacing)
			new_obstacle.position.y = start_point.y + (col * obstacle_spacing) - (width * obstacle_spacing) / 2 + (obstacle_spacing / 2)
			new_obstacle.apply_scale(Vector2(obstacle_scale, obstacle_scale))
			
			new_obstacle.position += randomize_position()
			
			obstacles.add_child(new_obstacle)

## Returns the randomization offset vector, accounting for max spacing.
func randomize_position() -> Vector2:
	var max_rand_offset = ((obstacle_spacing / 2) - (obstacle_scale * OBSTACLE_SIZE) / 2) * (obstacle_randomization / 100)
	var rand_vector = Vector2(max_rand_offset * randf_range(-1, 1), max_rand_offset * randf_range(-1, 1))
	return rand_vector
	
