from absl import app
from absl import flags
import json
import os
from pathlib import Path

from pyimagesearch.centroid_tracker import CentroidTracker

flags.DEFINE_string(
    'path_to_json', None, 'Path to json or directory of jsons.'
)
flags.mark_flag_as_required('path_to_json')
FLAGS = flags.FLAGS

def main(argv):
	assert os.path.exists(FLAGS.path_to_json), f'{FLAGS.path_to_json_dir} does not exist.'

	# Is a single json
	if os.path.isfile(FLAGS.path_to_json):
		jsons = [FLAGS.path_to_json]
	# Is a directory containing jsons
	else:
		jsons = Path(FLAGS.path_to_json).glob('*.json')

	for json_file in jsons:
		with open(json_file) as file:
			frames = json.load(file)

		ct = CentroidTracker(1.0, 1.0)

		l_count, r_count, na_count = 0, 0, 0
		for i in range(len(frames)):
			rects = []
			for j in range(frames[i]['object']['count']):
				bbox = frames[i]['object']['bbox']
				rects.append([bbox['xmin'][j], bbox['ymin'][j], bbox['xmax'][j]-bbox['xmin'][j], bbox['ymax'][j]-bbox['ymin'][j]])

			# Update centroid tracker using the set of bbox coordinates
			ct.update(rects)

			# Obtain counts in frame:
			counts = ct.getCounts()

			l_count, r_count, na_count = counts['left'], counts['right'], counts['NA']

		print(f'{json_file}: Left: {l_count}, Right: {r_count}, N/A: {na_count}')

if __name__ == '__main__':
	app.run(main)