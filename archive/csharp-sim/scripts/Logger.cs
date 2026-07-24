using System.Collections.Generic;
using System.Linq;
using Godot;

public partial class Logger : Node2D
{
    // An updated system for logging drone information
    // from the simulation. Can choose between enter/exit or continuous.

    // Settings
    [Export] bool log_EE = true;
    [Export] bool log_Continuous = true;
    [Export] bool includeTimes = true; // include times in continuous logging (otherwise, only store the interval)
    [Export] public int defaultTimerWaitTime_ms = 250; // how often (in milliseconds) to capture drones' motionpath data.
    [Export(PropertyHint.File)] string file_ee; // ee: Entry/Exit. The file to which entry/exit data will be sent.
    [Export(PropertyHint.File)] string file_cont; // cont: continuous. The file to which continuous motionpath data will be sent.
    private static Logger instance;

    // Export variables
    [Export] Field simulator; // simulator
    [Export] Node2D drones; // drone container

    // Nodes we're using to monitor the drones.
    [Export] Area2D area_ee;   // enter/exit monitoring
    [Export] Timer timer;      // timer for continuous monitoring.

    //var motionplan_data_array = [["strategy", "droneCount", "maxAngle", "droneID", "timeStamp", "x", "y"]];
    // Times when continuous data was collected
    private LinkedList<float> logTimes_ms = new();
    private float startTime_ms;

    // --------- INITIALIZATION ------------ //

    public override void _Ready()
    {
        // set static variables
        instance = this;

        // remove unused components
        if (!log_EE)
        {
            area_ee.QueueFree();
        }
        if (!log_Continuous)
        {
            timer.QueueFree();
        }
    }

    // Sets up the timer with the wait time of the given parameters & then starts it.
    // If the wait time of the parameters is 0, the logger's default wait time is used instead,
    // and is stored in the parameters.
    public void InitTimer(SimulationParameters p)
    {
        if (log_Continuous)
        {
            if (p.timerWaitTime_ms == 0)
            {
                p.timerWaitTime_ms = defaultTimerWaitTime_ms;
            }

            timer.WaitTime = p.timerWaitTime_ms / 1000.0;
            timer.Start();

            startTime_ms = Time.GetTicksMsec();
        }
    }

    // -------- ENTER / EXIT LOGGING --------- //

    // save time entered data to the drones
    void DroneEntered(Node2D body)
    {
        if (body is PlinkoDrone drone)
        {
            drone.timeEntered = Time.GetTicksMsec() - startTime_ms;
        }
    }

    // save time exited data to the drones
    void DroneExited(Node2D body)
    {
        if (body is PlinkoDrone drone)
        {
            drone.timeExited = Time.GetTicksMsec() - startTime_ms;
        }
    }

    public SimulationResults_EE GetResults_EE()
    {
        int numDrones = drones.GetChildren().Count;
        float[] times_entered = new float[numDrones];
        float[] times_exited = new float[numDrones];

        foreach (PlinkoDrone drone in drones.GetChildren().Cast<PlinkoDrone>())
        {
            times_entered[drone.id] = drone.timeEntered;
            times_exited[drone.id] = drone.timeExited;
        }

        return new SimulationResults_EE()
        {
            times_entered = times_entered,
            times_exited = times_exited
        };
    }

    // ------------ CONTINUOUS LOGGING -------------- //


    // called every time the timer ticks. logs drone position/time data to lists.
    void TimerTimeout()
    {
        logTimes_ms.AddLast(Time.GetTicksMsec() - startTime_ms);
        foreach (PlinkoDrone drone in drones.GetChildren().Cast<PlinkoDrone>())
        {
            if (drone.currentState != PlinkoDrone.State.FINISHED)
            {
                drone.path.AddLast(drone.Position);
            }
        }
    }

    public SimulationResults_Continuous GetResults_Continuous()
    {
        int numDrones = drones.GetChildren().Count;
        LinkedList<Vector2>[] paths = new LinkedList<Vector2>[numDrones];

        foreach (PlinkoDrone drone in drones.GetChildren().Cast<PlinkoDrone>())
        {
            paths[drone.id] = drone.path;
        }

        return new SimulationResults_Continuous()
        {
            times_ms = logTimes_ms,
            paths = paths
        };
    }

    // ------------ OUTPUT -------------- //

    // Saves the data collected to files.
    public static void SaveResults(SimulationParameters[] parameters, SimulationResults[] results)
    {
        if (instance.log_EE)
        {
            SaveResults_EE(parameters, results);
        }

        if (instance.log_Continuous)
        {
            SaveResults_Continuous(parameters, results);
        }
    }

