from absl import app
from absl import flags
from datetime import datetime
import json
import numpy as np
import os
from pathlib import Path
import re
from shutil import make_archive, rmtree
import tqdm
import uuid

import pyARIS

flags.DEFINE_string(
    'aris_dir', None, 'Path to source ARIS files.'
)
flags.DEFINE_string(
    'clip_dir', None, 'Directory to output generated clips.'
)
flags.DEFINE_string(
    'dump_path', None, 'Directory to output dump of json clips.'
)
flags.DEFINE_string(
    'new_aris_dir', None, 'Base directory to be prepended to ARIS filepaths.'
)
flags.DEFINE_string(
    'zip_location', None, 'Location to zip frames directories to for annotating.\n'
                        + 'Will zip warped-to-scale images regardless of save_raw.'
)
flags.DEFINE_bool(
    'save_raw', False, 'Additionally save un-warped images.'
)
flags.DEFINE_bool(
    'verbose', False, 'Adds extra debugging information.'
)
flags.DEFINE_integer(
    'window_radius', 100, 'Number of frames to include in a clip before or after the manual marking frame.\n'
                        + 'Only used if old_windows is False.'
)
flags.DEFINE_bool(
    'old_windows', False, 'Legacy code for interacting with old annotations.'
)
flags.mark_flag_as_required('aris_dir')
FLAGS = flags.FLAGS

upstream_motion_map = { 
    'Left To Right': 'right',
    'Right To Left': 'left'
}
fish_dir_map = {
    'right': {
        'Up': 'right',
        'Down': 'left'
    },
    'left': {
        'Up': 'left',
        'Down': 'right'
    }
}

json_dump = []
clip_names = set()
count_filenames = set()

# Some manual marking files do not include river direction so we keep track of direction for each camera location and fill in missing values when possible.
river_direction_map = {}

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
        raise RuntimeWarning(f'File {annot_fp} has no markings.')

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

    s = str(os.path.dirname(annot_fp)).replace(FLAGS.aris_dir, '')
    s = s[s.find('/'):]
    if s in river_direction_map:
        if info['upstream_motion'] == 'Undefined':
            info['upstream_motion'] = river_direction_map[s]
        else:
            assert river_direction_map[s] == info['upstream_motion']
    else:
        if info['upstream_motion'] != 'Undefined':
            river_direction_map[s] = info['upstream_motion']

    # River direction is omitted in Elwha data
    if 'elwha' in str(annot_fp).lower():
        info['upstream_motion'] = 'Left To Right'

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
    clips = []
    for value in data['annotations'].values():
        new = len(clips) == 0 or clips[-1]['end_frame'] < value['frame_num'] - FLAGS.window_radius
        start_frame = max(0, value['frame_num'] - FLAGS.window_radius)
        end_frame = min(max_frames - 1, value['frame_num'] + FLAGS.window_radius)
        
        if FLAGS.old_windows: # The check for overlap is broken. This is included for compatibility and should not be used.
            new = len(clips) == 0 or not (clips[-1]['start_frame'] + int(frame_rate * 10) <= value['frame_num'] <= clips[-1]['end_frame'] - int(frame_rate * 10))
            start_frame = max(0, int(value['frame_num'] - frame_rate*30))
            end_frame = min(max_frames - 1, int(value['frame_num'] + frame_rate*30))
        
        if new:
            clip = {}
            clip['start_frame'] = start_frame
            clip['end_frame'] = end_frame
            clip['upstream_direction'] = upstream_motion_map[data['info']['upstream_motion']]
            clip['fish'] = [{
                            'frame': int(value['frame_num']),
                            'direction': fish_dir_map[clip['upstream_direction']][value['dir']],
                            'length': value['L'], 
                            'R': value['R'],
                            'theta': value['theta']
                            }]
            clip['time'] = f'''{value['time'][:2]}_{value['time'][3:5]}_{value['time'][6:8]}'''
            clips.append(clip)
        else:
            clips[-1]['fish'].append({
                            'frame': int(value['frame_num']),
                            'direction': fish_dir_map[clip['upstream_direction']][value['dir']],
                            'length': value['L'], 
                            'R': value['R'],
                            'theta': value['theta']
                            })
    return clips

