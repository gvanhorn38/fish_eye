import re
import json
import pyARIS
import os
from datetime import datetime


# Path names as global variables:
clip_dir = '/Volumes/Trout_Data/Elwha/clips/'
json_dir = '/Volumes/Trout_Data/Elwha/json_files/'
aris_dir = '/Volumes/Keith_Denton_04/Elwha 2018/OM/'


# Parser for elwha and kenai formatted annotations text file
def parse_data(annot_fp):
	file = open(annot_fp, "r")
	contents = file.read()

	# parser:
	RE1 = re.compile(r"Total Fish\s+=[ ]+([0-9]+)\nUpstream\s+=[ ]+([0-9]+)\nDownstream\s+=[ ]+([0-9]+)\n\?\?\s+=[ ]+([0-9]+)"
					+ "\n+Total Frames\s+=[ ]+([0-9]+)\nExpected Frames\s+=[ ]+([0-9]+)\nTotal Time\s+=[ ]+([0-9]{2}:[0-9]{2}:[0-9]{2})\nExpected Time\s+=[ ]+([0-9]{2}:[0-9]{2}:[0-9]{2})"
					+ "\n+Upstream Motion\s+=[ ]+(.*)"
					+ "\n+Count\s+File\s+Name:[ ]+(?:.*)"
					+ "\n+Editor ID\s+=[ ]+(\w*)\nIntensity\s+=[ ]+(.*)\nThreshold\s+=[ ]+(.*)\nWindow Start\s+=[ ]+(.*)\nWindow End\s+=[ ]+(.*)(?:\nWater Temperature\s+=[ ]+(.*))*"
					+ "\n+(?:.*)\n+(?:.*)\n\-+"
					+ "\n([\w\s\S]*?)\n+")

	matched = RE1.search(contents)
	
	if not matched:
		print("ERROR: No matches found!")
		return 0

	data = matched.groups()
	if data[15] == '':
		return 1
	# Store into nested dictionary:
	elwha = {}
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
	elwha['info'] = info

	frames = {}
	elwha['annotations'] = frames
	annotations = re.split(r"\n", data[15])
	RE2 = re.compile(r"(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+"
						+ "((?:.*?)\s+(?:.*?)\s+(?:.*?)\s+(?:.*?)\s+(?:.*?))\s+"
						+ "((?:.*?)\s+(?:.*?)\s+(?:.*?)\s+(?:.*?)\s+(?:.*?))\s+")
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

	return elwha


# Stores parsed data into JSON
def store_data(annot_fp, json_fp):
	elwha = parse_data(annot_fp)
	# Store as JSON file:
	print("JSON file stored:", json_fp)
	json.dump(elwha, open(json_fp, 'w'))


# Pulls all clips (fish sightings) from each annotation textfile
def get_clips(data, frame_rate, max_frames):
	padding = int(frame_rate * 10)    # padding of 10s
	clips = []

	annotations = data['annotations']
	for key, value in annotations.items():
		if len(clips) == 0:
			clip = {}
			clip['interval'] = (max(0, int(value['frame_num'] - frame_rate*30)), min(max_frames-1, int(value['frame_num'] + frame_rate*30)))
			clip['num_fish'] = 1
			clip['time'] = value['time'][:2] + "_" + value['time'][3:5] + "_" + value['time'][6:8]
			clips.append(clip)
		else:
			if clips[-1]['interval'][0]+padding <= value['frame_num'] <= clips[-1]['interval'][1]-padding:
				clips[-1]['num_fish'] += 1
			else:
				clip = {}
				clip['interval'] = (max(0,int(value['frame_num'] - frame_rate*30)), min(max_frames-1, int(value['frame_num'] + frame_rate*30)))
				clip['num_fish'] = 1
				clip['time'] = value['time'][:2] + "_" + value['time'][3:5] + "_" + value['time'][6:8]
				clips.append(clip)
	return clips

