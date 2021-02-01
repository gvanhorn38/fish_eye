from absl import app
from absl import flags
from colorsys import hls_to_rgb
import json
import numpy as np
import os
import xml.etree.ElementTree as ET

from fish_length import Fish_Length
from tracker import Tracker

flags.DEFINE_string(
	'json_dump_path', None, 'Path to json containing annotated clip info.'
)
flags.DEFINE_string(
	'xml_dir', None, 'Directory containing xml annotation files.'
)
flags.DEFINE_string(
	'output_path', None, 'Directory to output clip annotation jsons.'
)
flags.mark_flag_as_required('json_dump_path')
flags.mark_flag_as_required('xml_dir')
flags.mark_flag_as_required('output_path')
FLAGS = flags.FLAGS

def get_annotation_from_clip(clip):
	root = ET.parse(os.path.join(FLAGS.xml_dir, clip['clip_name']+'.xml')).getroot()

	data = {}
	data['clip_id'] = clip['clip_id']
	data['aris_filename'] = clip['aris_filename']
	data['start_frame'] = clip['start_frame']
	data['end_frame'] = clip['end_frame']
	data['upstream_direction'] = clip['upstream_direction']
	data['image_meter_width'] = clip['aris_info']['pixel_meter_size']*clip['aris_info']['xdim']

	# Create image entries
	frames = []
	for i in range(int(root.findall('object')[0].findtext('startFrame')), 1 + int(root.findall('object')[0].findtext('endFrame'))):
		frame = {
			'frame_num': clip['start_frame'] + i,
			'fish': []
		}
		frames.append(frame)

	fishes = []
	# Populate images with bboxes
	for track_id, object in enumerate(root.findall('object')):
		fish = {}
		fish['id'] = track_id
		fish['length'] = -1
		fish['direction'] = 'N/A'
		fish['start_frame_index'] = -1
		fish['end_frame_index'] = -1
		fish['color'] = Tracker.selectColor(track_id)

		fishes.append(fish)

		last_drawn = None
		stat_interp = []
		lengths = []
		for polygon in object.findall('polygon'):
			if int(polygon.findtext('pt/l')) == -1:
				continue
			
			index = int(polygon.find('t').text)

			frame = frames[index]
			
			frame_entry = {}
			frame_entry['fish_id'] = track_id
			frame_entry['bbox'] = None
			frame_entry['visible'] = 1
			frame_entry['human_labeled'] = int(polygon.findtext('pt/l'))

			frame['fish'].append(frame_entry)
			
			# Determine if polygon is stationary
			if polygon.findtext('s') is not None and int(polygon.findtext('s')):
				stat_interp.append(frame_entry)
			else:
				frame_entry['bbox'] = list(np.array([int(polygon.findtext('pt/x'))/clip['aris_info']['xdim'], int(polygon.findtext('pt/y'))/clip['aris_info']['ydim'],
					int(polygon.findall('pt/x')[2].text)/clip['aris_info']['xdim'], int(polygon.findall('pt/y')[1].text)/clip['aris_info']['ydim']]))
				
				# Coordinates of greater than 1.1 will cause training to fail
				if (np.array(frame_entry['bbox']) > 1.1).any():
					print('Error: Invalid bbox.')
					frame['fish'].pop()
					continue

				lengths.append(int(polygon.findall('pt/x')[2].text)-int(polygon.findtext('pt/x')))

				# Interpolate if there are stationary boxes
				if stat_interp:
					bbox_interp = last_drawn + np.dot(1 + np.array(range(len(stat_interp)))[:,np.newaxis], (np.array(frame_entry['bbox']) - np.array(last_drawn))[np.newaxis])/(len(stat_interp) + 1)
					for frame_entry, bbox in zip(stat_interp, bbox_interp):	
						frame_entry['bbox'] = list(bbox)
					stat_interp = []
				last_drawn = frame_entry['bbox']
			
			if fish['start_frame_index'] == -1:
				fish['start_frame_index'] = index
			fish['end_frame_index'] = index

		if stat_interp:
			for frame_entry in stat_interp:
				frame_entry['bbox'] = last_drawn

	data['frames'] = frames
	data['fish'] = fishes

	# Add track
	for fish in fishes:
		for frame_entry in frames[fish['start_frame_index']]['fish']:
			if frame_entry['fish_id'] == fish['id']:
				start_bbox = frame_entry['bbox']
				break
		else:
			raise RuntimeWarning(f'Start box of fish {fish["id"]} in {clip["clip_name"]} is not defined.')

		for frame_entry in frames[fish['end_frame_index']]['fish']:
			if frame_entry['fish_id'] == fish['id']:
				end_bbox = frame_entry['bbox']
				break
		else:
			raise RuntimeWarning(f'End box of fish {fish["id"]} in {clip["clip_name"]} is not defined.')

		fish['direction'] = Tracker.get_direction(start_bbox, end_bbox)

	return Fish_Length.add_lengths(data)

def main(argv):
	with open(FLAGS.json_dump_path) as json_file:
		json_dump = json.load(json_file)
	
	for clip in json_dump:
		data = get_annotation_from_clip(clip)

		with open(os.path.join(FLAGS.output_path, f'{clip["clip_name"]}.json'), 'w') as output_file:
			json.dump(data, output_file, indent=2)

if __name__ == '__main__':
	app.run(main)