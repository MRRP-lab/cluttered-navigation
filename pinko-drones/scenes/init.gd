extends Node2D

@export var start_pos: Vector2
@export var field: Node2D
@export var obstacle_shape: String  ## can either be 'rectangle' or 'triangle'

func _ready() -> void:
	if obstacle_shape.to_lower() == "triangle":
		ObstacleGenerator.generate_plinko(field, start_pos)
	else:
		ObstacleGenerator.generate_rectangle(field, start_pos)
