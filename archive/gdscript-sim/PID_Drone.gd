extends RigidBody2D
class_name PID_Drone

var thrust = 200
var thrust_rotate = 200
var pid_rotate = PID.new()
var pid_forward = PID.new()
var pid_sideways = PID.new()

@export var target: Node2D
@onready var avoider_1: Area2D = $CollisionAvoider1
@onready var avoider_2: Area2D = $CollisionAvoider2

func _ready() -> void:
	pid_forward.p = 100
	pid_forward.d = 6000
	
	pid_rotate.p = 1000
	pid_rotate.d = 25000

func _physics_process(delta: float) -> void:
	
	# get a vector from the drone to its target
	var error_v = target.position - position
	var rotation_error = get_angle_to(target.position) / PI
	
	# calculate rotational thrust
	var thrust_r = pid_rotate.calculate(rotation_error, delta)
	apply_torque(thrust_r * thrust_rotate * delta) # ------------------------------- #
	
	# calculate forward thrust
	var thrust_f = pid_forward.calculate(error_v.length(), delta)
	if thrust_f > 10000:
		thrust_f = 10000
	var thrust_v = Vector2(thrust_f * cos(rotation), thrust_f * sin(rotation))
	if (abs(rotation_error) < 0.1):
		thrust_v -= thrust_v * abs(rotation_error) * 4
		apply_central_force(thrust_v * delta) # ----------------------------------- #
	
	# calculate sideways thrust
	for body in avoider_2.get_overlapping_bodies():
		if body != self:
			
			# get vector components
			var angle = get_angle_to(body.position)
			var col_v = body.position - position
			var side_comp = col_v.length() * sin(angle)
			var forward_comp = col_v.length() * cos(angle)
			
			#print("position vector: (" + str(col_v.x) + ", " + str(col_v.y) + ")")
			#print("horizontal component rel to my rotation: " + str(thrust_s))
			
			# calculate thrust
			var thrust_s = 100000 / (side_comp * abs(side_comp))
			thrust_s += (1000 / forward_comp) * sign(thrust_s)
			var thrust_v2 = Vector2(thrust_s * sin(rotation), thrust_s * cos(rotation) * -1)
			apply_central_force(thrust_v2 * delta * thrust)
