extends Node2D
class_name Swarm_Sim

 
@export var droneNum: int

@export_range(1, 180, 1, "suffix:°") var Minimum_Angle: float
@export var start: Node2D
@export var end: Node2D
@export var obstacles: Node2D
@export var drones: Node2D

# Optionally initialize the board.
func _ready() -> void:
	print("Hello World!")
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
		
