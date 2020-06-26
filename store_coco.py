from absl import app
from absl import flags
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import xml.etree.ElementTree as ET

flags.DEFINE_string(
	'output_path', None, 'Directory to output annotation jsons or path to output combined json.'
)
flags.DEFINE_string(
    'clip_dir', None, 'Directory that contains generated clips.'
)
flags.DEFINE_string(
	'xml_dir', None, 'Location of XML annotations (default is nested in clips).'
)
flags.DEFINE_string(
	'framedir_name', 'frames', 'Name of nested frames directory if xml_dir is None.'
)
flags.mark_flag_as_required('output_path')
flags.mark_flag_as_required('clip_dir')
FLAGS = flags.FLAGS


def get_json_from_data(xml, framedir):
	root = ET.parse(xml).getroot()

	image = plt.imread(os.path.join(framedir, '0.jpg'))
	height = image.shape[0]
	width = image.shape[1]

	# Create image entries
	images = {}
	for i in range(int(root.findall('object')[0].findtext('startFrame')), 1 + int(root.findall('object')[0].findtext('endFrame'))):
		data = {}
		data['filename'] = os.path.join(framedir, f'{i}.jpg')
		data['id'] = data['filename']
		data['height'] = height
		data['width'] = width
		data['class'] = {}
		data['class']['label'] = 1
		data['class']['text'] = 'fish'
		data['object'] = {}
		data['object']['bbox'] = {}
		data['object']['bbox']['xmin'] = []
		data['object']['bbox']['xmax'] = []
		data['object']['bbox']['ymin'] = []
		data['object']['bbox']['ymax'] = []
		data['object']['bbox']['label'] = []
		data['object']['bbox']['track_id'] = []
		data['object']['count'] = 0
		
		images[i] = data
	
	# Populate images with bboxes
	for track_id, fish in enumerate(root.findall('object')):
		last_drawn = None
		stat_interp = []
		for polygon in fish.findall('polygon'):
			if int(polygon.findtext('pt/l')) == -1:
				continue
			image = images[int(polygon.find('t').text)]

			image['object']['count'] += 1
			bbox = image['object']['bbox']
			bbox['label'].append(1)
			bbox['track_id'].append(track_id)

			# Determine if polygon is stationary
			if int(polygon.findtext('s')):
				stat_interp.append(bbox)
			else:
				points = np.array([int(polygon.findtext('pt/x'))/image['width'], int(polygon.findtext('pt/y'))/image['height'],
					int(polygon.findall('pt/x')[2].text)/image['width'], int(polygon.findall('pt/y')[1].text)/image['height']])

				bbox['xmin'].append(points[0])
				bbox['ymin'].append(points[1])
				bbox['xmax'].append(points[2])
				bbox['ymax'].append(points[3])
				
				# Interpolate if there are stationary boxes
				if stat_interp:
					bbox_interp = last_drawn + np.dot(1 + np.array(range(len(stat_interp)))[:,np.newaxis], (points - last_drawn)[np.newaxis,:])/(len(stat_interp) + 1)
					for object_bbox, bbox in zip(stat_interp, bbox_interp):
						object_bbox['xmin'].append(bbox[0])
						object_bbox['ymin'].append(bbox[1])
						object_bbox['xmax'].append(bbox[2])
						object_bbox['ymax'].append(bbox[3])
					stat_interp = []
				last_drawn = points
					
	return list(images.values())

def main(argv):
	# If output_path is a directory, output json for each clip else combine
	combine = False
	if not os.path.isdir(FLAGS.output_path):
		combine = True
		total = []

	if FLAGS.xml_dir:
		for file in os.listdir(FLAGS.xml_dir):
			name = os.path.splitext(file)
			if name[1] == '.xml':
				data = get_json_from_data(os.path.join(FLAGS.xml_dir, file), os.path.join(FLAGS.clip_dir, name[0], FLAGS.framedir_name))
				if combine:
					total += data
				else:
					json.dump(data, open(os.path.join(FLAGS.output_path, f'{name[0]}.json'), 'w'), default=str, indent=2)
	else:
		for file in os.listdir(FLAGS.clip_dir):
			data = get_json_from_data(os.path.join(FLAGS.clip_dir, file, 'output.xml'), os.path.join(FLAGS.clip_dir, file, FLAGS.framedir_name))
			if combine:
				total += data
			else:
				json.dump(data, open(os.path.join(FLAGS.output_path, f'{file}.json'), 'w'), default=str, indent=2)

	if combine:
		json.dump(total, open(FLAGS.output_path, 'w'), default=str, indent=2)
	
if __name__ == '__main__':
	app.run(main)