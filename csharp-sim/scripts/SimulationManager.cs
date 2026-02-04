using Godot;

public partial class SimulationManager : GridContainer
{
	[Export] PackedScene simulationViewerScene;

	SimulationSlot[] slots;
	SimulationParameters[] parameters;
	SimulationResults[] results;
	int nextIndex;
	int finishedCount;

	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		SimulationSlot.manager = this;
		SimulationSlot.simulationViewerScene = simulationViewerScene;
		CreateSimulationSlots(8);
		GenerateParameters();
		StartSimulations();
	}

	// Initializes the simulation slots and adds them to the window.
	private void CreateSimulationSlots(int count)
	{
		int sqrtCeil = Mathf.CeilToInt(Mathf.Sqrt(count));
		Columns = sqrtCeil;
		Scale = Vector2.One / sqrtCeil;

		slots = new SimulationSlot[count];
		for (int i = 0; i < count; i++)
		{
			slots[i] = SimulationSlot.CreateSimulationSlotViewer(i);
		}
	}

	// Generates the list of simulation parameters to use.
	private void GenerateParameters()
	{
		float[] maximumAngle = [30, 35, 40];
		int[] droneNum = [5, 10, 15, 20];
		bool[] weightedDirection = [false, true];

		int n = maximumAngle.Length * droneNum.Length * weightedDirection.Length;
		parameters = new SimulationParameters[n];
		results = new SimulationResults[n];

		for (int i = 0; i < n; i++)
		{
			// Note: the way this is done is unrelated to the rest of the program,
			// and the parameters could also be generated in some other way.
			float current_maximumAngle = maximumAngle[i % 3];
			int current_droneNum = droneNum[i / 3 % 4];
			bool current_weightedDirection = weightedDirection[i / 12 % 2];
			parameters[i] = new()
			{
				maximumAngle = current_maximumAngle,
				droneNum = current_droneNum,
				weightedDirection = current_weightedDirection
			};
		}
	}

	// Starts a simulation in each slot.
	private void StartSimulations()
	{
		int n = Mathf.Min(slots.Length, parameters.Length);

		for (int i = 0; i < n; i++)
		{
			slots[i].StartSimulation(parameters[i], i);
		}

		nextIndex = n;
		finishedCount = 0;
	}

	// Called by a SimulationSlot after it finishes a simulation.
	// Gives it the next set of parameters to start a new simulation if there are more,
	// or prints the data collected if all simulations have been finished.
	public void NotifySimulationFinished(SimulationSlot slot, SimulationResults result)
	{
		results[slot.worldID] = result;

		if (++finishedCount == results.Length)
		{
			FinishProgram();
		}
		else if (nextIndex < parameters.Length)
		{
			//slot.CallDeferred("StartSimulation", parameters[nextIndex], nextIndex++);
			slot.StartSimulation(parameters[nextIndex], nextIndex++);
		}
	}

	/*// Prints the data collected to the console.
	private void PrintResults()
	{
		for (int i = 0; i < results.Length; i++)
		{
			SimulationParameters p = parameters[i];
			SimulationResults r = results[i];

			GD.Print($"{i:00}: r1 = {p.r1}, m1 = {p.m1}, r2 = {p.r2}, m2 = {p.m2}, v1i = {p.v1}, v2i = {p.v2}: " +
				$"time = {r.duration:0.000}, v1f = {r.v1}, v2f = {r.v2}, result = {r.finishType}");
		}
	}*/

	// Outputs the results, and exits the program.
	private void FinishProgram()
	{
		Logger.SaveResults(parameters, results);
		GetTree().Quit();
	}
}