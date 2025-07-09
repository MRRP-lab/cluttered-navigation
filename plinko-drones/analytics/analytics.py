# Swarm Analytics - Taiming YuenJames
# This script processes data files to compute and visualize makespan and spatial statistics for comparing drone navigation strategies

import os  # For file and directory operations
import scipy as sp  # For spacial distribution computing
import numpy as np  # For numerical operations and polynomial fitting
import matplotlib.pyplot as plt  # For plotting charts

# --- Makespan Calculation for a Single File ---
def makespanSingleFile(filePath):
    """
    Parses a single data file and computes the makespan for a given experiment.
    Makespan is defined as the difference between the earliest entry time and the latest exit time among all drones.
    Skips lines with malformed data or missing exit times.
    """
    minEntry, maxExit = float('inf'), float('-inf')  # Initialize to extreme values
    with open(filePath, 'r') as file:
        for i, line in enumerate(file):
            vals = line.strip().split(',')
            if len(vals) < 6:
                continue  # Skip lines that don't have enough columns
            if vals[5].strip() == '<null>':
                continue  # Skip lines with missing exit time
            try:
                entryTime = float(vals[4])  # Entry time is at index 4
                exitTime = float(vals[5])   # Exit time is at index 5
                minEntry = min(minEntry, entryTime)
                maxExit = max(maxExit, exitTime)
            except ValueError:
                continue  # Skip lines with non-numeric entry/exit times
    # Only return makespan if valid times were found
    makespanVal = maxExit - minEntry if minEntry != float('inf') and maxExit != float('-inf') else None
    return makespanVal

# --- Makespan Calculation for a Folder of Files ---
def makespanFolder(folderPath, xAxis):
    """
    Collects (x, makespan) data from all .txt files in a folder for plotting.
    The x value is extracted from the first line of each file: droneCount (index 1) or angle (index 2).
    Ignores files that do not have valid data or x values.
    """
    data = []  # List to store (x, makespan) tuples
    for fileName in os.listdir(folderPath):
        if not fileName.endswith('.txt'):
            continue  # Only process .txt files
        filePath = os.path.join(folderPath, fileName)
        xValue = None  # Initialize x value
        try:
            with open(filePath, 'r') as f:
                firstLine = f.readline()
                vals = firstLine.strip().split(',')
                if len(vals) < 3:
                    xValue = None  # Not enough columns to extract x value
                elif xAxis == 'droneCount':
                    xValue = int(vals[1])  # droneCount is at index 1
                elif xAxis == 'angle':
                    xValue = float(vals[2])  # angle is at index 2
        except Exception:
            xValue = None  # If any error occurs, skip this file
        yValue = makespanSingleFile(filePath)  # Compute makespan for the file
        if xValue is not None and yValue is not None:
            data.append((xValue, yValue))  # Only add valid data
    return data

# --- Bar Chart Plotting ---
def barChart(data, title):
    """
    Plots a bar chart for makespan by strategy (used for bothFixed analysis).
    Expects data as a list of (x, makespan) tuples, where x is typically the strategy name.
    """
    if not data:
        print(f"No data for {title}")
        return
    xValues, yValues = zip(*data)  # Unpack x and y values
    plt.bar(xValues, yValues)
    plt.title(title)
    plt.ylabel('Makespan')
    plt.xlabel('Strategy')
    plt.show()

# --- Scatter Plot with Quadratic Fit ---
def scatterPlot(data, title, xLabel, yLabel):
    """
    Plots a scatter plot with a quadratic best-fit curve for makespan analysis.
    Expects data as a list of (x, makespan) tuples.
    """
    if not data:
        print(f"No data for {title}")
        return
    xValues, yValues = zip(*data)
    plt.scatter(xValues, yValues, label='Data Points')  # Plot raw data points
    # Fit and plot a quadratic curve if there are enough points
    if len(xValues) > 1:
        coeffs = np.polyfit(xValues, yValues, deg=2)  # Quadratic fit
        poly = np.poly1d(coeffs)
        xFit = np.linspace(min(xValues), max(xValues), 100)
        yFit = poly(xFit)
        plt.plot(xFit, yFit, color='red', label='Best Fit Curve')
    plt.title(title)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.legend()
    plt.show()

