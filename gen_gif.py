import os
import json
import csv
import math
import ctypes
import matplotlib
import imageio
import numpy as np
from os import listdir
from matplotlib import pyplot as plt
from scipy import interpolate
from numpy.ctypeslib import ndpointer
from datetime import datetime, timedelta
from IPython.display import HTML

import load_aris


def store_data(annot_fp, json_fp):
	"""
	Takes an excel file containing human annotations for the ARIS files on the
	hard drive, processes the data, and stores it as a JSON object.

	Arguments:
		annot_fp: Filepath to the annotations file in CSV format.
		json_fp: Filepath where we want to store the JSON file.
	"""
	
	# Process Data:
	with open(annot_fp) as csvfile:
		readCSV = csv.reader(csvfile, delimiter=',')
		data = []
		for row in readCSV:
			data.append(row[:8])
		data[0][0] = 'Date'
		data[0][4] = 'Confidence'
		data[0][5] = 'Length'
		data[0][6] = 'Temp'
		data[0][7] = 'Mins'
		for row in data[1:]:
			for i in range(3, 8):
				if row[i].strip() != '':
					row[i] = float(row[i])
				else:
					row[i] = float('nan')

	# Store into nested dictionary:
	data = {}
	frames = {}
	data['info'] = ''
	data['annotations'] = frames
	id = 0
	for row in data[1:]:
		frame = {}
		frame['id'] = id
		for i in range(len(data[0])):
			frame[data[0][i]] = row[i]
		frames[int(frame['id'])] = frame
		id += 1

	# Store as JSON file:
	json.dump(data, open(json_fp, 'w'))


def get_annotations(json_fp):
	"""
	Retrieves all annotations as DATETIME objects from a JSON file.

	Arguments:
		json_fp: Filepath where JSON annotations file is stored.

	Returns:
		spottings: List of all annotations (in order) as DATETIME objects.
	"""

	# Retrieve from JSON file:
	data = json.load(open(json_fp,'r'))

	# For each annotation in raw_data, get DATETIME:
	annotations = data['annotations']
	spottings = []
	for key, value in annotations.items():
		if value['Date'] != '' and value['Time'] != '':
			time = datetime.strptime(value['Date'] + ' ' + value['Time'],
									'%Y-%m-%d %H:%M:%S')
			spottings.append(time)
	return spottings


def get_frame_time(index, spottings, 
				path_name='aris_samples'):
	"""
	Calculates the FrameTime (PC time stamp when recorded, in microseconds since
	01/01/1970, as described by the ARIS documentation) of the annotation and
	gives the file name of the ARIS file that contains the recorded 
	observation.

	Arguments:
		index: The id (0-based index) that identifies the recorded observation.
		spottings: List of each observation/annotation as DATETIME objects.
		path_name: Path to directory storing all ARIS files.

	Returns:
		delta: The FrameTime (ie timestamp of recorded observation) in 
			   microseconds (float).
		filename: The filename of the ARIS file most likely containing the
				  recorded observation (string).

	"""

	# Convert aris filenames to DATETIME objects so we can compare them.
	names = listdir(path_name)
	names.sort()
	dts = []
	for n in names:
		dt = datetime.strptime(n[5:22], '%Y-%m-%d_%H%M%S') # dataset specific
		dts.append(dt)

	start = datetime(1970, 1, 1) # FrameTime reference
	end = spottings[index] # just testing
	this_dt = dts[0]
	filename = ''
	for dt in dts:
		if dt <= end:
			this_dt = dt
		else:
			break
	for name in names:
		if this_dt.strftime('%Y-%m-%d_%H%M%S') in name: # specific to this dataset
			filename = name
	delta = (end - start).total_seconds() * (1e6)
	print("FILENAME:", filename)
	return delta, filename


