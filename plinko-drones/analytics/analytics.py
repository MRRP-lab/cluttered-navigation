# Swarm Analytics - Taiming YuenJames
# Processes data files to compute and visualize makespan and traversal statistics for drone navigation strategies

import os
import numpy as np
import matplotlib.pyplot as plt
import glob

def makespanSingleFile(filePath):
    """Return makespan (last exit - first exit) for valid lines in file, or None if invalid."""
    minExit, maxExit = float('inf'), float('-inf')
    with open(filePath) as file:
        for line in file:
            vals = line.strip().split(',')
            # Skip lines with missing or malformed exit time
            if len(vals) < 6 or vals[5].strip() == '<null>':
                continue
            try:
                exitTime = float(vals[5])
                minExit = min(minExit, exitTime)
                maxExit = max(maxExit, exitTime)
            except ValueError:
                continue
    # Return makespan only if valid exit times were found
    return maxExit - minExit if minExit != float('inf') and maxExit != float('-inf') else None

def makespanFolder(folderPath, xAxis):
    """Return list of (x, makespan) for all .txt files in folder, x from first line (droneCount/angle)."""
    data = []
    for fileName in os.listdir(folderPath):
        if not fileName.endswith('.txt'):
            continue
        filePath = os.path.join(folderPath, fileName)
        try:
            with open(filePath) as file:
                vals = file.readline().strip().split(',')
                # Extract x value from first line (droneCount or angle)
                if len(vals) < 3:
                    continue
                xValue = int(vals[1]) if xAxis == 'droneCount' else float(vals[2])
        except Exception:
            continue
        makespan = makespanSingleFile(filePath)
        if makespan is not None:
            data.append((xValue, makespan))
    return data

def traversalSingleFile(filePath):
    """Return average traversal time (exit-entry) for valid lines in file, or None if invalid."""
    traversalTimes = []
    with open(filePath) as file:
        for line in file:
            vals = line.strip().split(',')
            # Skip lines with missing or malformed entry/exit times
            if len(vals) < 6 or vals[5].strip() == '<null>':
                continue
            try:
                entryTime, exitTime = float(vals[4]), float(vals[5])
                traversal = exitTime - entryTime
                if traversal >= 0:
                    traversalTimes.append(traversal)
            except ValueError:
                continue
    # Return average traversal time if any valid times found
    return sum(traversalTimes) / len(traversalTimes) if traversalTimes else None

def traversalFolder(folderPath, xAxis):
    """Return list of (x, avgTraversalTime) for all .txt files in folder, x from first line (droneCount/angle)."""
    data = []
    for fileName in os.listdir(folderPath):
        if not fileName.endswith('.txt'):
            continue
        filePath = os.path.join(folderPath, fileName)
        try:
            with open(filePath) as file:
                vals = file.readline().strip().split(',')
                # Extract x value from first line (droneCount or angle)
                if len(vals) < 3:
                    continue
                xValue = int(vals[1]) if xAxis == 'droneCount' else float(vals[2])
        except Exception:
            continue
        avgTraversal = traversalSingleFile(filePath)
        if avgTraversal is not None:
            data.append((xValue, avgTraversal))
    return data

def barChart(data, title, yLabel):
    """Plot a bar chart comparing decentralized and centralized strategies."""
    strategies = ['Decentralized', 'Centralized']
    yValues = [next((val for strat, val in data if strat.lower() == s.lower()), None) for s in strategies]
    plt.bar(strategies, yValues)
    plt.title(title)
    plt.ylabel(yLabel)
    plt.xlabel('Strategy')
    plt.show()

def scatterPlot(data, title, xLabel, yLabel, xIntTicks=False):
    """Plot a scatter plot with quadratic best-fit curve for numeric x/y data."""
    if not data:
        print(f"No data for {title}"); return
    xValues, yValues = zip(*data)
    plt.scatter(xValues, yValues, label='Data Points')
    # Fit and plot a quadratic curve if there are enough points
    if len(xValues) > 1:
        coeffs = np.polyfit(xValues, yValues, 2)
        poly = np.poly1d(coeffs)
        xFit = np.linspace(min(xValues), max(xValues), 100)
        plt.plot(xFit, poly(xFit), color='red', label='Quadratic Best Fit')
    plt.title(title)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    if xIntTicks:
        xMin, xMax = int(min(xValues)), int(max(xValues))
        # For drone count, start at 0, then 5, 10, 15, 20
        if xLabel.lower().startswith('drone count'):
            plt.xticks(np.arange(0, xMax+1, 5))
        else:
            step = 5 if xMax - xMin > 6 else 1
            plt.xticks(np.arange(xMin, xMax+1, step))
    plt.legend()
    plt.show()