# Generates clips for each sighting interval in given annotation text file
def gen_clips(annot_file):
    base = os.path.basename(annot_file)
    RE = re.compile(r'FCe_(.*?)_ID_(.*?).txt')
    name = RE.match(base).groups()[0] # Groups are name and annotator id

    filename = os.path.join(os.path.dirname(annot_file), f'{name}.aris')
    if not os.path.exists(filename):
        raise RuntimeWarning(f'{filename} is missing.')

    ARISdata, frame = pyARIS.DataImport(filename)
    frame_rate = frame.framerate     # Instantaneous frame rate between frame N and frame N-1 from frame header
    max_frames = ARISdata.FrameCount

    data = parse_data(annot_file)
    clips = get_intervals(data, frame_rate, max_frames)

    # Load in the beam width information
    beam_width_data, camera_type = pyARIS.load_beam_width_data(frame, beam_width_dir='beam_widths')

    # What is the meter resolution of the smallest sample?
    min_pixel_size = pyARIS.get_minimum_pixel_meter_size(frame, beam_width_data)

    # What is the meter resolution of the sample length?
    sample_length = frame.sampleperiod * 0.000001 * frame.soundspeed / 2

    # Choose the size of a pixel
    pixel_meter_size = max(min_pixel_size, sample_length)

    # Determine the image dimensions
    xdim, ydim, x_meter_start, y_meter_start, x_meter_stop, y_meter_stop = pyARIS.compute_image_bounds(
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
    marking_mapping = dict(zip(zip(sample_read_rows, sample_read_cols), 
                                zip(image_write_rows, image_write_cols)))

    annot_file = annot_file.replace('/fishcounting/kenai_data/', '')
    # date = next(iter(data['annotations'].values()))['date']
    for i, clip in enumerate(clips):
        clip_name = filename.replace('/fishcounting/kenai_data/', '').replace('/', '_').replace('.aris', '')
        clip_name += f'_{clip["start_frame"]}_{clip["end_frame"]}'


        # clip_name = str(os.path.dirname(annot_file)).replace(str(Path(FLAGS.aris_dir).parent)+'/', '').replace('/', '_').replace('\\', '_').replace(' ', '_')
        # clip_name += f'_{clip["start_frame"]}_{clip["end_frame"]}'

        print(clip_name)

        if clip_name not in clip_names:
            print(clip_name, 'not a clip')
            continue

        entry = {}
        if FLAGS.new_aris_dir is not None:
            filename = str(filename).replace(str(Path(FLAGS.aris_dir).parent)+'/', FLAGS.new_aris_dir)
        entry['aris_filename'] = str(filename)

        entry['clip_name'] = clip_name

        entry['start_frame'] = clip['start_frame']
        entry['end_frame'] = clip['end_frame']
        entry['start_time'] = pyARIS.FrameRead(ARISdata, entry['start_frame']).sonartimestamp
        entry['end_time'] = pyARIS.FrameRead(ARISdata, entry['end_frame']).sonartimestamp
        entry['upstream_direction'] = clip['upstream_direction']

        entry['fish'] = []
        for marking in clip['fish']:
            R = int((marking['R']-frame.windowstart)/pixel_meter_size)
            Theta = np.argmin(np.abs(beam_width_data['beam_center']-marking['theta']))
            if (R, Theta) not in marking_mapping:
                if FLAGS.verbose:
                    print(f'(R={R}, Theta={Theta}) can not be mapped.')
                continue
            y, x = marking_mapping[(R, Theta)]

            marking['x'] = x / xdim
            marking['y'] = y / ydim
            entry['fish'].append(marking)

        entry['aris_info'] = {}
        entry['aris_info']['camera_type'] = camera_type
        entry['aris_info']['framerate'] = frame_rate
        entry['aris_info']['pixel_meter_size'] = pixel_meter_size
        entry['aris_info']['xdim'] = xdim
        entry['aris_info']['ydim'] = ydim
        entry['aris_info']['x_meter_start'] = x_meter_start
        entry['aris_info']['y_meter_start'] = y_meter_start
        entry['aris_info']['x_meter_stop'] = x_meter_stop
        entry['aris_info']['y_meter_stop'] = y_meter_stop

        json_dump.append(entry)

        with open(FLAGS.dump_path, 'w') as dump_file:
            json.dump(json_dump, dump_file, indent=2)

        if FLAGS.clip_dir is not None:
            if not os.path.exists(os.path.join(FLAGS.clip_dir, clip_name)):
                os.makedirs(os.path.join(FLAGS.clip_dir, clip_name))

            # Generate frames in range
            pyARIS.make_video(
                ARISdata,
                xdim, ydim, sample_read_rows, sample_read_cols, image_write_rows, image_write_cols,
                FLAGS.clip_dir,
                clip_name,
                fps = frame_rate,
                start_frame = clip['start_frame'],
                end_frame = clip['end_frame'],
                timestamp = True,
                fontsize = 25,
                ts_pos = (0,frame.samplesperbeam-50)
            )
            if FLAGS.zip_location:
                make_archive(os.path.join(FLAGS.zip_location, clip_name), 'zip', os.path.join(FLAGS.clip_dir, clip_name, 'frames/'))
                rmtree(os.path.join(FLAGS.clip_dir, clip_name, 'frames/'))

def main(argv):
    assert FLAGS.clip_dir or FLAGS.dump_path, 'Must define output directory for clips or json dump path or there is no task.'

    # with open('batch3_justin.json') as json_file:
    #     json_dump = json.load(json_file)

    # for entry in json_dump:
    #     clip_name = entry['aris_filename'].replace('kenai_data/', '').replace('/', '_').replace('.aris', '')
    #     clip_name += f'_{entry["start_frame"]}_{entry["end_frame"]}'

    #     clip_names.add(clip_name)
    #     count_filenames.add(entry['count_filename'])
    
    # files = count_filenames
    for file in tqdm.tqdm(Path(FLAGS.aris_dir).rglob('*.txt'), desc='Parsing/Downloading'):
        try:
            parse_data(file, validate=True)
            files.append(file)

        except RuntimeWarning as err:
            if FLAGS.verbose:
                print(err)

    print(len(files))
    with open('temp_files.json', 'w') as json_file:
        json.dump(files, json_file, indent=2)

    for file in tqdm.tqdm(files, desc='Processing Marking File', position=0, leave=True):
        try:
            gen_clips(os.path.join(FLAGS.aris_dir, file))
            
        except RuntimeWarning as err:
            if FLAGS.verbose:
                print(err)
    
    if FLAGS.dump_path is not None:
        with open(FLAGS.dump_path, 'w') as dump_file:
            json.dump(json_dump, dump_file, indent=2)

if __name__ == '__main__':
    app.run(main)