def get_frames(index, N, json_fp, aris_dir, annot_fp):
	"""
	Returns the range of frames that surround the recorded observation.

	Arguments:
		index: The id (0-based index) that identifies the recorded observation
		       (int).
		N: The window (+/- N frames) around the frame of observation (int).
		json_fp: Filepath of the JSON file (string).
		aris_dir: Path of the directory storing the ARIS files (string).
		annot_fp: Filepath to the annotations file in CSV format.
	
	Returns:
		range(min_i, max_i+1): A list of frames that will make up our GIF that
		                       visualizes the observation.
	"""
	
	# Stores csv file into json object
	store_data(annot_fp, json_fp)

	spotting_dates = get_annotations(json_fp) # holds the DATETIME of each annotation
	frame_time, filename = get_frame_time(index, spotting_dates)
	
	aris_fp = aris_dir + filename
	lib = np.ctypeslib.load_library("arisparse.so", os.path.dirname(".")) # added '.so'
	get_frame_index = lib.get_frame_index
	inputPath = ctypes.c_char_p(aris_fp.encode('utf-8')) # have to convert string to bytes first
	delta = ctypes.c_uint64(int(frame_time))
	num_frames = ctypes.c_long()
	index = get_frame_index(inputPath, delta, ctypes.byref(num_frames))
	
	print("NUM_FRAMES:", num_frames.value)

	if index == -7:
		return []
	else:
		min_i, max_i = index-N, index+N
		if min_i < 0:
			min_i = 0
		if max_i >= num_frames.value:
			max_i = num_frames.value - 1
		return range(min_i, max_i+1)


def gen_image(index, frame_data, meshgrid_X, meshgrid_Y):
	"""
	Generates image for the frame labelled by 'index'.

	Arguments:
		index: Index of the frame in the ARIS file, 1-based (int).
		frame_data: List containing data for each frame in ARIS file.
		meshgrid_X: List of mesh grid X values.
		meshgrid_Y: List of mesh grid Y values.

	Returns:
		image: Image for the inidividual frame.
	"""

	f = interpolate.interp1d([0, 255], [0, 80])
	fig, ax = plt.subplots(figsize=(10,5))
	im = ax.pcolormesh(meshgrid_X, meshgrid_Y, f(frame_data[index]), vmin=0, vmax=80)
	ax.set_title("Frame: %d" % index)
	ax.set(xlabel='Meters', ylabel='Meters')
	cbar = fig.colorbar(im, ax=ax)
	cbar.ax.set_ylabel('dB')
	
	fig.canvas.draw()
	image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
	# print(fig.canvas.get_width_height()[::-1])
	# print(image.shape)
	image = image.reshape(1000, 2000, 3)

	return image


def gen_gif(index, N, json_fp, csv_fp, gif_name):
	"""
	Generates a GIF for the recorded observation.

	Arguments:
		index: Index of the frame in the ARIS file, 1-based (int).
		N: The window (+/- N frames) around the frame of observation (int).
	"""
	spottings = get_annotations(json_fp)

	aris_dir = 'aris_samples/'

	frame_range = get_frames(index, N, json_fp, aris_dir, csv_fp)
	if len(frame_range) == 0:
		return
	print(frame_range)

	# Specify a path to an aris data file
	aris_fp = aris_dir + get_frame_time(index, spottings)[1]
	beam_width_fp = "beam_widths/BeamWidths_ARIS1800_96.h" # Assumes you are in the project directory

	frame_data, meshgrid_X, meshgrid_Y = load_aris.load_frames(aris_fp=aris_fp, frame_range=frame_range, beam_width_fp=beam_width_fp)
	num_frames = frame_data.shape[0]

	gif_fp = 'GIFs/' + gif_name + str(index) + '.gif'
	imageio.mimsave(gif_fp, [gen_image(i, frame_data, meshgrid_X, meshgrid_Y) for i in frame_range], fps=4.2)
	print("datetime:", spottings[index])


# Generate example GIF for window of +/- 20 frames around the 6th recorded observation in 'raw_data_steelhead.csv'.
gen_gif(6, 20, json_fp='oregon.json', csv_fp='../raw_data_steelhead.csv', gif_name='oregon_')
# for i in range(25):
# 	print("INDEX ", i)
# 	gen_gif(i, 20, json_fp='oregon.json', csv_fp='../raw_data_steelhead.csv', gif_name='oregon_')
# 	print("\n")




