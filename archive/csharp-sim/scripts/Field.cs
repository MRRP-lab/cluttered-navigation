using Godot;
public enum ObstacleShape { Triangle, Rectangle }
public enum ControlType { Centralized, Decentralized }

public partial class Field : Node2D
{

	private static PackedScene drone = ResourceLoader.Load<PackedScene>(
		"res://scenes/plinko_drone.tscn");
	private static PackedScene obstacle = ResourceLoader.Load<PackedScene>(
		"res://scenes/obstacle.tscn");

	RandomNumberGenerator rand = new();

	[ExportGroup("Obstacle Generation")]
	[Export] ObstacleShape obstacleShape; // Shape of the obstacle field, either Triangle or Rectangle
	[Export] int obstacleWidth = 4;  // Number of obstacles along the y-axis of the field. If triangular, the width of the base
	[Export] int obstacleDepth = 4;  // Number of obstacles along the x-axis of the field. If triangular, this is ignored
	[Export] int obstacleSpacing = 60;  // Spacing in pixels between obstacles
	[Export(PropertyHint.Range, "0, 100, 1, suffix:%")] float obstacleRandomization = 50; // Maximum randomization offset, where 100% is the maximum range between obstacles without collisions
	[Export] float obstacleScale = 1.0f;  // Scale of the obstacle image and collision circle

	[ExportGroup("Drone Properties")]
	[Export] public ControlType control; // right now used for logging.
	[Export] int droneNum; // Number of drones to generate
	[Export] public bool weightedDirection;

	[Export(PropertyHint.Range, "1, 180, 1, suffix:°")] float maximumAngle = 45;

	[ExportGroup("Nodes")]
	[Export] Node2D start;
	[Export] Node2D end;
	[Export] Node2D obstacles;
	[Export] Node2D drones;
	[Export] Logger logger;

	double startTime;
	int remainingDrones; // number of drones that haven't yet reached the finish area
	public SimulationSlot simulationSlot;

	const float OBSTACLE_SIZE = 32;  // size in pixels of the obstacle image

	// Initializes the simulation with the given parameters.
	public void StartSimulation(SimulationParameters p, SimulationSlot slot)
	{
		control = p.controlType;
		obstacleShape = p.obstacleShape;
		obstacleWidth = p.obstacleWidth;
		obstacleDepth = p.obstacleDepth;
		obstacleSpacing = p.obstacleSpacing;
		obstacleRandomization = p.obstacleRandomization;
		obstacleScale = p.obstacleScale;
		droneNum = p.droneNum;
		weightedDirection = p.weightedDirection;
		maximumAngle = p.maximumAngle;

		simulationSlot = slot;
		maximumAngle = Mathf.DegToRad(maximumAngle);
		Vector2 startPoint = obstacles.Position + new Vector2(140, 0);
		if (obstacleShape == ObstacleShape.Triangle)
		{
			GenerateTriangle(startPoint);
		}
		else
		{
			GenerateRectangle(startPoint);
		}

		CreateDrones();

		logger.InitTimer(p);

		startTime = Time.GetUnixTimeFromSystem();
	}

	// Initialize drones in start region based on the parameters.
	public void CreateDrones()
	{
		remainingDrones = droneNum;
		float endRegionStartX = end.GlobalPosition.X - ((RectangleShape2D)end.
			GetChild<CollisionShape2D>(0).Shape).Size.X / 2;
		for (int i = 0; i < droneNum; i++)
		{
			PlinkoDrone newDrone = drone.Instantiate<PlinkoDrone>();

			newDrone.Name = "drone_" + i;
			newDrone.id = i;
			newDrone.moveSpeed = 50;

			// Vector2 startOffset = new(-((CircleShape2D)start.
			// 	GetChild<CollisionShape2D>(0).Shape).Radius, 0);
			// Vector2 endOffset = new(((RectangleShape2D)end.
			// 	GetChild<CollisionShape2D>(0).Shape).Size.X / 2, 0);
			// newDrone.startPoint = start.GlobalPosition + startOffset;
			// newDrone.endPoint = end.GlobalPosition;

			newDrone.startPoint = start.GlobalPosition;
			newDrone.endPoint = end.GlobalPosition;
			newDrone.endRegionStartX = endRegionStartX;

			newDrone.maxAngle = maximumAngle;
			newDrone.weighted = weightedDirection;

			Vector2 randOffset = new(rand.RandfRange(-25, 25), rand.RandfRange(-25, 25));
			newDrone.Position = start.Position + randOffset;

			newDrone.rand = rand;
			newDrone.field = this;

			drones.AddChild(newDrone);
			//GD.Print("Drone sprite texture:", newDrone.GetNode<Sprite2D>("Sprite2D").Texture);
			//GD.Print("Drone position", newDrone.Position);
		}
	}

