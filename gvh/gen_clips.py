from absl import app
from absl import flags
from datetime import datetime
import json
import numpy as np
import os
from pathlib import Path
import re
from shutil import make_archive

import pyARIS

flags.DEFINE_string(
	'aris_dir', None, 'Path to source ARIS files.'
)
flags.DEFINE_string(
    'clip_dir', None, 'Directory to output generated clips.'
)
flags.DEFINE_string(
	'river_name', 'elwha', 'River name and location (eg. kenai or elwha).'
)
flags.DEFINE_string(
	'river_location', 'wa', 'State that the river is located in (eg. wa).'
)
flags.DEFINE_string(
	'zip_location', None, 'Location to zip frames directories to for annotating.\n'
	                    + 'Will zip warped-to-scale images regardless of save_raw.'
)
flags.DEFINE_bool(
	'no_infotxt', False, 'Omit info.txt in clip creation.'
)
flags.DEFINE_bool(
	'save_raw', False, 'Additionally save un-warped images.'
)
flags.DEFINE_bool(
	'verbose', False, 'Adds extra debugging information.'
)
flags.DEFINE_bool(
	'save_remap_info', False, 'Stores mapping between non-warped and warped image.'
)
flags.mark_flag_as_required('aris_dir')
flags.mark_flag_as_required('clip_dir')
FLAGS = flags.FLAGS

# Parser for elwha and kenai formatted annotations text file
def parse_data(annot_fp, validate=False):
	with open(annot_fp) as file:
		contents = file.read()

	RE1 = re.compile( r'Total Fish\s+=[ ]+([0-9]+)\n'
					+ r'Upstream\s+=[ ]+([0-9]+)\n'
					+ r'Downstream\s+=[ ]+([0-9]+)\n'
					+ r'\?\?\s+=[ ]+([0-9]+)\n'
					+ r'\n'
					+ r'Total Frames\s+=[ ]+([0-9]+)\n'
					+ r'Expected Frames\s+=[ ]+([0-9]+)\n'
					+ r'Total Time\s+=[ ]+([0-9]{2}:[0-9]{2}:[0-9]{2})\n'
					+ r'Expected Time\s+=[ ]+([0-9]{2}:[0-9]{2}:[0-9]{2})\n'
					+ r'\n'
					+ r'Upstream Motion\s+=[ ]+(.*)\n'
					+ r'\n'
					+ r'Count\s+File\s+Name:[ ]+(?:.*)\n'
					+ r'Editor ID\s+=[ ]+(\w*)\n'
					+ r'Intensity\s+=[ ]+(.*)\n'
					+ r'Threshold\s+=[ ]+(.*)\n'
					+ r'Window Start\s+=[ ]+(.*)\n'
					+ r'Window End\s+=[ ]+(.*)\n'
					+ r'Water Temperature\s+=[ ]+(.*)degC\n'
					+ r'\n'
					+ r'\n'
					+ r'(?:.*)\n+(?:.*)\n\-+'
					+ r'\n([\w\s\S]*?)\n\n+')

	matched = RE1.search(contents)
	
	if not matched:
		raise RuntimeWarning(f'Format of {annot_fp} was not expected.')

	data = matched.groups()

	if data[15].strip() == '':
		raise RuntimeWarning(f'File {annot_fp} has no annotations.')

	if validate:
		return

	# Store into nested dictionary:
	info = {}
	info['tot_fish'] = int(data[0])
	info['num_up'] = int(data[1])
	info['num_down'] = int(data[2])
	info['num_unknown'] = int(data[3])
	info['tot_frames'] = int(data[4])
	info['exp_frames'] = int(data[5])
	info['tot_time'] = data[6]
	info['exp_time'] = data[7]
	info['upstream_motion'] = data[8]
	info['editor_id'] = data[9]
	info['intensity'] = data[10]
	info['threshold'] = data[11]
	info['window_start'] = float(data[12])
	info['window_end'] = float(data[13])
	info['water_temp'] = data[14]
	json_data = {'info': info}

	frames = {}
	json_data['annotations'] = frames
	annotations = re.split(r'\n', data[15])
	RE2 = re.compile(r'(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+'
						+ r'((?:.*?)\s+(?:.*?)\s+(?:.*?)\s+(?:.*?)\s+(?:.*?))\s+'
						+ r'((?:.*?)\s+(?:.*?)\s+(?:.*?)\s+(?:.*?)\s+(?:.*?))\s+')
	for i in range(len(annotations)):
		annotations[i] = annotations[i].strip()
		data = RE2.match(annotations[i]).groups()
		frame = {}
		frame['id'] = int(data[1])
		frame['frame_num'] = int(data[2])
		frame['dir'] = data[3]
		frame['R'] = float(data[4])
		frame['theta'] = float(data[5])
		frame['L'] = float(data[6])
		frame['dR'] = float(data[7])
		frame['L_dR'] = float(data[8])
		frame['aspect'] = float(data[9])
		frame['time'] = data[10]
		frame['date'] = data[11]
		frame['latitude'] = data[12]
		frame['longitude'] = data[13]
		frames[frame['id']] = frame

	return json_data


# Pulls all fish sighting frame intervals from each annotation text file
def get_intervals(data, frame_rate, max_frames):
	padding = int(frame_rate * 10)    # Pad frame range with 10
	clips = []

	annotations = data['annotations']
	for _, value in annotations.items():
		if len(clips) == 0:
			clip = {}
			clip['interval'] = (max(0, int(value['frame_num'] - frame_rate*30)), min(max_frames - 1, int(value['frame_num'] + frame_rate*30)))
			clip['num_fish'] = 1
			clip['time'] = f'''{value['time'][:2]}_{value['time'][3:5]}_{value['time'][6:8]}'''
			clips.append(clip)
		else:
			if clips[-1]['interval'][0] + padding <= value['frame_num'] <= clips[-1]['interval'][1] - padding:
				clips[-1]['num_fish'] += 1
			else:
				clip = {}
				clip['interval'] = (max(0, int(value['frame_num'] - frame_rate*30)), min(max_frames - 1, int(value['frame_num'] + frame_rate*30)))
				clip['num_fish'] = 1
				clip['time'] = f'''{value['time'][:2]}_{value['time'][3:5]}_{value['time'][6:8]}'''
				clips.append(clip)
	return clips


