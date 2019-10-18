import argparse, json, os, sys
import random

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

import numpy as np

# Annotation colors
colors = ('r', 'b', 'g', 'c', 'm', 'y', 'k', 'w')

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('frames', type=str, help='directory containing image frames labeled beginning at 0')
	parser.add_argument('annotations', type=str, nargs='+', help='json files or directories with json files that contain annotations over the given frames')
	parser.add_argument('-s', '--save', type=str, help='save patched images to folder')
	parser.add_argument('-a', '--auto', type=float, help='auto animate images at provided sleep between frames')
	parser.add_argument('-n', '--nodisplay', help='don\'t display anything', action='store_true')
	parser.add_argument('--demo', help='add noise to annotations', action='store_true')

	args = parser.parse_args()

	assert os.path.exists(args.frames), '%s does not exist' % args.frames
	assert args.save is None or os.path.exists(args.save), '%s does not exist' % args.save
	assert args.auto is None or args.auto > 0, 'auto must be positive'

	files = []

	# Parse json args
	for arg in args.annotations:
		if not os.path.exists(arg):
			sys.stderr.write(arg + ' does not exist.\n')
		# If arg is a directory
		elif os.path.isdir(arg):
			for file in os.listdir(arg):
				ext = os.path.splitext(file)[-1].lower()
				if ext == '.json':
					files.append(os.path.join(arg, file))
		# Is a json file
		else:
			files.append(arg)

	total_annotations = {}
	image_id_to_file_name = {}
	# Collect annotations from json files, but don't draw
	for i, file in enumerate(files):
		with open(file) as json_file:
			json_data = json.load(json_file)
			for annotation in json_data['annotations']:
				# The annotations in the json only have an image_id, not
				# the filename of the image, so in order to find the
				# matching frames we search for the image that contains
				# the matching id tag in the json and take it's file_name
				# attribute.
				image_id = annotation['image_id']
				file_name = ''
				if image_id in total_annotations:
					file_name = total_annotations[image_id]
				else:
					for image in json_data['images']:
						if image['id'] == image_id:
							file_name = image['file_name']
							image_id_to_file_name[image_id] = file_name
							break
							# Possibly faster to only look up the first one and
							# then add one each time to get the file name since
							# annotations in a file should be in order?

				bbox = annotation['bbox']

				if file_name in total_annotations:
					total_annotations[file_name][i] = bbox
				else:
					total_annotations[file_name] = {i : bbox}

	index = 0
	file_names = list(total_annotations.keys())

	# Stage image and annotations
	def draw_image_with_annotations(file_name):
		image_path = os.path.join(args.frames, file_names[index])
		if os.path.exists(image_path):
			ax.cla()
			ax.imshow(np.array(Image.open(image_path)))
			for i, bbox in total_annotations[file_name].items():
				# Draw rectangle
				if not args.demo:
					rect = patches.Rectangle(bbox[:2],bbox[2],bbox[3],linewidth=1,edgecolor=colors[i],facecolor='none')
				else:
					rect = patches.Rectangle((bbox[0]+random.randint(-5,5),bbox[1]+bbox[3]+random.randint(-5,5)),bbox[2]+random.randint(-5,5),bbox[3]+random.randint(-5,5),linewidth=1,edgecolor=colors[i],facecolor='none')

				# Draw debug bbox text
				#plt.text(5, 20, str(bbox), fontsize=14, bbox=dict(facecolor='red', alpha=0.5))

				# Layer annotation onto picture
				ax.add_patch(rect)
		else:
			sys.stderr.write(image_path + 'does not exist.\n')

	def key_event(e):
	    nonlocal index, file_names

	    if e.key == 'right':
	    	index += 1
	    elif e.key == 'left':
	    	index -= 1
	    elif e.key == 'q':
	    	exit()
	    else:
	    	return
	    index %= len(file_names)
	    draw_image_with_annotations(file_names[index])
	    fig.canvas.draw()

	fig = plt.figure()
	fig.canvas.mpl_connect('key_press_event', key_event)
	ax = fig.add_subplot(111)

	# Save images
	if args.save is not None:
		for file_name, annotations in total_annotations.items():
			draw_image_with_annotations(file_name)

			# Save to CWD
			plt.savefig(os.path.join(args.save, file_name + '.annotated.jpg'))

	# Display images for viewing
	if not args.nodisplay:
		draw_image_with_annotations(file_names[index])
		if args.auto is not None:
			while True:
				index += 1
				index %= len(file_names)
				draw_image_with_annotations(file_names[index])
				plt.show(block=False)
				plt.pause(args.auto)
		else:
			plt.show()

if __name__ == '__main__':
	main()
