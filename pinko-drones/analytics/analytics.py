# Swarm Analytics - Taiming YuenJames
# This script processes data files to compute and visualize makespan and spatial statistics for comparing drone navigation strategies

import os
import scipy as sp
import numpy as np
import matplotlib.pyplot as plt

def makespan(filePath, xAxis):
    """
    Parses a data file and computes the makespan for a given experiment.

    Args:
        filePath (str): Path to the data file.
        xAxis (str): The variable to use as the x-axis ('droneCount' or 'angle').

    Returns:
        tuple: (xValue, makespanVal) where xValue is either the drone count or angle, and makespanVal is the makespan.
    """
    # Initialize min/max entry/exit times and placeholders for drone count and angle
    minEntry, maxExit = float('inf'), float('-inf')
    droneCount, angle = None, None
    # Read the file line by line
    with open(filePath, 'r') as file:
        for i, line in enumerate(file):
            vals = line.strip().split(',')
            if len(vals) < 6:
                continue  # Skip malformed lines
            # Only store the value needed for the x axis
            if xAxis == 'angle' and i == 0:
                angle = vals[2].strip()
            if xAxis == 'droneCount' and droneCount is None:
                try:
                    droneCount = int(vals[1].strip())
                except:
                    pass  # Skip if drone count is not an integer
            try:
                entryTime = float(vals[4])
                exitTime = float(vals[5])
                minEntry = min(minEntry, entryTime)
                maxExit = max(maxExit, exitTime)
            except ValueError:
                continue  # Skip lines with invalid times
    # Only compute makespan if all required values are present
    makespanVal = maxExit - minEntry if minEntry != float('inf') and maxExit != float('-inf') and droneCount is not None else None
    # Select x value for plotting based on the analysis type
    if xAxis == 'droneCount':
        xValue = droneCount
    elif xAxis == 'angle':
        xValue = float(angle) if angle is not None else None
    else:
        xValue = None
    return (xValue, makespanVal)

def collectMakespanData(folderPath, xAxis):
    """
    Collects (x, makespan) data from all .txt files in a folder for plotting.

    Args:
        folderPath (str): Path to the folder containing data files.
        xAxis (str): The variable to use as the x-axis ('droneCount' or 'angle').

    Returns:
        list: List of (x, makespan) tuples for valid data files.
    """
    data = []
    for dataFile in os.listdir(folderPath):
        if not dataFile.endswith('.txt'):
            continue  # Only process .txt files
        filePath = os.path.join(folderPath, dataFile)
        x, y = makespan(filePath, xAxis)
        if x is not None and y is not None:
            data.append((x, y))  # Only add valid data points
    return data

def barChart(data, title):
    """
    Plots a bar chart for makespan by strategy (used for bothFixed analysis).

    Args:
        data (list): List of (x, makespan) tuples.
        title (str): Title for the plot.
    """
    if not data:
        print(f"No data for {title}")
        return
    x, y = zip(*data)
    plt.bar(x, y)
    plt.title(title)
    plt.ylabel('Makespan')
    plt.xlabel('Strategy')
    plt.show()

def scatterPlot(data, title, xLabel, yLabel):
    """
    Plots a scatter plot with a quadratic best-fit curve for makespan analysis.

    Args:
        data (list): List of (x, makespan) tuples.
        title (str): Title for the plot.
        xLabel (str): Label for the x-axis.
        yLabel (str): Label for the y-axis.
    """
    if not data:
        print(f"No data for {title}")
        return
    x, y = zip(*data)
    plt.scatter(x, y, label='Data Points')
    # Fit and plot a quadratic curve if there are enough points
    if len(x) > 1:
        coeffs = np.polyfit(x, y, deg=2)
        poly = np.poly1d(coeffs)
        xFit = np.linspace(min(x), max(x), 100)
        yFit = poly(xFit)
        plt.plot(xFit, yFit, color='red', label='Best Fit Curve')
    plt.title(title)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.legend()
    plt.show()

def testMakespan():
    """
    Test utility to visualize the makespan calculation for multiple files using the scatterPlot function.
    Plots makespan for decentralizedMakespan10.txt, 15.txt, and 20.txt in a single scatter plot for comparison.
    """
    fileList = [
        'f:/files/school/wwu/research/robotics/simulationSwarm/cluttered-navigation/pinko-drones/analytics/sampleOutput/decentralizedMakespan10.txt',
        'f:/files/school/wwu/research/robotics/simulationSwarm/cluttered-navigation/pinko-drones/analytics/sampleOutput/decentralizedMakespan15.txt',
        'f:/files/school/wwu/research/robotics/simulationSwarm/cluttered-navigation/pinko-drones/analytics/sampleOutput/decentralizedMakespan20.txt'
    ]
    xAxis = 'droneCount'
    data = []
    labels = []
    for filePath in fileList:
        x, makespanVal = makespan(filePath, xAxis)
        print(f"File: {filePath}")
        print(f"xValue ({xAxis}): {x}")
        print(f"Makespan: {makespanVal}")
        if x is not None and makespanVal is not None:
            data.append((x, makespanVal))
            labels.append(str(x))
        else:
            print("No valid data to plot for this file.")
    if data:
        x, y = zip(*data)
        plt.scatter(x, y, label='Data Points')
        for i, label in enumerate(labels):
            plt.annotate(label, (x[i], y[i]), textcoords="offset points", xytext=(0,10), ha='center')
        if len(x) > 1:
            coeffs = np.polyfit(x, y, deg=2)
            poly = np.poly1d(coeffs)
            xFit = np.linspace(min(x), max(x), 100)
            yFit = poly(xFit)
            plt.plot(xFit, yFit, color='red', label='Best Fit Curve')
        plt.title("Makespan Comparison for Decentralized (10, 15, 20 Drones)")
        plt.xlabel(xAxis)
        plt.ylabel("Makespan")
        plt.legend()
        plt.show()
    else:
        print("No valid data to plot.")

def main():
    """
    Main function to traverse the folder structure and generate all required plots for makespan analysis.
    """
    rootFolder = './root'  # Change this to your actual root folder
    for strategy in ['centralized', 'decentralized']:
        strategyPath = os.path.join(rootFolder, 'makespan', strategy)
        # Bar chart for bothFixed: makespan by strategy
        bothFixedPath = os.path.join(strategyPath, 'bothFixed')
        if os.path.isdir(bothFixedPath):
            # Use the strategy name directly for the bar chart
            data = [(strategy, makespan(os.path.join(bothFixedPath, f), 'droneCount')[1])
                    for f in os.listdir(bothFixedPath) if f.endswith('.txt')]
            barChart(data, f"Makespan by Strategy ({strategy.capitalize()})")
        # Scatter plot for angleFixed: makespan vs max angle
        angleFixedPath = os.path.join(strategyPath, 'angleFixed')
        if os.path.isdir(angleFixedPath):
            data = collectMakespanData(angleFixedPath, 'angle')
            scatterPlot(data, f"Makespan vs Max Angle ({strategy.capitalize()})", xLabel="Max Angle", yLabel="Makespan")
        # Scatter plot for countFixed: makespan vs drone count
        countFixedPath = os.path.join(strategyPath, 'countFixed')
        if os.path.isdir(countFixedPath):
            data = collectMakespanData(countFixedPath, 'droneCount')
            scatterPlot(data, f"Makespan vs Drone Count ({strategy.capitalize()})", xLabel="Drone Count", yLabel="Makespan")

if __name__ == "__main__":
    testMakespan()
#    main()