# Generates clips for each sighting interval in given annotation text file
def gen_clips(river_name, river_location, annot_file):
	base = os.path.basename(annot_file)
	RE = re.compile(r'FCe_(.*?)_ID_(.*?).txt')
	name = RE.match(base).groups()[0] # Groups are name and annotator id

	filename = os.path.join(os.path.dirname(annot_file), f'{name}.aris')
	if not os.path.exists(filename):
		raise RuntimeWarning(f'{filename} is missing.')

	ARISdata, frame = pyARIS.DataImport(filename)
	frame_rate = frame.framerate 	# Instantaneous frame rate between frame N and frame N-1 from frame header
	max_frames = ARISdata.FrameCount

	data = parse_data(annot_file)
	clips = get_intervals(data, frame_rate, max_frames)

	# Load in the beam width information
	beam_width_data = pyARIS.load_beam_width_data(frame, beam_width_dir='beam_widths')

	# What is the meter resolution of the smallest sample?
	min_pixel_size = pyARIS.get_minimum_pixel_meter_size(frame, beam_width_data)

	# What is the meter resolution of the sample length?
	sample_length = frame.sampleperiod * 0.000001 * frame.soundspeed / 2

	# Choose the size of a pixel
	pixel_meter_size = max(min_pixel_size, sample_length)

	# Determine the image dimensions
	xdim, ydim, x_meter_start, y_meter_start, _, _  = pyARIS.compute_image_bounds(
	    pixel_meter_size, frame, beam_width_data,
	    additional_pixel_padding_x=0,
	    additional_pixel_padding_y=0
	)
	
	# Compute the mapping from the samples to the image
	sample_read_rows, sample_read_cols, image_write_rows, image_write_cols = pyARIS.compute_mapping_from_sample_to_image(
	    pixel_meter_size,
	    xdim, ydim, x_meter_start, y_meter_start,
	    frame, beam_width_data
	)

	date = next(iter(data['annotations'].values()))['date'] # `next` is required because some annotations are badly formatted

	print(annot_file)
	for i, clip in enumerate(clips):
		clip_name = f'''{river_name}_{river_location}_{date[:4]}_{date[5:7]}_{date[8:]}_{clip['time']}_{clip['num_fish']}'''
		print(f'''\t{i+1}/{len(clips)} : {clip_name}''')
		print(f'''\trange: {clip['interval'][0]} {clip['interval'][1]}''')
		if clip_name != 'kenai_wa_2018_05_26_22_25_30_1':
			continue

		if not os.path.exists(os.path.join(FLAGS.clip_dir, clip_name)):
			os.makedirs(os.path.join(FLAGS.clip_dir, clip_name))

		if not FLAGS.no_infotxt:
			with open(os.path.join(FLAGS.clip_dir, clip_name, 'info.txt'), 'w') as file:
				file.write(f'{os.path.join(FLAGS.clip_dir, clip_name)}\n')
				file.write(f'{filename}\n')
				file.write(f'{river_name}\n')
				file.write(f'{river_location}\n')
				file.write(f'''{clip['num_fish']}\n''')
				file.write(f'{min_pixel_size}\n')
				file.write(f'{sample_length}\n')
				file.write(f'{pixel_meter_size}\n')
				file.write(f'{xdim} {ydim}\n')
				file.write(f'{frame_rate}\n')
				file.write(f'''{clip['interval'][0]} {clip['interval'][1]}\n''')
				file.write(f'''{datetime.strptime(date+clip['time'], '%Y-%m-%d%H_%M_%S')}\n''')

		if FLAGS.save_remap_info:
			np.savez_compressed(os.path.join(FLAGS.clip_dir, clip_name, 'mapping.npz'), sample_read_rows=sample_read_rows, sample_read_cols=sample_read_cols, image_write_rows=image_write_rows, image_write_cols=image_write_cols)

		# Generate frames in range
		pyARIS.make_video(
			ARISdata,
			xdim, ydim, sample_read_rows, sample_read_cols, image_write_rows, image_write_cols,
			FLAGS.clip_dir,
			clip_name,
			fps = frame_rate,
			start_frame = clip['interval'][0],
			end_frame = clip['interval'][1],
			timestamp = True,
			fontsize = 25,
			ts_pos = (0,frame.samplesperbeam-50),
			save_raw = FLAGS.save_raw,
			no_infotxt = FLAGS.no_infotxt
		)
		if FLAGS.zip_location:
			make_archive(os.path.join(FLAGS.zip_location, clip_name), 'zip', os.path.join(FLAGS.clip_dir, clip_name, 'frames/'))
			

def main(argv):
	FLAGS.river_name = FLAGS.river_name.lower()
	FLAGS.river_location = FLAGS.river_location.lower()

	files = []
	for file in Path(FLAGS.aris_dir).rglob('*.txt'):
		try:
			parse_data(file, validate=True)
			files.append(file)

		except RuntimeWarning as err:
			if FLAGS.verbose:
				print(err)

	for file in files:
		try:
			gen_clips(FLAGS.river_name, FLAGS.river_location, file)
		
		except RuntimeWarning as err:
			if FLAGS.verbose:
				print(err)

if __name__ == '__main__':
	app.run(main)