using Godot;

public partial class SimulationSlot : SubViewport
{
	[Export] PackedScene worldScene;

	public static SimulationManager manager;
	public static PackedScene simulationViewerScene;

	public int slotID;
	Field currentSim;
	public int worldID;
	double remainingTime;
	SimulationResults results;

	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		World2D = new(); // each slot should have a separate world
	}

	public override void _PhysicsProcess(double delta)
	{
		if (currentSim != null) // currently running a simulation
		{
			base._PhysicsProcess(delta);
			remainingTime -= delta;
			if (remainingTime < 0)
			{
				currentSim.NotifyTimeout();
			}
		}
		else if (results != null) // this occurs on the frame after a simulation finishes
		{
			manager.NotifySimulationFinished(this, results);
			results = null;
		}
		// otherwise, all simulations are either finished or in progress in other slots,
		// and there is nothing else for this one to do
	}

	// Creates a simulation slot, and adds its viewport container to the grid.
	public static SimulationSlot CreateSimulationSlotViewer(int ID)
	{
		SubViewportContainer viewer = simulationViewerScene.Instantiate<SubViewportContainer>();
		manager.AddChild(viewer);

		SimulationSlot slot = viewer.GetChild<SimulationSlot>(0);
		slot.slotID = ID;

		return slot;
	}

	// Starts a simulation with the given parameters and associates it with the given index.
	public void StartSimulation(SimulationParameters p, int worldID)
	{
		currentSim = worldScene.Instantiate<Field>();
		AddChild(currentSim);

		currentSim.StartSimulation(p, this);

		this.worldID = worldID;
		remainingTime = p.maxTime;

		GD.Print($"[{Time.GetTicksMsec()}] {slotID}:{worldID} starting");
	}

	// Called by the currently simulated world when its simulation is finished.
	// Deletes the world, and stores the data from the simulation to return on the next frame.
	public void FinishSimulation(SimulationResults results)
	{
		GD.Print($"[{Time.GetTicksMsec()}] {slotID}:{worldID} finished ({results.duration}, {results.finishType})");

		if (currentSim == null) // ensure that only the first call of this from a world is processed
		{
			return;
		}

		currentSim.QueueFree();
		currentSim = null;

		this.results = results;
	}
}
