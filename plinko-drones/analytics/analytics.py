# Swarm Analytics - Taiming YuenJames
# Processes data files to compute and visualize makespan and traversal statistics for drone navigation strategies

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment

# --- Utility Functions ---

def readFirstLineValue(filePath, xAxis):
    """Extract x value (droneCount or angle) from the first line of a file."""
    try:
        with open(filePath) as file:
            vals = file.readline().strip().split(',')
            if len(vals) < 3:
                return None
            return int(vals[1]) if xAxis == 'droneCount' else float(vals[2])
    except Exception:
        return None

def parseSpatialFile(filePath):
    """Parse a spatial log file into a dict: timeStamp -> list of (x, y) positions."""
    positionsByTime = {}
    with open(filePath) as file:
        for line in file:
            vals = line.strip().split(',')
            if len(vals) < 6 or vals[5].strip() == '<null>':
                continue
            try:
                timeStamp = int(vals[4])
                x, y = float(vals[0]), float(vals[1])
                positionsByTime.setdefault(timeStamp, []).append((x, y))
            except ValueError:
                continue
    return positionsByTime

def computeWasserstein(positionsA, positionsB):
    """Compute Wasserstein EMD between two 2D point sets."""
    if not positionsA.size or not positionsB.size:
        return None
    costMatrix = cdist(positionsA, positionsB)
    rowInd, colInd = linear_sum_assignment(costMatrix)
    return costMatrix[rowInd, colInd].mean()

# --- Data Extraction Functions ---

def extractMakespan(filePath):
    """Return makespan (last exit - first exit) for valid lines in file, or None if invalid."""
    minExit, maxExit = float('inf'), float('-inf')
    with open(filePath) as file:
        for line in file:
            vals = line.strip().split(',')
            if len(vals) < 6 or vals[5].strip() == '<null>':
                continue
            try:
                exitTime = float(vals[5])
                minExit = min(minExit, exitTime)
                maxExit = max(maxExit, exitTime)
            except ValueError:
                continue
    return maxExit - minExit if minExit != float('inf') and maxExit != float('-inf') else None

def extractTraversal(filePath):
    """Return average traversal time (exit-entry) for valid lines in file, or None if invalid."""
    traversalTimes = []
    with open(filePath) as file:
        for line in file:
            vals = line.strip().split(',')
            if len(vals) < 6 or vals[5].strip() == '<null>':
                continue
            try:
                entryTime, exitTime = float(vals[4]), float(vals[5])
                traversal = exitTime - entryTime
                if traversal >= 0:
                    traversalTimes.append(traversal)
            except ValueError:
                continue
    return np.mean(traversalTimes) if traversalTimes else None

def extractEmd(filePath, referenceArray=None):
    """Return average EMD over all time steps in a spatial file."""
    positionsByTime = parseSpatialFile(filePath)
    if not positionsByTime:
        return None
    if referenceArray is None:
        referenceArray = np.array(positionsByTime.get(0, []))
    emdVals = []
    for t in sorted(positionsByTime):
        positionsArray = np.array(positionsByTime[t])
        emd = computeWasserstein(positionsArray, referenceArray)
        if emd is not None:
            emdVals.append(emd)
    return np.mean(emdVals) if emdVals else None

def folderStats(folderPath, xAxis, statFunc):
    """Return list of (x, stat) for all .txt files in folder using statFunc."""
    data = []
    for fileName in os.listdir(folderPath):
        if not fileName.endswith('.txt'):
            continue
        filePath = os.path.join(folderPath, fileName)
        xValue = readFirstLineValue(filePath, xAxis)
        if xValue is None:
            continue
        stat = statFunc(filePath)
        if stat is not None:
            data.append((xValue, stat))
    return data

# --- Plotting Functions ---

def barChart(data, title, yLabel):
    """Plot a bar chart comparing decentralized and centralized strategies."""
    strategies = ['Decentralized', 'Centralized']
    yValues = [next((val for strat, val in data if strat.lower() == s.lower()), None) for s in strategies]
    if any(v is None for v in yValues):
        print(f"Warning: Missing data for one or more strategies in '{title}'. Skipping plot.")
        return
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
        if xLabel.lower().startswith('drone count'):
            plt.xticks(np.arange(0, xMax+1, 5))
        else:
            step = 5 if xMax - xMin > 6 else 1
            plt.xticks(np.arange(xMin, xMax+1, step))
    plt.legend()
    plt.show()

# --- Analysis Functions ---

