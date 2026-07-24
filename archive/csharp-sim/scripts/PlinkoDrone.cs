using Godot;
using System.Collections.Generic;

public partial class PlinkoDrone : CharacterBody2D
{
	// drone variables:
	[Export] public float moveSpeed = 100;
	public RandomNumberGenerator rand;
	public Field field;
	public int id;

	// float for turning left or right. Left is 0, Right is 1
	// Equal probability of either direction is 0.5
	[Export(PropertyHint.Range, "0, 1, 0.01, suffix:%")] float avoidProbability = 0.5f;

	[Export] public Vector2 startPoint;
	[Export] public Vector2 endPoint;
	public float endRegionStartX;

	[Export] public float maxAngle;
	[Export] public bool weighted;
	// scanners for obstacles.
	// detector 1 monitors if the drone is about to hit an obstacle.
	// detector 2 makes sure the drone won't crash into the same obstacle again after avoiding it.
	// detectors 3 and 4 makes sure the drone won't crash going sideways
	[ExportGroup("Components")]
	[Export] CollisionShape2D collisionShape;
	[Export] Area2D detector1;
	[Export] Area2D detector2;
	[Export] Area2D detector3;
	[Export] Area2D detector4;

	// Entered & Exited for logging purposes.
	public float timeEntered;
	public float timeExited;

	// Path taken by the drone for logging purposes.
	public LinkedList<Vector2> path = new();

	// basic state machine for plinko-based drone control.
	public enum State
	{
		ADVANCING,
		AVOIDING,
		REENTERING,
		FINISHED
	}

	// state variables. These are the core of the state machine.
	public State currentState;
	float direction;

	// ----------------------------------------------------- //

	// state that moves the drone towards the target.
	void Advance(float delta)
	{
		if (IsFinished())
		{
			ChangeState_Finished();
		}
		else if (IsOutOfBounds())
		{
			ChangeState_ReenterBounds();
		}
		// switch to avoiding if there is an obstacle.
		else if (ObstacleDetected(detector1))
		{
			ChangeState_Avoiding();
		}
	}

	// state that avoids detected obstacles
	void Avoid(float delta)
	{
		// switch directions if about to hit an obstacle from the side.
		if (ObstacleDetected(detector3))
		{
			direction = 1;
		}
		if (ObstacleDetected(detector4))
		{
			direction = -1;
		}

		// set velocity according to direction
		Velocity = new Vector2(0, moveSpeed * direction);

		// switch to advancing if moved away from the obstacle.
		if (!ObstacleDetected(detector2))
		{
			ChangeState_Advancing();
		}
	}

	void Reenter()
	{
		if (IsOutOfBounds())
		{
			float vx = (Position.X > endPoint.X) ?
				-moveSpeed : 0;
			float vy = (GlobalPosition.Y > endPoint.Y) ?
				-moveSpeed : moveSpeed;

			Velocity = new Vector2(vx, vy);
		}
		else
		{
			ChangeState_Advancing();
		}
	}

	// -------------------------------------------------------------- //

	// returns true if there is an object detected
	// that isn't this drone.
	bool ObstacleDetected(Area2D detector)
	{
		foreach (Node2D body in detector.GetOverlappingBodies())
		{
			if (body != this)
			{
				return true;
			}
		}
		return false;
	}

	bool IsFinished(){
		return GlobalPosition.X >= endRegionStartX;
	}

	bool IsOutOfBounds()
	{
		// imagine a line from the ending outwards at the angle specified.
		return AngleFromEnd() > maxAngle;
	}

	// Angle in radians from the endpoint
	float AngleFromEnd()
	{
		return AngleBetween(startPoint, endPoint, GlobalPosition);
	}

	// Angle in radians from points that make up angle ABC.
	static float AngleBetween(Vector2 A, Vector2 B, Vector2 C)
	{
		Vector2 v1 = (A - B).Normalized();
		Vector2 v2 = (C - B).Normalized();
		return Mathf.Acos(v1.Dot(v2));
	}

	// returns 0.5 to -0.5 based on the angle of the drone to the end
	float GetVerticalPercent()
	{
		var percent = AngleFromEnd() / (maxAngle * 2);
		if (GlobalPosition.Y < endPoint.Y)
		{
			return percent;
		}
		else
		{
			return -percent;
		}

	}


	// change the state to advancing.
	void ChangeState_Advancing()
	{
		Velocity = new Vector2(moveSpeed, 0);

		currentState = State.ADVANCING;
	}

	void ChangeState_ReenterBounds()
	{
		currentState = State.REENTERING;
	}

	void ChangeState_Finished()
	{
		field.NotifyDroneFinished(this);

		Velocity = Vector2.Zero;
		collisionShape.QueueFree();

		currentState = State.FINISHED;
	}

	// change the state to avoiding.
	void ChangeState_Avoiding()
	{
		Velocity = Vector2.Zero;

		float verticalPercent = weighted ? GetVerticalPercent() : 0;

		// Set a random avoid direction based off the percent the drone exists
		// between the angled boundary from the end
		float rng = rand.Randf();
		direction = rng < (avoidProbability + verticalPercent) ? 1 : -1;

		currentState = State.AVOIDING;
	}

	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		base._Ready();
		ChangeState_Advancing();
	}

	float debugTimer = 2.0f;
	public override void _PhysicsProcess(double delta)
	{
		switch (currentState)
		{
			case State.ADVANCING:
				Advance((float)delta);
				break;
			case State.AVOIDING:
				Avoid((float)delta);
				break;
			case State.REENTERING:
				Reenter();
				break;
			case State.FINISHED:
				break;
		}

		MoveAndSlide();

		// if ((debugTimer -= (float)delta) <= 0){
		// 	debugTimer = 2.0f;
		// 	GD.Print($"x: {GlobalPosition.X}/{endRegionStartX}");
		// }
	}
}
