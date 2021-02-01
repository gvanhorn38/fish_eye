from collections import Counter
from colorsys import hls_to_rgb
from copy import deepcopy
import json
import numpy as np

from fish_length import Fish_Length
from sort import Sort

class Tracker:
    def __init__(self, clip_info, algorithm=Sort, args={'max_age':1, 'min_hits':0, 'iou_threshold':0.05}, min_hits=3):
        self.algorithm = algorithm(**args)
        self.fish_ids = Counter()
        self.min_hits = min_hits
        self.json_data = deepcopy(clip_info)
        self.frame_id = self.json_data['start_frame']
        self.json_data['frames'] = []

    # Boxes should be given in normalized [x1,y1,x2,y2,c]
    def update(self, dets=np.empty((0, 5))):
        new_frame_entries = []
        for track in self.algorithm.update(dets):
            self.fish_ids[int(track[4])] += 1
            new_frame_entries.append({
            'fish_id': int(track[4]),
            'bbox': list(track[:4]),
            'visible': 1,
            'human_labeled': 0
            })
        new_frame_entries = sorted(new_frame_entries, key=lambda k: k['fish_id']) 

        self.json_data['frames'].append(
            {
                'frame_num': self.frame_id,
                'fish': new_frame_entries
            })
        self.frame_id += 1
    
    def finalize(self, output_path=None, min_length=-1.0): # vert_margin=0.0
        fish_id_map = {}
        fish_start_end = {}
        json_data = deepcopy(self.json_data)

        for fish_id, count in self.fish_ids.items():
            if count >= self.min_hits:
                fish_id_map[fish_id] = len(fish_id_map)
                fish_start_end[fish_id] = [[], []]

        for i, frame in enumerate(json_data['frames']):
            new_frame_entries = []
            for frame_entry in frame['fish']:
                if frame_entry['fish_id'] in fish_id_map:
                    if not fish_start_end[frame_entry['fish_id']][0]:
                        fish_start_end[frame_entry['fish_id']][0] = [i, len(new_frame_entries)]
                    fish_start_end[frame_entry['fish_id']][1] = [i, len(new_frame_entries)]
                    frame_entry['fish_id'] = fish_id_map[frame_entry['fish_id']]
                    new_frame_entries.append(frame_entry)
            frame['fish'] = sorted(new_frame_entries, key=lambda k: k['fish_id'])

        json_data['fish'] = []
        for track_id, (start_frame_index, end_frame_index) in enumerate(fish_start_end.values()):
            fish_entry = {}
            fish_entry['id'] = track_id

            # top = False
            # bottom = False
            # for frame in json_data['frames']:
            #     for frame_entry in frame['fish']:
            #         if frame_entry['fish_id'] == track_id:
            #             if frame_entry['bbox'][3] > vert_margin:
            #                 top = True
            #             if frame_entry['bbox'][1] < 1 - vert_margin:
            #                 bottom = True
            #             break

            # if not top or not bottom:
            #     continue

            fish_entry['length'] = -1

            start_bbox = json_data['frames'][start_frame_index[0]]['fish'][start_frame_index[1]]['bbox']
            end_bbox = json_data['frames'][end_frame_index[0]]['fish'][end_frame_index[1]]['bbox']

            fish_entry['direction'] = Tracker.get_direction(start_bbox, end_bbox)
            fish_entry['start_frame_index'] = start_frame_index[0]
            fish_entry['end_frame_index'] = end_frame_index[0]
            fish_entry['color'] = Tracker.selectColor(track_id)

            json_data['fish'].append(fish_entry)

        json_data = Fish_Length.add_lengths(json_data)

        if min_length != -1.0:
            new_fish = []
            for fish in json_data['fish']:
                if fish['length'] > min_length:
                    new_fish.append(fish)
            json_data['fish'] = new_fish

        if output_path is not None:
            with open(output_path,'w') as output:
                json.dump(json_data, output, indent=2)

        return json_data

    def state(self, output_path=None):
        json_data = deepcopy(self.json_data)

        if output_path is not None:
            with open(output_path,'w') as output:
                json.dump(json_data, output, indent=2)
        
        return json_data

    @staticmethod
    def selectColor(number):
        hue = ((number * 137.508 + 60) % 360) / 360
        return '#{0:02x}{1:02x}{2:02x}'.format(*(int(n * 255) for n in hls_to_rgb(hue, 0.5, 0.75)))

    @staticmethod
    def get_direction(start_bbox, end_bbox):
        start_center = (start_bbox[2] + start_bbox[0])/2
        end_center = (end_bbox[2] + end_bbox[0])/2
        if start_center < 0.5 and end_center >= 0.5:
            return 'right'
        elif start_center >= 0.5 and end_center < 0.5:
            return 'left'
        else:
            return 'none'

    @staticmethod
    def count_dirs(json_data):
        right = 0
        left = 0
        none = 0
        for fish_entry in json_data['fish']:
            if fish_entry['direction'] == 'right':
                right += 1
            elif fish_entry['direction'] == 'left':
                left += 1
            else:
                none += 1
        return (right, left, none)
