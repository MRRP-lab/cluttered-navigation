# Swarm Analytics - Taiming YuenJames
# Processes data files to compute and visualize makespan and traversal statistics for drone navigation strategies

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment
import scipy.stats

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
            if len(vals) < 7 or vals[5].strip() == '<null>' or vals[6].strip() == '<null>':
                continue
            try:
                timeStamp = int(vals[4])
                x, y = float(vals[5]), float(vals[6])
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
        # Use the first non-empty time step as reference
        for t in sorted(positionsByTime):
            arr = np.array(positionsByTime[t])
            if arr.size > 0:
                referenceArray = arr
                break
        else:
            return None
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

def barChart(data, errors, title, yLabel):
    """Plot a bar chart with error bars and annotate each bar with its integer value centered in the bar."""
    strategies = ['centralized', 'decentralized']
    yValues = [next((val for strat, val in data if strat == s), None) for s in strategies]
    yErrs = [errors.get(s, 0.0) for s in strategies]
    if any(v is None for v in yValues):
        print(f"Warning: Missing data for one or more strategies in '{title}'. Skipping plot.")
        return
    bars = plt.bar(strategies, yValues, yerr=yErrs, capsize=8)
    plt.title(title)
    plt.ylabel(yLabel)
    plt.xlabel('Strategy')
    # Center annotation vertically in the bar
    for bar, y in zip(bars, yValues):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height / 2, str(int(round(y))),
                 ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    plt.show()

def scatterPlot(data, title, xLabel, yLabel, xIntTicks=False):
    """Plot a scatter plot with least squares linear best-fit line for numeric x/y data."""
    if not data:
        print(f"No data for {title}"); return
    xValues, yValues = zip(*data)
    plt.scatter(xValues, yValues, label='Data Points')
    if len(xValues) > 1:
        # Linear least squares fit
        coeffs = np.polyfit(xValues, yValues, 1)
        poly = np.poly1d(coeffs)
        xFit = np.linspace(min(xValues), max(xValues), 100)
        plt.plot(xFit, poly(xFit), color='red', label='Linear Best Fit')
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

def boxPlot(samplesDict, title, yLabel):
    """Plot a boxplot for each strategy's sample distribution, with wider boxes."""
    strategies = list(samplesDict.keys())
    data = [samplesDict[s] for s in strategies]
    plt.figure(figsize=(7, 6))  # Make the plot larger
    plt.boxplot(data, labels=strategies, patch_artist=True, showmeans=True,
                meanprops={"marker":"o","markerfacecolor":"white","markeredgecolor":"black"},
                widths=0.5)  # Make boxes wider
    plt.title(title)
    plt.ylabel(yLabel)
    plt.xlabel('Strategy')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

# --- Analysis Functions ---

def analyzeFixed(folderType, rootFolder, strategies, xAxis, statFuncs, plotFuncs, plotTitles, xLabel, yLabels, xIntTicks=False):
    """Generalized analysis for bothFixed, angleFixed, and countFixed folders."""
    for strategy in strategies:
        # Build paths for makespan and spatial data
        pathMakespan = os.path.join(rootFolder, 'makespan', strategy, folderType)
        pathSpatial = os.path.join(rootFolder, 'spatial', strategy, folderType)
        # For makespan and traversal
        if os.path.isdir(pathMakespan):
            for statFunc, plotFunc, plotTitle, yLabel in zip(statFuncs, plotFuncs, plotTitles, yLabels):
                data = folderStats(pathMakespan, xAxis, statFunc)
                plotFunc(data, plotTitle.format(strategy), xLabel, yLabel, xIntTicks)
        # For EMD
        if os.path.isdir(pathSpatial):
            emdData = folderStats(pathSpatial, xAxis, extractEmd)
            scatterPlot(emdData, plotTitles[-1].format(strategy), xLabel, yLabels[-1], xIntTicks)

def extractMakespanSamples(filePath):
    """Return a list of exit times for all drones in the file (for margin of error calculation)."""
    exitTimes = []
    with open(filePath) as file:
        for line in file:
            vals = line.strip().split(',')
            if len(vals) < 6 or vals[5].strip() == '<null>':
                continue
            try:
                exitTime = float(vals[5])
                exitTimes.append(exitTime)
            except ValueError:
                continue
    return exitTimes

def extractTraversalSamples(filePath):
    """Return a list of traversal times (exit-entry) for all drones in the file (for margin of error calculation)."""
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
    return traversalTimes

