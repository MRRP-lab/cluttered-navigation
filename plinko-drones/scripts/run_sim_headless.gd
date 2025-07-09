extends SceneTree

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
    change_scene_to_packed(instance)

func _init():

    # get command line arguments (flags)
    # no idea why this stopped working
    var args = Array(OS.get_cmdline_args())
    print(args)

    # change variable values based on flags
    if args.has("-w"):
        print("weighted")
    else:
        print("unweighted")

    # loop over variable(s) of interest based on flags
    reset(45.0)
    # run sim with logging
    quit()
