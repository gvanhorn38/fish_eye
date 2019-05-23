import os
import ctypes
import numpy as np
from numpy.ctypeslib import ndpointer
lib = np.ctypeslib.load_library("arisparse.so", os.path.dirname(".")) # added '.so'
get_video_stats = lib.get_video_stats
get_video_stats.restype = ctypes.c_int
get_video_stats.argtypes = [
	ctypes.c_char_p,
	ctypes.POINTER(ctypes.c_long),
	ctypes.POINTER(ctypes.c_long),
	ctypes.POINTER(ctypes.c_long)
]

get_frame_data = lib.get_frame_data
get_frame_data.restype = ctypes.c_int
get_frame_data.argtypes = [
	ctypes.c_char_p,
	ctypes.c_int,
	ndpointer(ctypes.c_ubyte, flags="C_CONTIGUOUS,WRITEABLE"),
	ctypes.POINTER(ctypes.c_uint32),
	ctypes.POINTER(ctypes.c_float),
	ctypes.POINTER(ctypes.c_uint32)
]

def load_beam_widths(fp="beam_widths/BeamWidths_ARIS1800_96.h", max_frames=1000):
	beam_widths = []
	index = -1
	with open(fp,'r') as f:
		for line in f:
			index += 1
			# print("INDEX:", index)
			if 'DEFINE_BEAMWIDTH3' in line:
				#  re.findall(r"[-]?\d+(?:\.\d+)?", "DEFINE_BEAMWIDTH3(0, -13.619, -13.740, -13.442)")
				pieces = line.strip().split("(")[1][:-1].split(",")
				beam_num = int(pieces[0])
				beam_center = float(pieces[1])
				beam_left = float(pieces[2])
				beam_right = float(pieces[3])

				beam_widths.append([beam_center, beam_left, beam_right])

	return beam_widths

def load_frames(aris_fp, frame_range=[], beam_width_fp="beam_widths/BeamWidths_ARIS1800_96.h"):

	if not os.path.exists(aris_fp):
		print(aris_fp)
		raise ValueError("Aris file path does not exist")

	if not os.path.exists(beam_width_fp):
		raise ValueError("Beam width file path does not exist")

	inputPath = ctypes.c_char_p(aris_fp.encode('utf-8')) # have to convert string to bytes first
	samples_per_beam = ctypes.c_long()
	num_beams = ctypes.c_long()
	num_frames = ctypes.c_long()
	success = get_video_stats(inputPath, ctypes.byref(samples_per_beam), ctypes.byref(num_beams), ctypes.byref(num_frames))

	samples_per_beam = samples_per_beam.value
	num_beams = num_beams.value
	num_frames = num_frames.value

	print("Aris Video Stats:")
	print("Samples per beam: %d" % (samples_per_beam,))
	print("Number of beams: %d" % (num_beams,))
	print("Number of frames: %d" % (num_frames,))

	all_frame_data = np.zeros([num_frames, samples_per_beam, num_beams], dtype=np.uint8)
	all_frame_params = []
	if len(frame_range) == 0:
		frame_range = range(min(num_frames - 1,1000))

	# Watch out for the last frame failing!
	print("NOTE: not processing last frame due to likely failure (need to investigate what the last frame is...)")
	for frame_index in frame_range:
	# for frame_index in range(min(num_frames - 1,500)):
		# print(frame_index)

		# We need to capture these for further processing
		sample_start_delay = ctypes.c_uint32()
		sound_speed = ctypes.c_float()
		sample_period = ctypes.c_uint32()
		# print("ALL FRAME DATA:", all_frame_data[frame_index])
		success = get_frame_data(inputPath, frame_index, all_frame_data[frame_index], ctypes.byref(sample_start_delay), ctypes.byref(sound_speed), ctypes.byref(sample_period))
		# print("AFTER:", all_frame_data[frame_index])

		if not success == 0:
			print("ERROR: failed at frame %d" % frame_index)
			break

		all_frame_params.append([sample_start_delay.value, sound_speed.value, sample_period.value])

	# Flip the frame data left to right
	all_frame_data = all_frame_data[:,:,::-1]


	################
	# Construct a meshgrid so that we can properly render the video

	sample_start_delay = sample_start_delay.value
	sound_speed = sound_speed.value
	sample_period = sample_period.value

	print("LOAD BEAM WIDTHS")
	# Load in the beam widths
	beam_width_data = load_beam_widths(beam_width_fp)

	# lets make the mesh grid
	WindowStart = sample_start_delay * 1e-6 * sound_speed / 2
	WindowLength = sample_period * samples_per_beam * 1e-6 * sound_speed / 2
	RangeStart  = WindowStart
	RangeEnd    = WindowStart + WindowLength
	SampleLength = sample_period *  1e-6 * sound_speed  / 2

	Y = np.zeros([samples_per_beam + 1, num_beams + 1]) # mesh grid Y values (bounds)
	X = np.zeros([samples_per_beam + 1, num_beams + 1]) # mesh grid X values (bounds)

	# 28 degree fan width
	theta = 2 * np.linspace(-14*(2*np.pi)/360,14*2*np.pi/360,num_beams)
	rangeToBinStart = np.linspace(RangeStart,RangeEnd,samples_per_beam)

	left_angles = np.array([bwd[1] for bwd in beam_width_data])[::-1] # we want left to right
	right_angles = np.array([bwd[2] for bwd in beam_width_data])[::-1]

	for r in range(samples_per_beam + 1):

		# Construct the point that we will be rotating
		idx = r # samples_per_beam - r
		SampleRange = WindowStart + sample_period * idx * 1e-6 * sound_speed  / 2
		vec = np.array([0, SampleRange])

		# add the first left
		theta = np.deg2rad(left_angles[0])
		rot_matrix = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
		rot_vec = np.matmul(rot_matrix, vec)

		Y[r,0] = rot_vec[1]
		X[r,0] = rot_vec[0]

		for c in range(num_beams):

			theta = np.deg2rad(right_angles[c])
			rot_matrix = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
			rot_vec = np.matmul(rot_matrix, vec)

			Y[r,c + 1] = rot_vec[1]
			X[r,c + 1] = rot_vec[0]

	return all_frame_data, X, Y