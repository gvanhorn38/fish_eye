import json, math, os, sys

import numpy as np

def max_width(json_file_path):
	"""
	Calculates the length of the fish by taking the largest width.

	:param json_file_name: file path of annotation json file
	:returns: length calculated in meters
	"""
	length = 0.0
	with open(json_file_path) as json_file:
		json_data = json.load(json_file)
		for annotation in json_data['annotations']:
			length = max(length, annotation['bbox'][2])
	length *= json_data['info']['pixel_meter_size']
	return length

def max_diagonal_length(json_file_path):
	"""
	Calculates the length of the fish by taking the largest diagonal length.

	:param json_file_name: file path of annotation json file
	:returns: length calculated in meters
	"""
	length = 0.0
	with open(json_file_path) as json_file:
		json_data = json.load(json_file)
		for annotation in json_data['annotations']:
			_,_,w,h = annotation['bbox']
			length = max(length, math.sqrt(w*w+h*h))
	length *= json_data['info']['pixel_meter_size']
	return length

def average_upper_diagonal_length(json_file_path):
	"""
	Calculates the length of the fish by taking the average of the top 50% of
	diagonal lengths.

	:param json_file_name: file path of annotation json file
	:returns: length calculated in meters
	"""
	lengths = []
	with open(json_file_path) as json_file:
		json_data = json.load(json_file)
		for annotation in json_data['annotations']:
			_,_,w,h = annotation['bbox']
			lengths.append(math.sqrt(w*w+h*h))
	lengths.sort()
	length = json_data['info']['pixel_meter_size'] * np.mean(lengths[len(lengths)//2:])
	return length

def bbox_IOU(bbox1, bbox2, epsilon=1e-10):
	"""
	Calculate the "Intersection over Union" of two bounding boxes.

	:param bbox1: Bounding box in form (left x, top y, width, height)
	:param bbox2: Bounding box in form (left x, top y, width, height)
	:param epsilon: Infinitesimal number used to mitigate divide by 0
	:returns: IOU
	"""
	x1 = max(bbox1[0], bbox2[0])
	y1 = max(bbox1[1], bbox2[1])
	x2 = min(bbox1[0] + bbox1[2], bbox2[0] + bbox2[2])
	y2 = min(bbox1[1] + bbox1[3], bbox2[1] + bbox2[3])

	if x1 > x2 or y1 > y2:
		return 0
	area_overlap = (x2-x1)*(y2-y1)

	return area_overlap / (bbox1[2]*bbox1[3] + bbox2[2]*bbox2[3] + epsilon - area_overlap)

def single_average_IOU(json_file_path):
	"""
	Calculates the average "Intersection over Union" over annotations.

	:param json_file_name: file path of annotation json file
	:returns: average IOU
	"""
	IOUs = []
	with open(json_file_path) as json_file:
		json_data = json.load(json_file)
		last_bbox = []
		for annotation in json_data['annotations']:
			bbox = annotation['bbox']
			if last_bbox:
				IOUs.append(bbox_IOU(bbox, last_bbox))
			last_bbox = bbox
	return np.mean(IOUs)

def extract_bboxes(bboxes, json_file_path):
	"""
	Extract unit-scaled bboxes from a json_file.

	:param json_file_name1: file path annotation json file
	:returns: bboxes through bboxes parameter
	"""
	with open(json_file_path) as json_file:
		json_data = json.load(json_file)
		width, height = json_data['info']['clip_dim']
		for annotation in json_data['annotations']:
			bbox = annotation['bbox']
			bbox[0] /= width
			bbox[1] /= height
			bbox[2] /= width
			bbox[3] /= height
			bboxes.setdefault(annotation['image_id'],[]).append(bbox)

def double_average_IOU(json_file_path1, json_file_path2):
	"""
	Calculates the average "Intersection over Union" over two sets of annotations.

	:param json_file_name1: file path of first annotation json file
	:param json_file_name2: file path of second annotation json file
	:returns: average IOU
	"""
	bboxes = {}

	extract_bboxes(bboxes, json_file_path1)
	extract_bboxes(bboxes, json_file_path2)

	IOUs = []

	for _, value in bboxes.items():
		if len(value) == 1:
			IOUs.append(0)
		else:
			IOUs.append(bbox_IOU(value[0], value[1]))
	return np.mean(IOUs)