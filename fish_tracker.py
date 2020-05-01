from utils import extract_bboxes_pixels, map_frame_to_filename, extract_fps
from pyimagesearch.centroid_tracker import CentroidTracker
import argparse
import cv2
import os
import glob
import re
from PIL import Image
from absl import app, flags

flags.DEFINE_string(
	'path_to_frames', None, 'Path of the folder of frames')
flags.DEFINE_string(
	'path_to_annotations', None, 'Path to coco annotations json file')
FLAGS = flags.FLAGS


# Function to help sort frames in order by creation date
def numericalSort(value):
	numbers = re.compile(r'(\d+)')
	parts = numbers.split(value)
	parts[1::2] = map(int, parts[1::2])
	return parts

def main(argv):
	flags.mark_flag_as_required('path_to_frames')
	flags.mark_flag_as_required('path_to_annotations')

	PATH_TO_FRAMES = FLAGS.path_to_frames
	PATH_TO_ANNOTATIONS = FLAGS.path_to_annotations

	# Obtain the list of bounding boxes and a map from bbox id to image filename
	bboxes = {}
	width, height = extract_bboxes_pixels(bboxes, PATH_TO_ANNOTATIONS)
	ff_map = {}
	map_frame_to_filename(ff_map, PATH_TO_ANNOTATIONS)  # second argument is path to json file (coco format)

	# fetch frames from clip
	frames = os.listdir(PATH_TO_FRAMES)		# Path to directory containing clip frames
	frames = sorted(frames, key=numericalSort)
	i = -1

	# Initialize our centroid tracker and frame dimensions
	ct = CentroidTracker(width, height)

	# array to store all images
	img_array = []

	# Loop over each frame
	# while True:
	l_count, r_count, na_count = 0, 0, 0
	for j in range(len(frames)):
		i += 1
		f = frames[i]
		rects = []
		if f in ff_map:
			rects = bboxes[ff_map[f]]

		# Update centroid tracker using the set of bbox coordinates
		objects = ct.update(rects)

		# obtain counts in frame:
		counts = ct.getCounts()

		# update overall counts:
		l_count = counts['left']
		r_count = counts['right']
		na_count = counts['NA']

	# Output total counts:
	print("Left: "+str(l_count)+" Right: "+str(r_count)+" NA: "+str(na_count))

if __name__ == '__main__':
  app.run(main)