# Generates a clip (video, folder of images, numpy file, info textfile)
# Note: our current code just generates the first clip of every textfile, if there are multiple clips (since we only want 100 clips).
def gen_clip(annot_file):
	base = os.path.basename(annot_file)
	RE = re.compile(r"FCe_(.*?)_ID_.txt")
	name = RE.match(base).groups()[0]

	# Load in the first frame
	filename = os.path.dirname(annot_file) + "/" + name + ".aris"
	ARISdata, frame = pyARIS.DataImport(filename)
	frame_rate = frame.framerate 	# Instantaneous frame rate between frame N and frame N-1 from frame header
	max_frames = ARISdata.FrameCount

	# Get annotations
	json_path = json_dir + name + ".json"
	# json_path = "/Users/Angelina/Desktop/University/Trout/fish_eye/test.json"
	if not os.path.isfile(json_path):
		store_data(annot_file, json_path)  # 1st param is annotation file path
	data = json.load(open(json_path, "r"))
	clips = get_clips(data, frame_rate, max_frames)

	# Load in the beam width information
	beam_width_data = pyARIS.load_beam_width_data(frame, beam_width_dir='beam_widths')

	# What is the meter resolution of the smallest sample?
	min_pixel_size = pyARIS.get_minimum_pixel_meter_size(frame, beam_width_data)	# change to something larger; dont need min to be too small

	# What is the meter resolution of the sample length?
	sample_length = frame.sampleperiod * 0.000001 * frame.soundspeed / 2

	# Choose the size of a pixel
	pixel_meter_size = max(min_pixel_size, sample_length)

	# Determine the image dimensions
	xdim, ydim, x_meter_start, y_meter_start, x_meter_stop, y_meter_stop  = pyARIS.compute_image_bounds(
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

	# Make a clip of the first annotation
	date = data['annotations']['1']['date']
	clip_name = "elwha_wa_" + date[:4] + "_" + date[5:7] + "_" + date[8:] + "_" + clips[0]['time'] + "_" + str(clips[0]['num_fish'])
	print("clip_name:", clip_name)
	print("range:", clips[0]['interval'][0], clips[0]['interval'][1])


	# Create directory if one doesn't exist
	if not os.path.exists(clip_dir+clip_name):
		os.makedirs(clip_dir+clip_name)

	with open(clip_dir+clip_name+"/info.txt", 'w') as file:
		file.write(clip_dir+clip_name+"\n")
		file.write(filename + "\n")
		file.write("elwha\n")
		file.write("wa\n")
		file.write(str(clips[0]['num_fish'])+"\n")
		file.write(str(min_pixel_size)+"\n")
		file.write(str(sample_length)+"\n")
		file.write(str(pixel_meter_size)+"\n")
		file.write(str(xdim)+" "+str(ydim)+"\n")
		file.write(str(frame_rate)+"\n")
		file.write(str(clips[0]['interval'][0])+" "+str(clips[0]['interval'][1])+"\n")
		file.write(str(datetime.strptime(date+clips[0]['time'], "%Y-%m-%d%H_%M_%S"))+"\n")

	# Make a video using some of the frames
	pyARIS.make_video(
	    ARISdata,
	    xdim, ydim, sample_read_rows, sample_read_cols, image_write_rows, image_write_cols,
	    clip_dir,
	    clip_name,
	    fps = frame_rate,
	    start_frame = clips[0]['interval'][0],
	    end_frame = clips[0]['interval'][1],
	    timestamp = True,
	    fontsize = 25,
	    ts_pos = (0,frame.samplesperbeam-50)
	)

# Returns a list of 100 filenames of the annotation textfiles
def getAnnotFiles(directory):
	folders = os.listdir(directory)
	extensions = ('.txt')
	count = 0
	files = []
	for folder in folders:
		subdir = directory+folder
		for file in os.listdir(subdir):
			ext = os.path.splitext(file)[-1].lower()
			if ext in extensions:
				data = parse_data(os.path.join(subdir, file))
				if data not in [0, 1]:
					count += 1
					files.append(os.path.join(subdir, file))
					if count == 100:
						return files
	return files


def main():
	files = getAnnotFiles(aris_dir)
	i = 0
	for file in files:
		print(str(i)+"\n")
		gen_clip(file)
		i += 1
	

if __name__ == "__main__":
	main()