# --- Test Utility for Makespan Calculation ---
def testMakespan():
    """
    Test utility to visualize the makespan calculation for multiple files using the scatterPlot function.
    Plots makespan for decentralizedMakespan10.txt, 15.txt, and 20.txt in a single scatter plot for comparison.
    """
    fileList = [
        # List of test files for decentralized strategy with different drone counts
        'f:/files/school/wwu/research/robotics/simulationSwarm/cluttered-navigation/pinko-drones/analytics/sampleOutput/decentralizedMakespan10.txt',
        'f:/files/school/wwu/research/robotics/simulationSwarm/cluttered-navigation/pinko-drones/analytics/sampleOutput/decentralizedMakespan15.txt',
        'f:/files/school/wwu/research/robotics/simulationSwarm/cluttered-navigation/pinko-drones/analytics/sampleOutput/decentralizedMakespan20.txt'
    ]
    xAxis = 'droneCount'  # We are comparing by drone count
    data = []  # List to store (droneCount, makespan) tuples
    labels = []  # List to store labels for annotation
    for filePath in fileList:
        # Extract droneCount from filename (assumes number in filename is drone count)
        fileName = os.path.basename(filePath)
        try:
            xValue = int(''.join(filter(str.isdigit, fileName)))
        except Exception:
            xValue = None
        makespanVal = makespanSingleFile(filePath)
        print(f"File: {filePath}")
        print(f"xValue ({xAxis}): {xValue}")
        print(f"Makespan: {makespanVal}")
        if xValue is not None and makespanVal is not None:
            data.append((xValue, makespanVal))
            labels.append(str(xValue))
        else:
            print("No valid data to plot for this file.")
    if data:
        xValues, yValues = zip(*data)
        plt.scatter(xValues, yValues, label='Data Points')
        for i, label in enumerate(labels):
            plt.annotate(label, (xValues[i], yValues[i]), textcoords="offset points", xytext=(0,10), ha='center')
        if len(xValues) > 1:
            coeffs = np.polyfit(xValues, yValues, deg=2)
            poly = np.poly1d(coeffs)
            xFit = np.linspace(min(xValues), max(xValues), 100)
            yFit = poly(xFit)
            plt.plot(xFit, yFit, color='red', label='Best Fit Curve')
        plt.title("Makespan Comparison for Decentralized (10, 15, 20 Drones)")
        plt.xlabel(xAxis)
        plt.ylabel("Makespan")
        plt.legend()
        plt.show()
    else:
        print("No valid data to plot.")

# --- Main Analysis and Plotting Routine ---
def main():
    """
    Main function to traverse the folder structure and generate all required plots for makespan analysis.
    Generates bar and scatter plots for both centralized and decentralized strategies, for bothFixed, angleFixed, and countFixed experiments.
    """
    rootFolder = './root'  # Path to the root data folder (update as needed)
    if not os.path.isdir(rootFolder):
        print(f"Warning: root folder '{rootFolder}' does not exist. Please update the path.")
        return
    strategies = ['centralized', 'decentralized']  # The two navigation strategies
    dataBoth = []  # List to store (strategy, makespan) tuples for bothFixed
    
    for strategy in strategies:
        # --- Both Fixed: Compare makespan for each strategy ---
        bothFixedPath = os.path.join(rootFolder, 'makespan', strategy, 'bothFixed')
        if os.path.isdir(bothFixedPath):
            files = [f for f in os.listdir(bothFixedPath) if f.endswith('.txt')]
            if files:
                filePath = os.path.join(bothFixedPath, files[0])  # Use the first file found
                makespanVal = makespanSingleFile(filePath)
                dataBoth.append((strategy, makespanVal))
    barChart(dataBoth, "Makespan by Strategy (Both Fixed)")  # Plot bar chart for bothFixed

    for strategy in strategies:
        # --- Angle Fixed: Makespan vs Angle for each strategy ---
        angleFixedPath = os.path.join(rootFolder, 'makespan', strategy, 'angleFixed')
        if os.path.isdir(angleFixedPath):
            dataAngle = makespanFolder(angleFixedPath, 'angle')
            scatterPlot(dataAngle, f"Makespan vs Angle ({strategy.capitalize()})", xLabel="Angle", yLabel="Makespan")
        # --- Count Fixed: Makespan vs Drone Count for each strategy ---
        countFixedPath = os.path.join(rootFolder, 'makespan', strategy, 'countFixed')
        if os.path.isdir(countFixedPath):
            dataCount = makespanFolder(countFixedPath, 'droneCount')
            scatterPlot(dataCount, f"Makespan vs Drone Count ({strategy.capitalize()})", xLabel="Drone Count", yLabel="Makespan")

# --- Entry Point ---
if __name__ == "__main__":
    testMakespan()  # Run test utility by default
#    main()  # Uncomment to run full analysis