def analyzeBothFixed(rootFolder, strategies):
    """Analyze and plot makespan and average traversal time for angle and count fixed (by strategy)."""
    makespanData, traversalData = [], []
    for strategy in strategies:
        path = os.path.join(rootFolder, 'makespan', strategy.lower(), 'bothFixed')
        if os.path.isdir(path):
            # Only use the first .txt file found for each strategy
            fileName = next((f for f in os.listdir(path) if f.endswith('.txt')), None)
            if fileName:
                filePath = os.path.join(path, fileName)
                makespan = makespanSingleFile(filePath)
                traversal = traversalSingleFile(filePath)
                makespanData.append((strategy, makespan))
                traversalData.append((strategy, traversal))
    # Ensure only two tuples: one for each strategy
    makespanData = [t for t in makespanData if t[0].lower() in ('decentralized', 'centralized')][:2]
    traversalData = [t for t in traversalData if t[0].lower() in ('decentralized', 'centralized')][:2]
    barChart(makespanData, 'Makespan by Strategy (Angle & Count Fixed)', 'Makespan (ms)')
    barChart(traversalData, 'Average Traversal Time by Strategy (Angle & Count Fixed)', 'Average Traversal Time (ms)')

def analyzeAngleFixed(rootFolder, strategies):
    """Analyze and plot makespan and average traversal time versus drone count for each strategy (angle fixed)."""
    for strategy in strategies:
        stratLabel = 'Centralized' if strategy.lower() == 'centralized' else 'Decentralized'
        path = os.path.join(rootFolder, 'makespan', strategy.lower(), 'angleFixed')
        if os.path.isdir(path):
            makespanData = makespanFolder(path, 'droneCount')
            traversalData = traversalFolder(path, 'droneCount')
            scatterPlot(makespanData, f'Makespan vs. Drone Count for {stratLabel} (Angle Fixed at 40°)', 'Drone Count', 'Makespan (ms)', xIntTicks=True)
            scatterPlot(traversalData, f'Average Traversal Time vs. Drone Count for {stratLabel} (Angle Fixed at 40°)', 'Drone Count', 'Average Traversal Time (ms)', xIntTicks=True)

def analyzeCountFixed(rootFolder, strategies):
    """Analyze and plot makespan and average traversal time versus angle for each strategy (drone count fixed)."""
    for strategy in strategies:
        stratLabel = 'Centralized' if strategy.lower() == 'centralized' else 'Decentralized'
        path = os.path.join(rootFolder, 'makespan', strategy.lower(), 'countFixed')
        if os.path.isdir(path):
            makespanData = makespanFolder(path, 'angle')
            traversalData = traversalFolder(path, 'angle')
            scatterPlot(makespanData, f'Makespan vs. Angle for {stratLabel} (Drone Count Fixed at 10)', 'Angle (degrees)', 'Makespan (ms)', xIntTicks=True)
            scatterPlot(traversalData, f'Average Traversal Time vs. Angle for {stratLabel} (Drone Count Fixed at 10)', 'Angle (degrees)', 'Average Traversal Time (ms)', xIntTicks=True)

def test(directory=None):
    """Visualize makespan and avg traversal time for all .txt files in directory as bar charts."""
    if directory is None:
        directory = os.getcwd()
    files = glob.glob(os.path.join(directory, '*.txt'))
    makespanData = [(os.path.basename(f), makespanSingleFile(f)) for f in files if makespanSingleFile(f) is not None]
    traversalData = [(os.path.basename(f), traversalSingleFile(f)) for f in files if traversalSingleFile(f) is not None]
    barChart(makespanData, 'Makespan for Present Files', 'Makespan')
    barChart(traversalData, 'Avg Traversal Time for Present Files', 'Avg Traversal Time')

def main():
    """Main function to run all analyses and plots for the experiment data."""
    rootFolder = 'F:\\files\\school\\wwu\\research\\robotics\\simulationSwarm\\cluttered-navigation\\plinko-drones\\analytics\\sampleOutput\\root' # Update this path as needed
    if not os.path.isdir(rootFolder):
        print(f"Warning: root folder '{rootFolder}' does not exist. Please update the path."); return
    strategies = ['centralized', 'decentralized']
    analyzeBothFixed(rootFolder, strategies)
    analyzeAngleFixed(rootFolder, strategies)
    analyzeCountFixed(rootFolder, strategies)

if __name__ == "__main__":
    main()  # Uncomment to run full analysis
