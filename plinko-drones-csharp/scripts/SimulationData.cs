using System.Collections.Generic;
using Godot;

public enum SimNotificationType { Finished, Timeout }

public class SimulationParameters
{
	public int droneNum = 10;
	public bool weightedDirection = false;
	public float maximumAngle = 45;

	public ObstacleShape obstacleShape = ObstacleShape.Triangle;
	public int obstacleWidth = 4, obstacleDepth = 4;
	public int obstacleSpacing = 60;
	public float obstacleRandomization = 50;
	public float obstacleScale = 1.0f;

	public float maxTime = 20;
	public int timerWaitTime_ms = 0;
	public ControlType controlType = ControlType.Decentralized;
}

public class SimulationResults
{
	public float duration;
	public SimNotificationType finishType;
	public SimulationResults_EE data_EE;
	public SimulationResults_Continuous data_Continuous;
}

public class SimulationResults_EE
{
	public float[] times_entered; // indexed by drone ID
	public float[] times_exited;
}

public class SimulationResults_Continuous
{
	public LinkedList<float> times_ms; // times of each recorded tick
	public LinkedList<Vector2>[] paths; // indexed by [drone ID][tick ID]
}

/*
// Generates arrays of parameter sets based on the cartesian product of arrays of individual parameters.
// Default parameters are used for empty arrays.
public class ParameterBuilder
{
	public int[] droneNum;
	public bool[] weightedDirection = [];
	public float[] maximumAngle = [];

	public ObstacleShape[] obstacleShape = [];
	public int[] obstacleWidth = [], obstacleDepth = [];
	public int[] obstacleSpacing = [];
	public float[] obstacleRandomization = [];
	public float[] obstacleScale = [];

	public float[] maxTime = [];
	public int[] timerWaitTime_ms = [];
	public ControlType[] controlType = [];

	private static SimulationParameters defaultParameters = new();
	private LinkedList<ParameterBuilder> otherBuilders = new();

	public ParameterBuilder Add(ParameterBuilder next)
	{
		otherBuilders.AddLast(next);
		return this;
	}

	private void BuildPart(LinkedList<SimulationParameters> current)
	{
		//set undefined parameters to default values
		droneNum ??= [defaultParameters.droneNum];
		weightedDirection ??= [defaultParameters.weightedDirection];
		maximumAngle ??= [defaultParameters.maximumAngle];

		obstacleShape ??= [defaultParameters.obstacleShape];
		obstacleWidth ??= [defaultParameters.obstacleWidth];
		obstacleDepth ??= [defaultParameters.obstacleDepth];
		obstacleSpacing ??= [defaultParameters.obstacleSpacing];
		obstacleRandomization ??= [defaultParameters.obstacleRandomization];
		obstacleScale ??= [defaultParameters.obstacleScale];

		maxTime ??= [defaultParameters.maxTime];
		timerWaitTime_ms ??= [defaultParameters.timerWaitTime_ms];
		controlType ??= [defaultParameters.controlType];

		foreach (int currentDroneNum in droneNum)
		{
			// I realized at this point that there wasn't a convenient way to tell this system
			// that certain parameters should be correlated, but I'm leaving it here because it
			// seems like a potentially useful idea.
		}
	}

	public SimulationParameters[] Build()
	{
        LinkedList<SimulationParameters> list = new();
		BuildPart(list);
		foreach (ParameterBuilder builder in otherBuilders)
		{
			builder.BuildPart(list);
		}
		return [.. list];
	}
}
*/