def analyzeBothFixed(rootFolder, strategies):
    """Analyze and plot makespan, traversal time, and EMD for angle and count fixed (by strategy)."""
    makespanData, traversalData, emdData = [], [], []
    for strategy in strategies:
        stratLabel = 'Centralized' if strategy.lower() == 'centralized' else 'Decentralized'
        pathMakespan = os.path.join(rootFolder, 'makespan', strategy.lower(), 'bothFixed')
        pathSpatial = os.path.join(rootFolder, 'spatial', strategy.lower(), 'bothFixed')
        if os.path.isdir(pathMakespan):
            fileName = next((f for f in os.listdir(pathMakespan) if f.endswith('.txt')), None)
            if fileName:
                filePath = os.path.join(pathMakespan, fileName)
                makespan = extractMakespan(filePath)
                traversal = extractTraversal(filePath)
                makespanData.append((stratLabel, makespan))
                traversalData.append((stratLabel, traversal))
        if os.path.isdir(pathSpatial):
            fileName = next((f for f in os.listdir(pathSpatial) if f.endswith('.txt')), None)
            if fileName:
                filePath = os.path.join(pathSpatial, fileName)
                emd = extractEmd(filePath)
                emdData.append((stratLabel, emd))
    barChart(makespanData, 'Makespan by Strategy (Angle & Count Fixed)', 'Makespan (ms)')
    barChart(traversalData, 'Average Traversal Time by Strategy (Angle & Count Fixed)', 'Average Traversal Time (ms)')
    barChart(emdData, 'EMD by Strategy (Angle & Count Fixed)', 'Wasserstein EMD')

def analyzeAngleFixed(rootFolder, strategies):
    """Analyze and plot makespan, traversal time, and EMD versus drone count for each strategy (angle fixed)."""
    for strategy in strategies:
        stratLabel = 'Centralized' if strategy.lower() == 'centralized' else 'Decentralized'
        pathMakespan = os.path.join(rootFolder, 'makespan', strategy.lower(), 'angleFixed')
        pathSpatial = os.path.join(rootFolder, 'spatial', strategy.lower(), 'angleFixed')
        if os.path.isdir(pathMakespan):
            makespanData = folderStats(pathMakespan, 'droneCount', extractMakespan)
            traversalData = folderStats(pathMakespan, 'droneCount', extractTraversal)
            scatterPlot(makespanData, f'Makespan vs. Drone Count for {stratLabel} (Angle Fixed at 40°)', 'Drone Count', 'Makespan (ms)', xIntTicks=True)
            scatterPlot(traversalData, f'Average Traversal Time vs. Drone Count for {stratLabel} (Angle Fixed at 40°)', 'Drone Count', 'Average Traversal Time (ms)', xIntTicks=True)
        if os.path.isdir(pathSpatial):
            emdData = folderStats(pathSpatial, 'droneCount', extractEmd)
            scatterPlot(emdData, f'EMD vs. Drone Count for {stratLabel} (Angle Fixed at 40°)', 'Drone Count', 'Wasserstein EMD', xIntTicks=True)

def analyzeCountFixed(rootFolder, strategies):
    """Analyze and plot makespan, traversal time, and EMD versus angle for each strategy (drone count fixed)."""
    for strategy in strategies:
        stratLabel = 'Centralized' if strategy.lower() == 'centralized' else 'Decentralized'
        pathMakespan = os.path.join(rootFolder, 'makespan', strategy.lower(), 'countFixed')
        pathSpatial = os.path.join(rootFolder, 'spatial', strategy.lower(), 'countFixed')
        if os.path.isdir(pathMakespan):
            makespanData = folderStats(pathMakespan, 'angle', extractMakespan)
            traversalData = folderStats(pathMakespan, 'angle', extractTraversal)
            scatterPlot(makespanData, f'Makespan vs. Angle for {stratLabel} (Drone Count Fixed at 10)', 'Angle (degrees)', 'Makespan (ms)', xIntTicks=True)
            scatterPlot(traversalData, f'Average Traversal Time vs. Angle for {stratLabel} (Drone Count Fixed at 10)', 'Angle (degrees)', 'Average Traversal Time (ms)', xIntTicks=True)
        if os.path.isdir(pathSpatial):
            emdData = folderStats(pathSpatial, 'angle', extractEmd)
            scatterPlot(emdData, f'EMD vs. Angle for {stratLabel} (Drone Count Fixed at 10)', 'Angle (degrees)', 'Wasserstein EMD', xIntTicks=True)

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
    main()
