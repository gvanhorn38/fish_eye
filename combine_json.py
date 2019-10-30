import argparse, json, os

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('image_folder', type=str, help='directory containing clip folders')
	parser.add_argument('annotation_folder', type=str, help='directory containing json annotation files')

	args = parser.parse_args()

	image_id_to_data = {}

	for file in os.listdir(args.annotation_folder):
		ext = os.path.splitext(file)[-1].lower()
		if ext == '.json':
			with open(os.path.join(args.annotation_folder, file)) as json_file:
				json_data = json.load(json_file)

				for image in json_data['images']:
					data = {}
					data['filename'] = os.path.join(args.image_folder, os.path.splitext(file)[0], 'frames/', image['file_name'])
					data['id'] = image['id']
					data['class'] = {}
					data['class']['label'] = 0
					data['class']['text'] = 'fish'
					data['object'] = {}
					data['object']['bbox'] = {}
					data['object']['bbox']['xmin'] = []
					data['object']['bbox']['xmax'] = []
					data['object']['bbox']['ymin'] = []
					data['object']['bbox']['ymax'] = []
					data['object']['bbox']['label'] = []
					image_id_to_data[data['id']] = data

				for annotation in json_data['annotations']:
					data = image_id_to_data[annotation['image_id']]

					data['class']['label'] += 1

					data['object']['bbox']['xmin'].append(annotation['bbox'][0])
					data['object']['bbox']['xmax'].append(annotation['bbox'][0] + annotation['bbox'][2])
					data['object']['bbox']['ymin'].append(annotation['bbox'][1])
					data['object']['bbox']['ymax'].append(annotation['bbox'][1] + annotation['bbox'][3])
					data['object']['bbox']['label'].append(annotation['track_id'])
	with open('./full.json' , 'w') as output:
		json.dump(list(image_id_to_data.values()), output)

if __name__ == '__main__':
	main()
