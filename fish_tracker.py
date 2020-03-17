from utils import extract_bboxes_pixels, map_frame_to_filename, extract_fps
from pyimagesearch.centroidtracker import CentroidTracker
import argparse
import cv2
import os
import glob
import re
from PIL import Image


# Function to help sort frames in order by creation date
numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

# constrct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--frames", required=True, help="path to folder of frames")
args = vars(ap.parse_args())

print(args['frames'])

# Obtain the list of bounding boxes and a map from bbox id to image filename
bboxes = {}
width, height = extract_bboxes_pixels(bboxes, args['frames']+".json")
ff_map = {}
map_frame_to_filename(ff_map, args['frames']+".json")

# fetch frames from clip
# frames = os.listdir('/Users/Angelina/Documents/clips/elwha_wa_2018_07_11_05_01_26_1/frames')
frames = os.listdir(args['frames'])		# Path to directory containing clip frames
frames = sorted(frames, key=numericalSort)
i = -1

# Initialize our centroid tracker and frame dimensions
ct = CentroidTracker(width, height)

# array to store all images
img_array = []

# Loop over each frame
while True:
	i += 1

	# only for testing! delete later >>>>>>>>>:
	if i < 200:
		continue
	# >>>>>>>>>>>>>

	f = frames[i]
	frame = cv2.imread(args['frames'] + '/' + f)    # Path to the specific frame
	
	print(f)
	rects = []
	if f in ff_map:
		rects = bboxes[ff_map[f]]
		print(rects)

	# Update centroid tracker using the set of bbox coordinates
	objects = ct.update(rects)
	
	# loop over the tracked objects
	for (objectID, centroid) in objects.items():
		print(objectID, centroid)
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
	cv2.putText(frame, left, (width-150, height-200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
	cv2.putText(frame, right, (width-150, height-150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
	cv2.putText(frame, na, (width-150, height-100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

	# Show output frame
	cv2.imshow('Frame', frame)
	# Add output frame to array
	img_array.append(frame)

	input("Press Enter to continue..." + "\n")
	
	# if the `q` key was pressed, break from the loop
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break

# Save frames to video
out = cv2.VideoWriter('test.mp4', cv2.VideoWriter_fourcc(*'DIVX'), extract_fps(args['frames']+".json"), (width, height))
for img in img_array:
	out.write(img)
out.release()


