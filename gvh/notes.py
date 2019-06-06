
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import numpy as np
import cv2

import pyARIS


# Load in the first frame
filename = '../aris_samples/Washington/2018-07-09_190000.aris'
ARISdata, frame = pyARIS.DataImport(filename)

# Load in the beam width information
beam_width_data = pyARIS.load_beam_width_data(frame, beam_width_dir='beam_widths')

# What is the meter resolution of the smallest sample?
min_pixel_size = pyARIS.get_minimum_pixel_meter_size(frame, beam_width_data)

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

# Make a video using some of the frames
pyARIS.make_video(
    ARISdata,
    xdim, ydim, sample_read_rows, sample_read_cols, image_write_rows, image_write_cols,
    '../sample_vids/sample_sm.mp4',
    fps = 25.0,
    start_frame = 690,
    end_frame = 750,
    timestamp = True,
    fontsize = 25,
    ts_pos = (0,frame.samplesperbeam-50)
)





