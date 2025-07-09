# Swarm Analytics - Taiming YuenJames
# Processes data files to compute and visualize makespan and traversal statistics for drone navigation strategies

import os
import numpy as np
import matplotlib.pyplot as plt
import glob

def makespanSingleFile(filePath):
    """Return makespan (max exit - min entry) for valid lines in file, or None if invalid."""
    minEntry, maxExit = float('inf'), float('-inf')
    with open(filePath) as file:
        for line in file:
            vals = line.strip().split(',')
            if len(vals) < 6 or vals[5].strip() == '<null>':
                continue
            try:
                entry, exit = float(vals[4]), float(vals[5])
                minEntry = min(minEntry, entry)
                maxExit = max(maxExit, exit)
            except ValueError:
                continue
    return maxExit - minEntry if minEntry != float('inf') and maxExit != float('-inf') else None

def traversalSingleFile(filePath):
    """Return average traversal time (exit-entry) for valid lines in file, or None if invalid."""
    times = []
    with open(filePath) as file:
        for line in file:
            vals = line.strip().split(',')
            if len(vals) < 6 or vals[5].strip() == '<null>':
                continue
            try:
                entry, exit = float(vals[4]), float(vals[5])
                t = exit - entry
                if t >= 0:
                    times.append(t)
            except ValueError:
                continue
    return sum(times) / len(times) if times else None

def makespanFolder(folderPath, xAxis):
    """Return list of (x, makespan) for all .txt files in folder, x from first line (droneCount/angle)."""
    data = []
    for fileName in os.listdir(folderPath):
        if not fileName.endswith('.txt'): continue
        filePath = os.path.join(folderPath, fileName)
        try:
            with open(filePath) as f:
                vals = f.readline().strip().split(',')
                if len(vals) < 3: continue
                x = int(vals[1]) if xAxis == 'droneCount' else float(vals[2])
        except Exception:
            continue
        y = makespanSingleFile(filePath)
        if y is not None:
            data.append((x, y))
    return data

def traversalFolder(folderPath, xAxis):
    """Return list of (x, avgTraversalTime) for all .txt files in folder, x from first line (droneCount/angle)."""
    data = []
    for fileName in os.listdir(folderPath):
        if not fileName.endswith('.txt'): continue
        filePath = os.path.join(folderPath, fileName)
        try:
            with open(filePath) as f:
                vals = f.readline().strip().split(',')
                if len(vals) < 3: continue
                x = int(vals[1]) if xAxis == 'droneCount' else float(vals[2])
        except Exception:
            continue
        y = traversalSingleFile(filePath)
        if y is not None:
            data.append((x, y))
    return data

def barChart(data, title, yLabel):
    if not data:
        print(f"No data for {title}"); return
    x, y = zip(*data)
    plt.bar(x, y)
    plt.title(title)
    plt.ylabel(yLabel)
    plt.xlabel('Strategy' if all(isinstance(i, str) for i in x) else 'File')
    plt.show()

def scatterPlot(data, title, xLabel, yLabel):
    if not data:
        print(f"No data for {title}"); return
    x, y = zip(*data)
    plt.scatter(x, y, label='Data Points')
    if len(x) > 1:
        coeffs = np.polyfit(x, y, 2)
        poly = np.poly1d(coeffs)
        xFit = np.linspace(min(x), max(x), 100)
        plt.plot(xFit, poly(xFit), color='red', label='Best Fit Curve')
    plt.title(title)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.legend()
    plt.show()

def analyzeBothFixed(rootFolder, strategies):
    ms, tr = [], []
    for s in strategies:
        p = os.path.join(rootFolder, 'makespan', s, 'bothFixed')
        if os.path.isdir(p):
            f = next((f for f in os.listdir(p) if f.endswith('.txt')), None)
            if f:
                fp = os.path.join(p, f)
                ms.append((s, makespanSingleFile(fp)))
                tr.append((s, traversalSingleFile(fp)))
    barChart(ms, 'Makespan by Strategy (Both Fixed)', 'Makespan')
    barChart(tr, 'Avg Traversal Time by Strategy (Both Fixed)', 'Avg Traversal Time')

def analyzeAngleFixed(rootFolder, strategies):
    for s in strategies:
        p = os.path.join(rootFolder, 'makespan', s, 'angleFixed')
        if os.path.isdir(p):
            ms = makespanFolder(p, 'angle')
            tr = traversalFolder(p, 'angle')
            scatterPlot(ms, f'Makespan vs Angle ({s.capitalize()})', 'Angle', 'Makespan')
            scatterPlot(tr, f'Avg Traversal Time vs Angle ({s.capitalize()})', 'Angle', 'Avg Traversal Time')

def analyzeCountFixed(rootFolder, strategies):
    for s in strategies:
        p = os.path.join(rootFolder, 'makespan', s, 'countFixed')
        if os.path.isdir(p):
            ms = makespanFolder(p, 'droneCount')
            tr = traversalFolder(p, 'droneCount')
            scatterPlot(ms, f'Makespan vs Drone Count ({s.capitalize()})', 'Drone Count', 'Makespan')
            scatterPlot(tr, f'Avg Traversal Time vs Drone Count ({s.capitalize()})', 'Drone Count', 'Avg Traversal Time')

def test(directory=None):
    """Visualize makespan and avg traversal time for all .txt files in directory as bar charts."""
    if directory is None:
        directory = os.getcwd()
    files = glob.glob(os.path.join(directory, '*.txt'))
    ms = [(os.path.basename(f), makespanSingleFile(f)) for f in files if makespanSingleFile(f) is not None]
    tr = [(os.path.basename(f), traversalSingleFile(f)) for f in files if traversalSingleFile(f) is not None]
    barChart(ms, 'Makespan for Present Files', 'Makespan')
    barChart(tr, 'Avg Traversal Time for Present Files', 'Avg Traversal Time')

def main():
    root = './root'
    if not os.path.isdir(root):
        print(f"Warning: root folder '{root}' does not exist. Please update the path."); return
    strategies = ['centralized', 'decentralized']
    analyzeBothFixed(root, strategies)
    analyzeAngleFixed(root, strategies)
    analyzeCountFixed(root, strategies)

if __name__ == "__main__":
    test(r'F:\files\school\wwu\research\robotics\simulationSwarm\cluttered-navigation\plinko-drones\analytics\sampleOutput')
#    main()  # Uncomment to run full analysis
