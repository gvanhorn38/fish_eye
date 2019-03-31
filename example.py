"""
Example usage.
"""

import matplotlib
from matplotlib import pyplot as plt
from scipy import interpolate
import numpy as np
import imageio
from IPython.display import HTML

import load_aris

# Specify a path to an aris data file
aris_fp = "aris_samples/ARIS_2018-03-27_160000_F11_B96_S1290_T14_R0-27.aris"
beam_width_fp = "beam_widths/BeamWidths_ARIS1800_96.h" # Assumes you are in the project directory

frame_data, meshgrid_X, meshgrid_Y = load_aris.load_frames(aris_fp=aris_fp, beam_width_fp=beam_width_fp)
num_frames = frame_data.shape[0]

# Render the video
print("Press any button to see the next frame")
f = interpolate.interp1d([0, 255], [0, 80])
plt.figure()
plt.ion()
for i in range(num_frames):
    plt.pcolormesh(meshgrid_X, meshgrid_Y, f(frame_data[i]), vmin=0, vmax=80)
    plt.title("Frame: %d" % i)
    plt.ylabel("Meters")
    plt.xlabel("Meters")
    cbar = plt.colorbar()
    cbar.ax.set_ylabel("dB")
    plt.show()

    r = input() # had to replace with input() for Python 3
    plt.clf()
