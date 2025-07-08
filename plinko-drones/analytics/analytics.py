# Swarm Analytics

import scipy as sp
import matplotlib.pyplot as plt
import os
import numpy as np

def makespan():
	folder_path = './sampleOutput'  # Replace with your folder path
	results = []
	for filename in os.listdir(folder_path):
		if not filename.endswith('.txt'):
			continue
		droneCount = None
		min_time = float('inf')
		max_time = float('-inf')
		file_path = os.path.join(folder_path, filename)
		with open(file_path, 'r') as file:
			droneCount = int(file.readline().strip())
			for line in file:
				parts = line.strip().split(',')
				if len(parts) != 3:
					continue
				try:
					time_ms = float(parts[2])
					if time_ms < min_time:
						min_time = time_ms
					if time_ms > max_time:
						max_time = time_ms
				except ValueError:
					continue
		if min_time != float('inf') and max_time != float('-inf'):
			makespan = max_time - min_time
		else:
			makespan = None
		results.append((droneCount, makespan))
	return results

# def spacial():

def makespanStats():
    # Get makespan results
	results = makespan()
	# Filter out None makespans and convert droneCount to int
	# Filter out results with None makespans and convert droneCount to int
	filtered = [
		(int(drone_count), makespan)
		for drone_count, makespan in results
		if makespan is not None
	]
	if not filtered:
		print("No valid data to plot.")
		return

	drone_counts, makespans = zip(*filtered)

	# Scatter plot
	plt.scatter(drone_counts, makespans, label='Data Points')

	# Fit a curve (polynomial of degree 2 as example)
	coeffs = np.polyfit(drone_counts, makespans, deg=2)
	poly = np.poly1d(coeffs)
	x_fit = np.linspace(min(drone_counts), max(drone_counts), 100)
	y_fit = poly(x_fit)
	plt.plot(x_fit, y_fit, color='red', label='Best Fit Curve')

	plt.xlabel('Drone Count')
	plt.ylabel('Makespan')
	plt.title('Makespan vs Drone Count')
	plt.legend()
	plt.show()

# def spacialStats():

def main():
    makespanStats()
    spacialStates()
    