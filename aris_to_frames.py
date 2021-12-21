from collections import namedtuple
import numpy as np
import os 
import cv2
import pyARIS
from PIL import Image

# TODO: This is largely taken from fisheye_flask/aris.py write_frames function. I was not able to get write_frames to work without being killed by the OS
# https://github.com/justinkay/fisheye_flask/blob/54b4df520e7894fc4d910b90c24f2f05e1743f9f/aris.py#L63

BEAM_WIDTH_DIR = './beam_widths/'

# Aris file in local directory
#kArisFilePath = '/Users/sstat/Projects/Fish_Counting/candidate_nusagak_batch4_data/RB_2018-06-12_191000.aris'
kArisFilePath = '/Users/sstat/Downloads/2018-07-10_230000.aris'
kFileName = os.path.basename(kArisFilePath).replace ( ".aris", "" )

# Directory where you want the frames and compiled video to be written
kOutFileDirectory = '/Users/sstat/Projects/Fish_Counting/candidate_elwha_batch4_data/';

ImageData = namedtuple('ImageData', [
    'pixel_meter_size',
    'xdim', 'ydim',
    'x_meter_start', 'y_meter_start', 'x_meter_stop', 'y_meter_stop',
    'sample_read_rows', 'sample_read_cols', 'image_write_rows', 'image_write_cols'
])

def FasterARISRead(fp, ARISdata, image_data, start_frame, end_frame):
    FrameSize = ARISdata.SamplesPerChannel*ARISdata.NumRawBeams
    fp.seek(start_frame*(1024+(FrameSize))+2048, 0)
    return np.array([np.frombuffer(fp.read(1024+FrameSize)[:FrameSize], dtype=np.uint8) for _ in range(end_frame-start_frame)], dtype=np.float32).reshape([end_frame-start_frame, ARISdata.SamplesPerChannel, ARISdata.NumRawBeams])[...,::-1]

def get_frames(fp, ARISdata, image_data, start_frame, end_frame):
    frames = np.zeros([end_frame - start_frame, image_data.ydim, image_data.xdim], dtype=np.float32)
    frames[:, image_data.image_write_rows, image_data.image_write_cols] = FasterARISRead(fp, ARISdata, image_data, start_frame, end_frame)[:, image_data.sample_read_rows, image_data.sample_read_cols]
    return frames

# Write the frames to a particular directory
frames_dir = os.path.join ( kOutFileDirectory, f'{kFileName}-frames' )
os.makedirs ( frames_dir, exist_ok=True )
print ( "Writing frames to", frames_dir )


ARISdata, aris_frame = pyARIS.DataImport(kArisFilePath)
frame_size = ARISdata.SamplesPerChannel * ARISdata.NumRawBeams
beam_width_data = pyARIS.load_beam_width_data(aris_frame, beam_width_dir=BEAM_WIDTH_DIR)[0]
# What is the meter resolution of the smallest sample?
min_pixel_size = pyARIS.get_minimum_pixel_meter_size(aris_frame, beam_width_data)
# What is the meter resolution of the sample length?
sample_length = aris_frame.sampleperiod * 0.000001 * aris_frame.soundspeed / 2
# Choose the size of a pixel (or hard code it to some specific value)
pixel_meter_size = max(min_pixel_size, sample_length)
# Determine the image dimensions
xdim, ydim, x_meter_start, y_meter_start, x_meter_stop, y_meter_stop = pyARIS.compute_image_bounds(
    pixel_meter_size, aris_frame, beam_width_data,
    additional_pixel_padding_x=0,
    additional_pixel_padding_y=0
)
# Compute the mapping from the samples to the image
sample_read_rows, sample_read_cols, image_write_rows, image_write_cols = pyARIS.compute_mapping_from_sample_to_image(
    pixel_meter_size,
    xdim, ydim, x_meter_start, y_meter_start,
    aris_frame, beam_width_data
)
image_data = ImageData(
    pixel_meter_size,
    xdim, ydim, x_meter_start, y_meter_start, x_meter_stop, y_meter_stop,
    sample_read_rows, sample_read_cols, image_write_rows, image_write_cols
)

fp = open(kArisFilePath, 'rb')
print ("StartFrame: " + str(ARISdata.StartFrame) + " EndFrame: " + str(ARISdata.EndFrame))
print("FrameCount " + str(ARISdata.FrameCount));
# It would be ideal if start_frame=0 and end_frame = ARISData.FrameCount
# On my Mac (3 GHz Dual-Core Intel Core i7 8 GB 1600 MHz DDR3), 100 frames was a nice place to iterate on. 
# 1000+ frames took too long to move through annotation candidates
frame_start=239
frame_count=3828#ARISdata.FrameCount
# in chunks of 100 frames, write frames to disk
step = 100
a = np.arange(frame_start, frame_count+step, step)
for i in range(0,len(a)):
	if len(a) <= i+1:
		break;
	start_frame = a[i];
	end_frame = a[i+1];
	frames = get_frames(fp, ARISdata, image_data, start_frame=start_frame, end_frame=end_frame)

	blurred_frames = frames.astype(np.float32)
	for i in range(frames.shape[0]):
	    blurred_frames[i] = cv2.GaussianBlur(
	        blurred_frames[i],
	        (5,5),
	        0
	    )

	print ( "Done writing cv.GaussianBlur");
	mean_blurred_frame = None
	if mean_blurred_frame is None:
	    mean_blurred_frame = blurred_frames.mean(axis=0)

	blurred_frames -= mean_blurred_frame

	mean_normalization_value = None
	if mean_normalization_value is None:
	    mean_normalization_value = np.max(np.abs(blurred_frames))

	blurred_frames /= mean_normalization_value
	blurred_frames += 1
	blurred_frames /= 2

	# Because of the optical flow computation, we only go to end_frame - 1
	print("Writing frames " + str(start_frame) + " to " + str(end_frame));
	for j, frame_offset in enumerate(range(start_frame, end_frame - 1)):
	    frame_image = np.dstack([
	                    frames[j] / 255,
	                    blurred_frames[j],
	                    np.abs(blurred_frames[j+1] - blurred_frames[j])
	                ]).astype(np.float32)
	    frame_image = (frame_image * 255).astype(np.uint8)
	    out_fp = os.path.join(frames_dir, f'{start_frame+j}.jpg') # = frame_offset.jpg?
	    Image.fromarray(frame_image).save(out_fp, quality=95)
	    
	print("frames written");

# Create a video from the written frames
video_filepath = os.path.join ( kOutFileDirectory, f"{kFileName}.mp4" )
cmd = "ffmpeg -framerate 10 -pattern_type glob -i '" + frames_dir +"/*.jpg' " + video_filepath;
print(cmd);
os.system(cmd);
print ( "Video written to", video_filepath )
