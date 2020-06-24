from absl import app
from absl import flags
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

flags.DEFINE_string(
	'frame_location', None, 'Directory containing frames 0.jpg-n.jpg.'
)
flags.DEFINE_list(
    'annotation_paths', None, 'List of comma-separated json files of annotations over given frames surrounded by quotes.'
)
flags.DEFINE_string(
	'save_path', None, 'Location to save annotated frames to.'
)
flags.DEFINE_bool(
	'auto', False, 'Auto-animated images.'
)
flags.DEFINE_bool(
	'no_display', False, 'Don\'t display images.'
)
flags.mark_flag_as_required('frame_location')
flags.mark_flag_as_required('annotation_paths')
FLAGS = flags.FLAGS

def main(argv):
	assert os.path.exists(FLAGS.frame_location), f'{FLAGS.frame_location} does not exist'

	max_num = 1
	total_annotations = {}
	for annotation_path in FLAGS.annotation_paths:
		with open(annotation_path) as json_file:
			for image in json.load(json_file):
				if image['filename'] in total_annotations:
					total_bbox = total_annotations[image['filename']]
					total_bbox['xmin'] += [n*image['width'] for n in image['object']['bbox']['xmin']]
					total_bbox['xmax'] += [n*image['width'] for n in image['object']['bbox']['xmax']]
					total_bbox['ymin'] += [n*image['height'] for n in image['object']['bbox']['ymin']]
					total_bbox['ymax'] += [n*image['height'] for n in image['object']['bbox']['ymax']]
					max_num = max(max_num, len(total_bbox['xmin']))
				else:
					image['object']['bbox']['xmin'] = [n*image['width'] for n in image['object']['bbox']['xmin']]
					image['object']['bbox']['xmax'] = [n*image['width'] for n in image['object']['bbox']['xmax']]
					image['object']['bbox']['ymin'] = [n*image['height'] for n in image['object']['bbox']['ymin']]
					image['object']['bbox']['ymax'] = [n*image['height'] for n in image['object']['bbox']['ymax']]
					total_annotations[image['filename']] = image['object']['bbox']

	index = 0
	file_names = list(total_annotations.keys())

	color = plt.cm.gist_ncar(np.linspace(0.2,1,max_num))

	# Stage image and annotations
	def draw_image_with_annotations(file_name):
		image_path = file_name
		if os.path.exists(image_path):
			ax.cla()
			ax.imshow(plt.imread(image_path))
			bbox = total_annotations[file_name]
			for i in range(len(bbox['xmin'])):
				# Draw rectangle
				rect = patches.Rectangle((bbox['xmin'][i],bbox['ymin'][i]),bbox['xmax'][i]-bbox['xmin'][i], bbox['ymax'][i]-bbox['ymin'][i],linewidth=1,edgecolor=color[i],facecolor='none')
				
				# Layer annotation onto picture
				ax.add_patch(rect)
		else:
			print(f'{image_path} does not exist.\n')

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
	if FLAGS.save_path is not None:
		for file_name in file_names:
			draw_image_with_annotations(file_name)

			# Save to directory
			plt.savefig(os.path.join(FLAGS.save_path, f'{os.path.splitext(os.path.basename(file_name))[0]}-annotated.jpg'), dpi=200)

	# Display images for viewing
	if not FLAGS.no_display:
		draw_image_with_annotations(file_names[index])
		if FLAGS.auto:
			while True:
				index += 1
				index %= len(file_names)
				draw_image_with_annotations(file_names[index])
				plt.show(block=False)
				plt.pause(0.1)
		else:
			plt.show()
	
if __name__ == '__main__':
	app.run(main)