def extractEmdSamples(filePath, referenceArray=None):
    """Return a list of EMD values for all time steps in a spatial file (for margin of error calculation)."""
    positionsByTime = parseSpatialFile(filePath)
    if not positionsByTime:
        return []
    if referenceArray is None:
        for t in sorted(positionsByTime):
            arr = np.array(positionsByTime[t])
            if arr.size > 0:
                referenceArray = arr
                break
        else:
            return []
    emdVals = []
    for t in sorted(positionsByTime):
        positionsArray = np.array(positionsByTime[t])
        emd = computeWasserstein(positionsArray, referenceArray)
        if emd is not None:
            emdVals.append(emd)
    return emdVals

def getStrategySamples(folderPath, sampleFunc):
    """Aggregate all samples for a strategy from all .txt files in a folder."""
    samples = []
    for fileName in os.listdir(folderPath):
        if not fileName.endswith('.txt'):
            continue
        filePath = os.path.join(folderPath, fileName)
        samples.extend(sampleFunc(filePath))
    return samples

def marginOfError(samples, confidence=0.95):
    """Calculate the margin of error for a list of samples at the given confidence level."""
    n = len(samples)
    if n < 2:
        return 0.0
    mean = np.mean(samples)
    sem = scipy.stats.sem(samples)
    h = sem * scipy.stats.t.ppf((1 + confidence) / 2, n - 1)
    return h

def main():
    """Main function to run all analyses and plots for the experiment data."""
    rootFolder = 'F:\\files\\school\\wwu\\research\\robotics\\simulationSwarm\\cluttered-navigation\\plinko-drones\\analytics\\sampleOutput\\root' # Update this path as needed
    if not os.path.isdir(rootFolder):
        print(f"Warning: root folder '{rootFolder}' does not exist. Please update the path."); return
    strategies = ['centralized', 'decentralized']
    # Both Fixed
    makespanSamplesDict, traversalSamplesDict, emdSamplesDict = {}, {}, {}
    for strategy in strategies:
        pathMakespan = os.path.join(rootFolder, 'makespan', strategy, 'bothFixed')
        pathSpatial = os.path.join(rootFolder, 'spatial', strategy, 'bothFixed')
        if os.path.isdir(pathMakespan):
            makespanSamples = getStrategySamples(pathMakespan, extractMakespanSamples)
            traversalSamples = getStrategySamples(pathMakespan, extractTraversalSamples)
            makespanSamplesDict[strategy] = makespanSamples
            traversalSamplesDict[strategy] = traversalSamples
        if os.path.isdir(pathSpatial):
            emdSamples = getStrategySamples(pathSpatial, extractEmdSamples)
            emdSamplesDict[strategy] = emdSamples
    boxPlot(makespanSamplesDict, 'Makespan by Strategy (Angle & Count Fixed)', 'Makespan (ms)')
    boxPlot(traversalSamplesDict, 'Average Traversal Time by Strategy (Angle & Count Fixed)', 'Average Traversal Time (ms)')
    boxPlot(emdSamplesDict, 'EMD by Strategy (Angle & Count Fixed)', 'Wasserstein EMD')
    # Angle Fixed
    analyzeFixed(
        'angleFixed', rootFolder, strategies, 'droneCount',
        [extractMakespan, extractTraversal],
        [scatterPlot, scatterPlot, scatterPlot],
        [
            'Makespan vs. Drone Count for {} (Angle Fixed at 40°)',
            'Average Traversal Time vs. Drone Count for {} (Angle Fixed at 40°)',
            'EMD vs. Drone Count for {} (Angle Fixed at 40°)'
        ],
        'Drone Count',
        ['Makespan (ms)', 'Average Traversal Time (ms)', 'Wasserstein EMD'],
        xIntTicks=True
    )
    # Count Fixed
    analyzeFixed(
        'countFixed', rootFolder, strategies, 'angle',
        [extractMakespan, extractTraversal],
        [scatterPlot, scatterPlot, scatterPlot],
        [
            'Makespan vs. Angle for {} (Drone Count Fixed at 10)',
            'Average Traversal Time vs. Angle for {} (Drone Count Fixed at 10)',
            'EMD vs. Angle for {} (Drone Count Fixed at 10)'
        ],
        'Angle (degrees)',
        ['Makespan (ms)', 'Average Traversal Time (ms)', 'Wasserstein EMD'],
        xIntTicks=True
    )

if __name__ == "__main__":
    main()
