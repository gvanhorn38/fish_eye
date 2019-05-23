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
from matplotlib import cm
from scipy import interpolate
from numpy.ctypeslib import ndpointer
from datetime import datetime, timedelta
from IPython.display import HTML

import load_aris


# Path names as global variables (rename depending on user):
csv_fp = "../raw_data_washington.csv"	# path to csv annotations file
json_fp = "washington.json"		# path where we want to store JSON file
beam_width_fp = "beam_widths/BeamWidths_ARIS1800_96.h"	# beamwidths file path
aris_dir = "aris_samples/Washington/"	# path to directory containing ARIS data


def store_data(annot_fp, json_fp):
	"""
	Takes an excel file containing human annotations for the ARIS files on the
	hard drive, processes the data, and stores it as a JSON object.

	Arguments:
		annot_fp: Filepath to the annotations file in CSV format.
		json_fp: Filepath where we want to store the JSON file.
	"""
	# print("1: store_data()")

	# Process Data:
	with open(annot_fp) as csvfile:
		readCSV = csv.reader(csvfile, delimiter=',')
		data = []
		for row in readCSV:
			data.append(row[:12])
		data[0][0] = 'Date'
		for row in data[1:]:
			if len(row[1]) != 0:
				if len(row[1]) != 5:
					row[1] = '0' + row[1]
				row[1] = row[1] + ':00'
			for i in [2,4,5,6,7,9]:
				if row[i].strip() != '':
					row[i] = float(row[i])
				else:
					row[i] = float('nan')

	# Store into nested dictionary:
	washington = {}
	frames_wash = {}
	washington['info'] = ''
	washington['annotations'] = frames_wash
	id = 0

	# First row of data:
	frame = {}
	frame['id'] = id
	if data[1][1] == '':
	    frame['num_fish'] = 0
	else:
	    frame['num_fish'] = 1
	for i in range(len(data[0])):
	    frame[data[0][i]] = data[1][i]
	frames_wash[int(frame['id'])] = frame
	id += 1
	curr_time = data[1][1] # current_time

	# Process rest of data
	for row in data[2:]:
	    if row[1] != '' and row[1] == curr_time:
	        frames_wash[id-1]['num_fish'] += 1
	        continue
	    frame = {}
	    frame['id'] = id
	    curr_time = row[1]
	    if curr_time == '':
	        frame['num_fish'] = 0
	    else:
	        frame['num_fish'] = 1
	    for i in range(len(data[0])):
	        frame[data[0][i]] = row[i]
	    frames_wash[int(frame['id'])] = frame
	    id += 1

	# Store as JSON file:
	print("JSON file stored:", json_fp)
	json.dump(washington, open(json_fp, 'w'))


def get_annotations(json_fp, data):
	"""
	Retrieves all annotations as DATETIME objects from a JSON file.

	Arguments:
		json_fp: Filepath where JSON annotations file is stored.

	Returns:
		spottings: List of all annotations (in order) as DATETIME objects.
	"""
	# print("2: get_annotations()")

	# # Retrieve from JSON file:
	# data = json.load(open(json_fp,'r'))

	# For each annotation in raw_data, get DATETIME:
	annotations = data['annotations']
	spottings = []
	for key, value in annotations.items():
		if value['Date'] != '' and value['Time'] != '':
			time = datetime.strptime(value['Date'] + ' ' + value['Time'],
									'%Y-%m-%d %H:%M:%S')
			spottings.append([key, time])
	return spottings

def get_datetime(index, fm_index, data):
	# print("3: get_datetime()")

	spotting_dates = get_annotations(json_fp, data) # holds the DATETIME of each annotation
	delta, filename = get_frame_time(index, spotting_dates)

	aris_fp = aris_dir + filename
	lib = np.ctypeslib.load_library("arisparse.so", os.path.dirname(".")) # added '.so'
	get_ft = lib.get_ft
	inputPath = ctypes.c_char_p(aris_fp.encode('utf-8')) # have to convert string to bytes first
	frame_time = ctypes.c_uint64()
	get_ft(inputPath, ctypes.c_int(fm_index), ctypes.byref(frame_time))
	frame_time = frame_time.value

	start = datetime(1970, 1, 1) # FrameTime reference
	dt = start + timedelta(microseconds=frame_time)
	dt = dt.strftime('%Y-%m-%d %H:%M:%S')
	return str(dt), frame_time
	

def get_frame_time(index, spottings, 
				path_name=aris_dir[:-1]):
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
	# print("4: get_frame_time()")

	# Convert aris filenames to DATETIME objects so we can compare them.
	names = listdir(path_name)
	names.sort()
	names = names[1:]
	dts = []
	for n in names:
		dt = datetime.strptime(n[:17], '%Y-%m-%d_%H%M%S') # dataset specific
		dts.append(dt)

	start = datetime(1970, 1, 1) # FrameTime reference
	end = spottings[index][1]
	end = end + timedelta(seconds=30) # Get middle of minute mark since we don't have seconds.
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
	return delta, filename


