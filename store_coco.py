import xml.etree.ElementTree as ET
from PIL import Image
import os
from datetime import datetime
import json
import uuid

# Path names as global variables:
directory = '/Volumes/Trout_Data/Elwha/annotations3/'
# directory = '/Users/Angelina/Desktop/annotations/'
clip_dir = '/Volumes/Trout_Data/Elwha/clips/'
# clip_dir = '/Users/Angelina/Desktop/clips/'
from absl import app
from absl import flags

flags.DEFINE_string(
	'annot_dir', '/Users/Angelina/Desktop/annotations/', 'Directory to output annotation files.'
)
flags.DEFINE_string(
    'clip_dir', '/Users/Angelina/Desktop/clips/', 'Directory that contains generated clips.'
)
FLAGS = flags.FLAGS


def getJSONFromData(annot_dir, clip_name):
	clip_path = os.path.join(annot_dir, clip_name)
	# Stop if no xml file found:
	if not os.path.exists(os.path.join(clip_path, 'output.xml')):
		return -1

	print(clip_name)
	info = {"clip_name": clip_name}
	categories = [{"id": 1, "name": "fish", "supercategory": "fish"}]
	clip_data = {"info": info, "images": [], "annotations":[], "categories": categories}

	tree = ET.parse(os.path.join(clip_path, 'output.xml'))
	root = tree.getroot()

	# Store info data:
	with open(os.path.join(clip_path, "info.txt")) as file:
		temp = file.read().splitlines()
	info['clip_name'] = temp[0]
	info['aris_name'] = temp[1]
	info['river_name'] = temp[2]
	info['state'] = temp[3]
	info['num_fish'] = int(temp[4])
	info['min_pixel_size'] = float(temp[5])
	info['sample_length'] = float(temp[6])
	info['pixel_meter_size'] = float(temp[7])
	info['clip_dim'] = [int(i) for i in temp[8].split()]
	info['fps'] = float(temp[9])
	info['frame_range'] = [int(i) for i in temp[10].split()]
	info['clip_date'] = temp[11]
	for child in root[:3]:
		if child.tag == 'url':
			info['url'] = child.text
		elif child.tag == 'date_created':
			info['date_created'] = datetime.strptime(child.text, '%m/%d/%Y')
		else:
			continue

	# Store images:
	clip_id = str(uuid.uuid4())
	images = []
	image_ids = {}
	i = 0
	j = 12
	print(len(os.listdir(os.path.join(clip_path, 'frames/'))))
	for i in range(len(os.listdir(os.path.join(clip_path, 'frames/')))):
		filename = str(i) + '.jpg'
		path = os.path.join(clip_path, 'frames', filename)
		image = {}
		image['id'] = temp[i+12]
		image_ids[i] = image['id']	# map image index (0-based) to image_id
		image['clip_id'] = clip_id
		im = Image.open(path)
		image['width'], image['height'] = im.size
		image['file_name'] = filename
		image['frame_num'] = int(image['id'].split('_')[0])
		image['num_fish'] = int(image['id'].split('_')[-1])
		image['date_captured'] = datetime.strptime(image['id'].split('_')[4] + image['id'].split('_')[5] + image['id'].split('_')[6]
								+image['id'].split('_')[7] + image['id'].split('_')[8] + image['id'].split('_')[9],
								"%Y%m%d%H%M%S")
		images.append(image)
	clip_data["images"] = images

	# Store annotations:
	annotations = []
	annot_id = 0
	track_id = 0
	for track_id, child in enumerate(root.findall('object')):
		for annot_id, polygon in enumerate(child.findall('polygon')):
			annotation = {}
			annotation['id'] = annot_id
			annotation['track_id'] = track_id
			annotation['image_id'] = image_ids[int(polygon.findall('t')[0].text)]
			annotation['category_id'] = 1
			points = [int(polygon.findall('pt/x')[0].text), int(polygon.findall('pt/y')[0].text),
					  int(polygon.findall('pt/x')[2].text), int(polygon.findall('pt/y')[1].text)]
			annotation['area'] = (points[2]-points[0]) * (points[3]-points[1])
			annotation['bbox'] = [points[0], points[1], points[2]-points[0], points[3]-points[1]] ##
			annotation['iscrowd'] = 0
			annotations.append(annotation)
	clip_data["annotations"] = annotations

	return clip_data

def main(argv):
	for file in os.listdir(FLAGS.clip_dir):
		data = getJSONFromData(FLAGS.clip_dir, file)
		if not data == -1:
			json.dump(data, open(os.path.join(FLAGS.annot_dir, file + '.json'), 'w'), default=str)

if __name__ == '__main__':
	app.run(main)
