	// Notify the simulation that a drone has reached the finish area.
	public void NotifyDroneFinished(PlinkoDrone drone)
	{
		if (--remainingDrones == 0)
		{
			simulationSlot.FinishSimulation(GetResults(SimNotificationType.Finished));
		}
	}

	// Notify the simulation that its time limit has been reached.
	public void NotifyTimeout()
	{
		simulationSlot.FinishSimulation(GetResults(SimNotificationType.Timeout));
	}

	// Generates obstacles in a triangular plinko formation
	void GenerateTriangle(Vector2 startPoint)
	{
		//GD.Print("Generating obstacles in a triangular plinko formation");

		for (int row = 0; row < obstacleWidth; row++)
		{
			for (int col = 0; col < row + 1; col++)
			{
				Node2D new_obstacle = obstacle.Instantiate<Node2D>();
				new_obstacle.Name = "obstacle_" + row + "_" + col;

				new_obstacle.Position = new Vector2(
					startPoint.X + row * obstacleSpacing,
					startPoint.Y + col * obstacleSpacing - row * obstacleSpacing / 2);

				new_obstacle.ApplyScale(obstacleScale * Vector2.One);
				new_obstacle.Position += RandomizePosition();

				obstacles.AddChild(new_obstacle);
			}
		}
	}

	// Generates obstacles in a rectangular plinko formation
	// The start vector corresponds to the middle of the first row of obstacles
	void GenerateRectangle(Vector2 startPoint)
	{
		//GD.Print("Generating obstacles in a rectangular formation");

		for (int row = 0; row < obstacleDepth; row++)
		{
			int width = (row % 2 == 0) ? obstacleWidth - 1 : obstacleWidth;
			for (int col = 0; col < width; col++)
			{
				Node2D new_obstacle = obstacle.Instantiate<Node2D>();
				new_obstacle.Name = "obstacle_" + row + "_" + col;

				new_obstacle.Position = new Vector2(
					startPoint.X + row * obstacleSpacing,
					startPoint.Y + col * obstacleSpacing - (width - 1) * obstacleSpacing / 2);

				new_obstacle.ApplyScale(obstacleScale * Vector2.One);
				new_obstacle.Position += RandomizePosition();

				obstacles.AddChild(new_obstacle);
			}
		}
	}


	// Returns the randomization offset vector, accounting for max spacing.
	Vector2 RandomizePosition()
	{
		float maxRandOffset = (obstacleSpacing - obstacleScale * OBSTACLE_SIZE) / 2 * (obstacleRandomization / 100);
		return new(maxRandOffset * rand.RandfRange(-1, 1), maxRandOffset * rand.RandfRange(-1, 1));
	}

	// Computes simulation results from the current state.
	public SimulationResults GetResults(SimNotificationType finishType)
	{
		double finishTime = Time.GetUnixTimeFromSystem();
		float duration = (float)(finishTime - startTime);

		SimulationResults results = new()
		{
			duration = duration,
			finishType = finishType,
			data_EE = logger.GetResults_EE(),
			data_Continuous = logger.GetResults_Continuous()
		};
		return results;
	}

	public override void _Draw()
	{
		base._Draw();
		Vector2 endpoint = new Vector2(-Mathf.Cos(maximumAngle), Mathf.Sin(maximumAngle)) * 400;
		DrawLine(end.GlobalPosition, end.GlobalPosition + endpoint, Colors.Red, 3);
		DrawLine(end.GlobalPosition, end.GlobalPosition + endpoint * new Vector2(1, -1), Colors.Red, 3);
	}

	/*## Logs data to the specified files
	func log_data():
		var filepath_ee = "res://output-data/" + filename_ee + ".txt"
		var filepath_cont = "res://output-data/" + filename_cont + ".txt"

		logger.log_data_ee(filepath_ee)
		logger.log_data_cont(filepath_cont)*/
}
