import argparse, json, os

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('image_folder', type=str, help='directory containing clip folders')
	parser.add_argument('annotation_folder', type=str, help='directory containing json annotation files')
	parser.add_argument('--framedir_name', type=str, default='frames', help='name of folder containing frames (eg. frames, frames-bs)')
	parser.add_argument('--output_dest', type=str, default='./full.json', help='location of outputted combined json including filename')

	args = parser.parse_args()

	image_id_to_data = {}

	for file in os.listdir(args.annotation_folder):
		ext = os.path.splitext(file)[-1].lower()
		if ext == '.json':
			with open(os.path.join(args.annotation_folder, file)) as json_file:
				json_data = json.load(json_file)

				frame_width, frame_height = json_data['info']['clip_dim']

				for image in json_data['images']:
					data = {}
					data['filename'] = os.path.join(args.image_folder, os.path.splitext(file)[0], args.framedir_name, image['file_name'])
					data['id'] = image['id']
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
					data['object']['count'] = 0
					image_id_to_data[data['id']] = data

				for annotation in json_data['annotations']:
					data = image_id_to_data[annotation['image_id']]

					data['object']['count'] += 1

					data['object']['bbox']['xmin'].append(annotation['bbox'][0] / frame_width)
					data['object']['bbox']['xmax'].append((annotation['bbox'][0] + annotation['bbox'][2]) / frame_width)
					data['object']['bbox']['ymin'].append(annotation['bbox'][1] / frame_height)
					data['object']['bbox']['ymax'].append((annotation['bbox'][1] + annotation['bbox'][3]) / frame_height)
					data['object']['bbox']['label'].append(1)
	with open(args.output_dest , 'w') as output:
		json.dump(list(image_id_to_data.values()), output)

if __name__ == '__main__':
	main()
