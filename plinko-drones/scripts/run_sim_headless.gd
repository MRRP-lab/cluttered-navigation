extends SceneTree

var scene_path := "res://scenes/field.tscn"
var position_arg := Vector2.ZERO
var velocity_arg := Vector2.ZERO

func reset(angle: float, weighted=true):
    var scene = load("res://scenes/field.tscn")
    # Instance the new scene.
    var instance = scene.instantiate()

    # Add it to the active scene, as child of root.
    # get_tree().root.add_child(instance)

    # Optionally, to make it compatible with the SceneTree.change_scene_to_file() API.
    # get_tree().instance = instance

    instance.obstacle_width = 6
    instance.obstacle_depth = 6
    instance.droneNum = 20
    instance.weighted_direction = true
    instance.Maximum_Angle = angle
    var w = "UW"
    if weighted:
        w = "W"
    # set logging filename based on variable values in this instance
    instance.filename_ee = "sample-N"+str(instance.droneNum)+"-"+w+"-ee"
    instance.filename_cont = "sample-N"+str(instance.droneNum)+"-"+w+"-cont"
    #change_scene_to_packed(instance)

func parse_command_line_args():
    var args = OS.get_cmdline_args()
    print(args)

    for i in range(args.size()):
        match args[i]:
            "-w":
                print("weighted")
                if i + 1 < args.size():
                    scene_path = args[i + 1]
            "--pos":
                if i + 2 < args.size():
                    position_arg = Vector2(args[i + 1].to_float(), args[i + 2].to_float())
            "--vel":
                if i + 2 < args.size():
                    velocity_arg = Vector2(args[i + 1].to_float(), args[i + 2].to_float())

func load_and_run_simulation():
    var scene_res = load(scene_path)
    if not scene_res:
        push_error("Failed to load scene: " + scene_path)
        quit(1)

    var scene_instance = scene_res.instantiate()
    if not scene_instance:
        push_error("Failed to instance scene.")
        quit(1)

    root.add_child(scene_instance)

        # Assuming the simulation has a node named "Agent" to modify
    var sim = scene_instance.get_node("Simulator") if scene_instance.has_node("Simulator") else null
    if sim:
        sim.droneNum = 5
    #if sim.has_method("set_velocity"):
    #    sim.set_velocity(velocity_arg)
    #elif "velocity" in sim:
    #    sim.velocity = velocity_arg

    # Optionally call a method like "start" to run the simulation
    if scene_instance.has_method("start_simulation"):
        scene_instance.start_simulation()

func _init():
    parse_command_line_args()
    load_and_run_simulation()

#func _init():
#
#    # get command line arguments (flags)
#    # no idea why this stopped working
#    var args = Array(OS.get_cmdline_args())
#    print(args)
#
#    # change variable values based on flags
#    if args.has("-w"):
#        print("weighted")
#    else:
#        print("unweighted")
#
#    # loop over variable(s) of interest based on flags
#    reset(45.0)
#    # run sim with logging
#    quit()
