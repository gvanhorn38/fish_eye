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
	# frames = os.listdir('/Users/Angelina/Documents/clips/elwha_wa_2018_07_11_05_01_26_1/frames')
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
		if i < 180:
			continue

		f = frames[i]
		frame = cv2.imread(PATH_TO_FRAMES + '/' + f)    # Path to the specific frame
		
		# print(f)
		rects = []
		if f in ff_map:
			rects = bboxes[ff_map[f]]

		# Update centroid tracker using the set of bbox coordinates
		objects = ct.update(rects)
		
		# loop over the tracked objects
		for (objectID, centroid) in objects.items():
			# draw both the ID of the object and the centroid of the
			# object on the output frame
			text = "ID {}".format(objectID)
			cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
			cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

		# display counts in frame:
		counts = ct.getCounts()
		left = "Left: {}".format(counts['left'])
		right = "Right: {}".format(counts['right'])
		na = "NA: {}".format(counts['NA'])
		# print(left, right, na)
		cv2.putText(frame, left, (width-150, height-200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
		cv2.putText(frame, right, (width-150, height-150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
		cv2.putText(frame, na, (width-150, height-100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

		# update overall counts:
		l_count = counts['left']
		r_count = counts['right']
		na_count = counts['NA']

		# Show output frame
		# cv2.imshow('Frame', frame)
		# Add output frame to array
		img_array.append(frame)

		# input("Press Enter to continue..." + "\n")
		
		# # if the `q` key was pressed, break from the loop
		# key = cv2.waitKey(1) & 0xFF
		# if key == ord("q"):
		# 	break

	# Output total counts:
	print("Left: "+str(l_count)+" Right: "+str(r_count)+" NA: "+str(na_count))

	# Save frames to video
	clip_name = PATH_TO_FRAMES.split("/")[-1]
	out = cv2.VideoWriter('./test_clips/'+clip_name+'.mp4', cv2.VideoWriter_fourcc(*'MP4V'), extract_fps(PATH_TO_ANNOTATIONS), (width, height))
	for img in img_array:
		out.write(img)
	out.release()

if __name__ == '__main__':
  app.run(main)