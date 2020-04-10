import argparse, json, os, sys
import random

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

import numpy as np


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('annotations', type=str, nargs='+', help='json files or directories with json files that contain annotations over the given frames')
	# parser.add_argument('-s', '--save', type=str, help='save counts')

	args = parser.parse_args()

	# assert args.save is None or os.path.exists(args.save), '%s does not exist' % args.save

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

	for file in files:
		with open(file) as json_file:
			json_data = json.load(json_file)

			width, _ = json_data['info']['clip_dim']

			start_id = json_data['images'][0]['id']
			end_id = json_data['images'][-1]['id']

			tracks = {}

			for annotation in json_data['annotations']:
				tracks.setdefault(annotation['track_id'],[]).append(annotation)

			print(file)
			for annotation_id, annotations in tracks.items():
				print(str(annotation_id) + ':')
				start = 'middle'
				if annotations[0]['image_id'] != start_id:
					if annotations[0]['bbox'][0] + (annotations[0]['bbox'][2] / 2) < width/2:
						start = 'left'
					else:
						start = 'right'
				
				end = 'middle'
				if annotations[-1]['image_id'] != end_id:
					if annotations[-1]['bbox'][0] + (annotations[-1]['bbox'][2] / 2) < width/2:
						end = 'left'
					else:
						end = 'right'

				print(start, 'to', end)

if __name__ == '__main__':
	main()