def get_frames(index, N, json_fp, aris_dir, annot_fp, data):
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
	# print("5: get_frames()")

	spotting_dates = get_annotations(json_fp, data) # holds the DATETIME of each annotation
	frame_time, filename = get_frame_time(index, spotting_dates)
	
	aris_fp = aris_dir + filename
	lib = np.ctypeslib.load_library("arisparse.so", os.path.dirname(".")) # added '.so'
	get_frame_index = lib.get_frame_index
	inputPath = ctypes.c_char_p(aris_fp.encode('utf-8')) # have to convert string to bytes first
	delta = ctypes.c_uint64(int(frame_time))
	num_frames = ctypes.c_long()
	frame_index = get_frame_index(inputPath, delta, ctypes.byref(num_frames))

	if frame_index == -7:
		return []
	else:
		min_i, max_i = frame_index-N, frame_index+N
		if min_i < 0:
			min_i = 0
		if max_i >= num_frames.value:
			max_i = num_frames.value - 1
		# return range(5680, 5750)
		# return range(5704, 5708)
		# return range(min_i, max_i+1)
		# return range(699, 749)
		return range(720, 730)


def gen_gif(index, json_fp, csv_fp):
	"""
	Generates a GIF for the recorded observation.

	Arguments:
		index: The id (0-based index) that identifies the recorded observation
			   (int).
		N: The window (+/- N frames) around the frame of observation (int).
	"""
	# print("7: gen_gif()\n")

	# Stores csv data in JSON file if not done so already.
	if not os.path.isfile(json_fp):
		# Stores csv file into json object
		store_data(csv_fp, json_fp)

	# Retrieve from JSON file:
	data = json.load(open(json_fp,'r'))

	spottings = get_annotations(json_fp, data)

	# aris_dir = 'aris_samples/Washington/'
	
	# Specify a path to an aris data file
	filename = get_frame_time(index, spottings)[1]
	aris_fp = aris_dir + filename 	# filename is an ARIS filename
	# beam_width_fp = "beam_widths/BeamWidths_ARIS1800_96.h" # Assumes you are in the project directory

	# Get frame rate of ARIS file:
	lib = np.ctypeslib.load_library("arisparse.so", os.path.dirname(".")) # added '.so'
	get_frame_rate = lib.get_frame_rate
	inputPath = ctypes.c_char_p(aris_fp.encode('utf-8')) # have to convert string to bytes first
	frame_rate = ctypes.c_float()
	get_frame_rate(inputPath, ctypes.byref(frame_rate))
	frame_rate = frame_rate.value
	print("frame_rate:", frame_rate)
	N = math.ceil(30*frame_rate)  # Gets number of frames per 30 seconds as window.

	frame_range = get_frames(index, N, json_fp, aris_dir, csv_fp, data)
	if len(frame_range) == 0:
		return
	print(frame_range)

	frame_data, meshgrid_X, meshgrid_Y = load_aris.load_frames(aris_fp=aris_fp, frame_range=frame_range, beam_width_fp=beam_width_fp)
	num_frames = frame_data.shape[0]

	annotations = data['annotations']
	num_fish = annotations[spottings[index][0]]['num_fish']
	# Create clip directory:
	print(filename)
	date = datetime.strptime(filename[:17], '%Y-%m-%d_%H%M%S') # dataset specific
	clip_dir = 'elwha_wa_' + spottings[index][1].strftime('%d_%m_%Y_%H_%M_%S_') + str(num_fish)
	if os.path.isdir(clip_dir):
		print("Error!", clip_dir, " is an existing directory.")
		return -1
	os.mkdir(clip_dir)
	os.mkdir(clip_dir + '/frames')	# create frame directory within clip directory
	
	direc = annotations[spottings[index][0]]['Direction']

	print("Start:")
	f = interpolate.interp1d([0, 255], [0, 80])
	for i in frame_range:
		print(i)
		fig = plt.figure(figsize=(12,20))
		dt, frame_time = get_datetime(index, i, data)
		plt.pcolormesh(meshgrid_X, meshgrid_Y, f(frame_data[i]), cmap=cm.YlGnBu_r, vmin=0, vmax=80)
		plt.title("Frame: %d\nDatetime: %r\nDirection: %r" % (i, dt, direc))
		plt.ylabel("Meters")
		plt.xlabel("Meters")
		cbar = plt.colorbar()
		cbar.ax.set_ylabel('dB')
		fig_path = clip_dir + '/frames/'

		# Saves frame:
		date = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
		plt.savefig('{}/frames/{}_{}_elwha_wa_{}.jpeg'.format(clip_dir, i, frame_time, date.strftime('%d_%m_%Y_%H_%M_%S')))
		plt.close(fig)

	np.savez(clip_dir + '/' + clip_dir, frame_data, meshgrid_X, meshgrid_Y)  # save numpy file

	vid_name = clip_dir + '/' + clip_dir + '.mp4'
	cmmd_line = "ffmpeg -framerate " + str(frame_rate) + " -pattern_type glob -i '" + clip_dir + "/frames/*.jpeg' " + "-c:v libx264 -r 30 -pix_fmt yuv420p " + vid_name
	os.system(cmmd_line)
	# os.system("ffmpeg -framerate 7.5 -pattern_type glob -i 'testing2/*.jpeg' -c:v libx264 -r 30 -pix_fmt yuv420p testing2.mp4")
	print("datetime:", spottings[index])



# gen_gif(1, json_fp='washington.json', csv_fp='../raw_data_washington.csv')

# gen_gif(2, json_fp='washington.json', csv_fp='../raw_data_washington.csv')
# gen_gif(3, json_fp='washington.json', csv_fp='../raw_data_washington.csv')
# gen_gif(4, json_fp='washington.json', csv_fp='../raw_data_washington.csv')
# gen_gif(5, json_fp='washington.json', csv_fp='../raw_data_washington.csv')
gen_gif(7, json_fp, csv_fp)





