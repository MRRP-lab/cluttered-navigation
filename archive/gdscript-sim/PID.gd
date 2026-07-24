class_name PID

var p: float = 0
var i: float = 0
var i_out: float = 0
var d: float = 0
var error_prev: float = 0

func calculate(error: float, delta: float) -> float:
	
	# calculate the values
	var p_out = p * error
	i_out += i * error * delta
	var d_out = d * (error - error_prev)
	
	# update error
	error_prev = error
	
	#print(str(p_out) + ", " + str(i_out) + ", " + str(d_out))
	return (p_out + i_out + d_out)

func reset() -> void:
	error_prev = 0
	p = 0
	i = 0
	d = 0