    private static void SaveResults_EE(SimulationParameters[] parameters, SimulationResults[] results)
    {
        GD.Print("Saving EE data to " + instance.file_ee);
        FileAccess file = FileAccess.Open(instance.file_ee, FileAccess.ModeFlags.Write); // open file

        // write header
        WriteCommonHeader(file);
        file.StoreCsvLine([
            "enteredTimePerDrone",
            "exitedTimePerDrone"
        ]);

        for (int i = 0; i < parameters.Length; i++)
        {
            SimulationParameters p = parameters[i];
            SimulationResults r = results[i];

            WriteCommonData(file, i, p, r);

            // write EE times
            for (int j = 0; j < p.droneNum; j++)
            {
                StoreObjectsAsCsv(file, [
                    r.data_EE.times_entered[j],
                    r.data_EE.times_exited[j],
                ]);
            }
        }

        file.Close();
    }

    private static void SaveResults_Continuous(SimulationParameters[] parameters, SimulationResults[] results)
    {
        GD.Print("Saving continuous data to " + instance.file_cont);
        FileAccess file = FileAccess.Open(instance.file_cont, FileAccess.ModeFlags.Write); // open file

        // write header
        WriteCommonHeader(file);
        if (instance.includeTimes)
        {
            file.StoreCsvLine(["numberOfTicks"]);
            file.StoreCsvLine(["timePerTick"]);
        }
        file.StoreCsvLine([
            "pathLengthPerDrone"
        ]);
        file.StoreCsvLine([
            "xPerTickPerDrone",
            "yPerTickPerDrone"
        ]);

        for (int i = 0; i < parameters.Length; i++)
        {
            SimulationParameters p = parameters[i];
            SimulationResults r = results[i];

            WriteCommonData(file, i, p, r);
            if (instance.includeTimes)
            {
                LinkedList<float> times = r.data_Continuous.times_ms;
                file.StoreCsvLine([times.Count.ToString()]);
                foreach (float t in times)
                {
                    file.StoreCsvLine([t.ToString()]);
                }
            }

            // write paths
            for (int j = 0; j < p.droneNum; j++) // for each drone
            {
                StoreObjectsAsCsv(file, [ // path length of drone
                    r.data_Continuous.paths[j].Count
                ]);

                foreach (Vector2 pos in r.data_Continuous.paths[j]) // for each tick
                {
                    StoreObjectsAsCsv(file, [ // position of drone at each tick
                        pos.X,
                        pos.Y
                    ]);
                }
            }
        }

        file.Close();
    }

    private static void WriteCommonHeader(FileAccess file)
    {
        file.StoreCsvLine([
            "simulationID",

            "droneNum",
            "weightedDirection",
            "maximumAngle",

            "obstacleShape",
            "obstacleWidth", "obstacleDepth",
            "obstacleSpacing",
            "obstacleRandomization",
            "obstacleScale",

            "maxTime",
            "timerWaitTime_ms",
            "controlType"
        ]);
        file.StoreCsvLine([
            "duration",
            "finishType"
        ]);
    }

    private static void WriteCommonData(FileAccess file, int id, SimulationParameters p, SimulationResults r)
    {    
        file.StoreLine(""); // add space between simulations

        // write simulation parameters
            StoreObjectsAsCsv(file, [
                id,

                p.droneNum,
                p.weightedDirection,
                p.maximumAngle,

                p.obstacleShape,
                p.obstacleWidth, p.obstacleDepth,
                p.obstacleSpacing,
                p.obstacleRandomization,
                p.obstacleScale,

                p.maxTime,
                p.timerWaitTime_ms,
                p.controlType
            ]);

            // write simulation results
            StoreObjectsAsCsv(file, [
                r.duration,
                r.finishType
            ]);
    }

    private static void StoreObjectsAsCsv(FileAccess file, object[] array)
    {
        string[] s = new string[array.Length];
        for (int i = 0; i < array.Length; i++)
        {
            s[i] = array[i].ToString();
        }
        file.StoreCsvLine(s);
    }

    /*// log drone data to the specified files.
    public void LogData_EE(string filepath){
        var file = FileAccess.Open(filepath, FileAccess.ModeFlags.Write); // open file
        print("writing line")
        file.store_csv_line(["strategy", "droneCount", "maxAngle", "droneID", "entryTime", "exitTime"]) // write header

        for drone in drones.get_children(): // write data
            var log = PackedStringArray([strategy, simulator.droneNum, rad_to_deg(simulator.Maximum_Angle), drone.get_instance_id(), drone.time_entered, drone.time_exited])
            file.store_csv_line(log)

        file.close()} // prevent data leaks

    // writes continuous motionplan data to a specified output file.
    func log_data_cont(filepath: String) :
        var file = FileAccess.open(filepath, FileAccess.WRITE) // open file

        for e in motionplan_data_array: // write data
            var log = PackedStringArray(e)
            file.store_csv_line(log)

        file.close() // prevent data leaks*/

}