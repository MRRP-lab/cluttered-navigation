extends Area2D

# drone_list stores data about the drones as a multidimentional array
var drone_list = []
var count = 0

# drone threshold is the number of drones
# after which to save the data & write to a csv file.
@export var drone_threshold: int = 1

# whether or not to write the gathered data to a csv file.
@export var write_to_file: bool = false

# the filename of the csv file to store data to. Do not include file extensions.
# WARNING: DO NOT have multiple scanners write to the same file.
# I don't know what will happen.
@export var filename: String

func print_data():
	for e in drone_list:
		print(str(e[0]) + ", " + str(e[1]) + ", " + str(e[2]))

# store the data as a csv file
# NOTE: it saves as a .txt file because godot can't make csv files for whatever.
func save_data():
	# make & open the file
	var filepath = "res://output-data/" + filename + ".txt"
	var file = FileAccess.open(filepath, FileAccess.WRITE)
	
	# load data from the list
	for e in drone_list:
		var str_array = PackedStringArray(e)
		file.store_csv_line(str_array)
	
	file.close()

# setup
func _ready() -> void:
	connect("body_entered", drone_entered)
	drone_list.append(["drone", "position", "time"])

# called when a drone enters the scanner's area.
# t: time = time in miliseconds since the simulation started running.
# p: position = the y-coordinate of the drone that entered the scnner.
# body: drone = the id of the drone.
var drone_entered = func(body: Node2D):
	count += 1
	
	var t = float(Time.get_ticks_msec())
	var p = body.position.y
	
	var node = [body, p, t]
	drone_list.append(node)
	
	# outputs the data once the specified number of drones pass through.
	# if write_to_file is true, saves the data to a csv file.
	if count >= drone_threshold:
		print_data()
		
		if write_to_file:
			save_data()
