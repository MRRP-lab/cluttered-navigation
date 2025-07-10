extends SceneTree

var scene_path := "res://scenes/field.tscn"
# var Init = preload("res://scripts/Initialize.gd").new()
var N_arg := 20
var w_arg := false

func parse_command_line_args():
    var args = OS.get_cmdline_args()
    print(args)

    for i in range(args.size()):
        match args[i]:
            "-w":
                print("weighted")
            "-N":
                if i + 1 < args.size():
                    N_arg = args[i + 1].to_int()

func load_and_run_simulation(angle: float, N: int, weighted=true):
    # load base scene to godot
    var scene_res = load(scene_path)
    if not scene_res:
        push_error("Failed to load scene: " + scene_path)
        quit(1)
    var scene_instance = scene_res.instantiate()
    if not scene_instance:
        push_error("Failed to instance scene.")
        quit(1)
    root.add_child(scene_instance)
    var sim = root.get_node("Simulator")

    # DEFAULTS
    ###

    sim.obstacle_width = 6
    sim.obstacle_depth = 6
    sim.log_button.emit_signal("pressed")

    # SET FOR THIS SIMRUN
    ###
    sim.droneNum = N
    sim.weighted_direction = w_arg
    sim.Maximum_Angle = angle
    var w = "uw"
    if weighted:
        sim.weighted_direction = true
        w = "w"

    # SET LOGS
    ###
    # set logging filename based on variable values in this sim
    var filename_ee = "sample-N"+str(sim.droneNum)+"-"+w+"-ee"
    var filename_cont = "sample-N"+str(sim.droneNum)+"-"+w+"-cont"
    sim.filename_ee = filename_ee # idk anymore
    sim.filename_cont = filename_cont
    var filepath_ee = "res://output-data/" + filename_ee + ".txt"
    var filepath_cont = "res://output-data/" + filename_cont + ".txt"

    print("Logging")
    # makes empty files? how to run in loop?
    sim.logger.log_data_ee(filepath_ee)
    sim.logger.log_data_cont(filepath_cont)

    # timeout and quit cleanly?

func _init():
    parse_command_line_args()
    var angle := 40.0
    var N := 5
    var weighted = true
    load_and_run_simulation(angle, N, weighted)
    quit()
