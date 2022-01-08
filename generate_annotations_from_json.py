import pyDIDSON
import os
import json
import glob
import json
import random
import numpy as np
import boto3
import os

kJsonFile = '/Users/sstat/Projects/Fish_Counting/kenai_batch_4_228_clips_01-05-2022.json'

f = open(kJsonFile);
data = json.load(f);

s3 = boto3.resource('s3')
my_bucket = s3.Bucket('fishcounting')
kS3DataFolder = "data/"

def download_file (file_path):
    aris_filename = kS3DataFolder + file_path
    dst=os.path.realpath(os.getcwd() + "/batch_4/" + file_path)
    directory = os.path.abspath(os.path.dirname(dst))
    if not (os.path.isdir(directory)):
        os.makedirs(directory)
    s3.Bucket('fishcounting').download_file(aris_filename, dst);


results_dir = 'kenai-batch4'
if not os.path.exists(results_dir):
	os.makedirs(results_dir);

i = 0;
for item in data:
	i += 1
	if ( i > 225 ):
		file_path = item['aris_filename']
		download_file ( file_path );
		file_name = file_path.replace("/", '_').replace('.aris','');
		file_name = file_name.replace('kenai_data', '');
		file_name = file_name[1:]

		file_path = os.getcwd() + '/batch_4/' + file_path;
		start_frame = item['start_frame']
		end_frame = item['end_frame']
		output_zip_file_name = '{results_dir}/{fname}_{start_frame}_{end_frame}.zip'.format(results_dir=results_dir, fname=file_name, start_frame=start_frame, end_frame=end_frame)

		print( "[" + str(i) + "] generating frames for aris file " + file_name + " start_frame: " + str(start_frame) + " end_frame: " + str(end_frame) + " to output file: " + output_zip_file_name);
		info = pyDIDSON.get_info ( file_path )
		frames = pyDIDSON.load_frames ( info, start_frame=start_frame, end_frame=end_frame )
		pyDIDSON.save_frames ( output_zip_file_name, frames, multiprocessing=True )

		# no more need for the aris file itself, so remove it to clear up space on machine
		os.remove(file_path);

# 220, 222, 223, 225 failed
# [222] generating frames for aris file 2018-08-16-JD228_RightFar_Stratum2_Set1_RO_2018-08-16_201000 start_frame: 453 end_frame: 653 to output file: kenai-batch4/2018-08-16-JD228_RightFar_Stratum2_Set1_RO_2018-08-16_201000_
# [225] generating frames for aris file 2018-08-16-JD228_RightFar_Stratum3_Set1_RO_2018-08-16_222000 start_frame: 3705 end_frame: 3905 to output file: kenai-batch4/2018-08-16-JD228_RightFar_Stratum3_Set1_RO_2018-08-16_22200
