extends Node2D
class_name ObstacleGenerator
## Static class to generate obstacle fields



## Generates obstacles in a triangular plinko formation
## 
static func generate_plinko(parent: Node2D, start: Vector2, levels := 4, spacing := 100, rand_offset := 0) -> void:
	print("Generating obstacles in a plinko formation")
	
	var obstacle = preload("res://scenes/obstacle.tscn")
	for depth in levels:
		for width in depth + 1:
			var new_obstacle = obstacle.instantiate()
			new_obstacle.name = str("obstacle_", depth, width)
			
			new_obstacle.position.x = start.x + (depth * spacing)
			new_obstacle.position.y = start.y + (width * spacing) - (depth * spacing / 2)
			parent.add_child(new_obstacle)


## Generates obstacles in a rectangular plinko formation
## The start vector corresponds to the middle of the first row of obstacles
static func generate_rectangle(parent: Node2D, start: Vector2, depth := 4, width := 4, spacing := 100, rand_offset := 0) -> void:
	print("Generating obstacles in a rectangular formation")
	
	var obstacle = preload("res://scenes/obstacle.tscn")
	for row in depth:
		for col in width:
			var new_obstacle = obstacle.instantiate()
			new_obstacle.name = str("obstacle_", row, col)
			
			new_obstacle.position.x = start.x + (row * spacing)
			new_obstacle.position.y = start.y + (col * spacing) - (width * spacing) / 2
			if (row % 2):
				new_obstacle.position.y += spacing / 2
			parent.add_child(new_obstacle)
			
	
	
	
