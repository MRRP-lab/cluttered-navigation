extends SceneTree

var scene_path := "res://scenes/field.tscn"
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

func load_and_run_simulation(angle: float, weighted=true):
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
    sim.droneNum = 5
    sim.obstacle_width = 6
    sim.obstacle_depth = 6

    # SET FOR THIS SIMRUN
    ###
    sim.droneNum = N_arg
    sim.weighted_direction = w_arg
    sim.Maximum_Angle = angle
    var w = "uw"
    if weighted:
        sim.weighted_direction = true
        w = "w"

    # SET LOGS
    ###
    # set logging filename based on variable values in this sim
    sim.filename_ee = "sample-N"+str(sim.droneNum)+"-"+w+"-ee"
    sim.filename_cont = "sample-N"+str(sim.droneNum)+"-"+w+"-cont"
    #change_scene_to_packed(sim) # not needed?

func _init():
    parse_command_line_args()
    var angle = 40
    var weighted = true
    load_and_run_simulation(angle, weighted)
