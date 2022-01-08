"""
Utilities to read and produce to-scale images from DIDSON and ARIS sonar files.

Portions of this code were adapted from SoundMetrics MATLAB code.
"""
__version__ = 'b1.0.0'

import contextlib
import itertools
from matplotlib.cm import get_cmap
import numpy as np
import os
import pandas as pd
from PIL import Image
from shutil import make_archive, rmtree
import struct
from types import SimpleNamespace

import pyARIS
from pyDIDSON_format import *


def get_info(file, beam_width_dir='beam_widths', ixsize=-1):
    """ Load header info from DIDSON or ARIS file and precompute some warps.
    
    Parameters
    ----------
    file : file-like object, string, or pathlib.Path
        The DIDSON or ARIS file to read.
    beam_width_dir : string or pathlib.Path, optional
        Location of ARIS beam width CSV files. Only used for ARIS files.
    ixsize : int, optional
        x-dimension width of output warped images to produce. Width is approximate for ARIS files and definite for
        DIDSON. If not specified, the default for ARIS is determined by pyARIS and the default for DIDSON is 300.

    Returns
    -------
    didson_info : dict
        Dictionary of extracted headers and computed sonar values.

    """

    if hasattr(file, 'read'):
        file_ctx = contextlib.nullcontext(file)
    else:
        file_ctx = open(file, 'rb')

    with file_ctx as fid:
        assert fid.read(3) == b'DDF'

        version_id = fid.read(1)[0]
        # print(f'Version {version_id}')

        fid.seek(0)

        didson_info = {
            'pydidson_version': __version__,
        }

        file_attributes, frame_attributes = {
            0: NotImplementedError,
            1: NotImplementedError,
            2: NotImplementedError,
            3: [file_attributes_3, frame_attributes_3],
            4: [file_attributes_4, frame_attributes_4],
            5: [file_attributes_5, frame_attributes_5],
        }[version_id]

        fileheaderformat = '=' + ''.join(file_attributes.values())
        fileheadersize = struct.calcsize(fileheaderformat)
        didson_info.update(dict(zip(file_attributes.keys(), struct.unpack(fileheaderformat, fid.read(fileheadersize)))))

        frameheaderformat = '=' + ''.join(frame_attributes.values())
        frameheadersize = struct.calcsize(frameheaderformat)
        didson_info.update(dict(zip(frame_attributes.keys(), struct.unpack(frameheaderformat, fid.read(frameheadersize)))))

        didson_info.update( {
            'fileheaderformat': fileheaderformat,
            'fileheadersize': fileheadersize,
            'frameheaderformat': frameheaderformat,
            'frameheadersize': frameheadersize,
        } )

        if version_id == 0:
            raise NotImplementedError
        elif version_id == 1:
            raise NotImplementedError
        elif version_id == 2:
            raise NotImplementedError
        elif version_id == 3:
            # Convert windowlength code to meters
            didson_info['windowlength'] = {
                0b00: [0.83, 2.5, 5, 10, 20, 40],  # DIDSON-S, Extended Windows
                0b01: [1.125, 2.25, 4.5, 9, 18, 36],  # DIDSON-S, Classic Windows
                0b10: [2.5, 5, 10, 20, 40, 70],  # DIDSON-LR, Extended Window
                0b11: [2.25, 4.5, 9, 18, 36, 72],  # DIDSON-LR, Classic Windows
            }[didson_info['configflags'] & 0b11][didson_info['windowlength'] + 2 * (1 - didson_info['resolution'])]

            # Windowstart 1 to 31 times 0.75 (Lo) or 0.375 (Hi) or 0.419 for extended
            didson_info['windowstart'] = {
                0b0: 0.419 * didson_info['windowstart'] * (2 - didson_info['resolution']),  # meters for extended DIDSON
                0b1: 0.375 * didson_info['windowstart'] *
                (2 - didson_info['resolution']),  # meters for standard or long range DIDSON
            }[didson_info['configflags'] & 0b1]

            didson_info['halffov'] = 14.4
        elif version_id == 4:
            # Convert windowlength code to meters
            didson_info['windowlength'] = [1.25, 2.5, 5, 10, 20,
                                           40][didson_info['windowlength'] + 2 * (1 - didson_info['resolution'])]

            # Windowstart 1 to 31 times 0.75 (Lo) or 0.375 (Hi) or 0.419 for extended
            didson_info['windowstart'] = 0.419 * didson_info['windowstart'] * (2 - didson_info['resolution'])

            didson_info['halffov'] = 14.4
        elif version_id == 5:  #ARIS
            if didson_info['pingmode'] in [1, 2]:
                BeamCount = 48
            elif didson_info['pingmode'] in [3, 4, 5]:
                BeamCount = 96
            elif didson_info['pingmode'] in [6, 7, 8]:
                BeamCount = 64
            elif didson_info['pingmode'] in [9, 10, 11, 12]:
                BeamCount = 128
            else:
                raise

            WinStart = didson_info['samplestartdelay'] * 0.000001 * didson_info['soundspeed'] / 2

            didson_info .update ( {
                'BeamCount': BeamCount,
                'WinStart': WinStart,
            } )

            aris_frame = SimpleNamespace(**didson_info)

            beam_width_data, camera_type = pyARIS.load_beam_width_data(frame=aris_frame, beam_width_dir=beam_width_dir)

            # What is the meter resolution of the smallest sample?
            min_pixel_size = pyARIS.get_minimum_pixel_meter_size(aris_frame, beam_width_data)

            # What is the meter resolution of the sample length?
            sample_length = aris_frame.sampleperiod * 0.000001 * aris_frame.soundspeed / 2

            # Choose the size of a pixel (or hard code it to some specific value)
            pixel_meter_size = max(min_pixel_size, sample_length)

            # Determine the image dimensions
            xdim, ydim, x_meter_start, y_meter_start, x_meter_stop, y_meter_stop = pyARIS.compute_image_bounds(
                pixel_meter_size,
                aris_frame,
                beam_width_data,
                additional_pixel_padding_x=0,
                additional_pixel_padding_y=0)

            if ixsize != -1:
                pixel_meter_size = pixel_meter_size * xdim / ixsize
                pixel_meter_size += 1e-5
                xdim, ydim, x_meter_start, y_meter_start, x_meter_stop, y_meter_stop = pyARIS.compute_image_bounds(
                    pixel_meter_size,
                    aris_frame,
                    beam_width_data,
                    additional_pixel_padding_x=0,
                    additional_pixel_padding_y=0)

            didson_info.update ( {
                'camera_type': camera_type,
                'min_pixel_size': min_pixel_size,
                'sample_length': sample_length,
                'pixel_meter_size': pixel_meter_size,
                'xdim': xdim,
                'ydim': ydim,
                'x_meter_start': x_meter_start,
                'y_meter_start': y_meter_start,
                'x_meter_stop': x_meter_stop,
                'y_meter_stop': y_meter_stop,
                'beam_width_dir': os.path.abspath(beam_width_dir),
            } )

            didson_info['halffov'] = 14
        else:
            raise

        if version_id < 5:
            didson_info['ixsize'] = 300 if ixsize == -1 else ixsize

    didson_info['filename'] = os.path.abspath(file_ctx.name)

    return didson_info


def __lens_distortion(nbeams, theta):
    """ Removes Lens distortion determined by empirical work at the barge.
    
    Parameters
    ----------
    nbeams : int
        Number of sonar beams.
    theta : (A,) ndarray
        Angle of warp for each x index.

    Returns
    -------
    beamnum : (A,) ndarray
        Distortion-adjusted beam number for each theta.

    """

    factor, a = {
        48: [1, [.0015, -0.0036, 1.3351, 24.0976]],
        189: [4.026, [.0015, -0.0036, 1.3351, 24.0976]],
        96: [1.012, [.0030, -0.0055, 2.6829, 48.04]],
        381: [4.05, [.0030, -0.0055, 2.6829, 48.04]],
    }[nbeams]

    return np.rint(factor * (a[0] * theta**3 + a[1] * theta**2 + a[2] * theta + a[3]) + 1).astype(np.uint32)


def __mapscan(didson_info):
    """ Calculate warp mapping from raw to scale images.
    
    Parameters
    ----------
    didson_info : dict
        Dictionary of extracted headers and computed sonar values.

    Returns
    -------
    isize : (iysize : int, ixsize : int)
        Dimensions of warped image.
    svector : (nbeams * nbins,) ndarray, np.uint32
        Flat representation of warped sonar image where each value is the index of the flattened raw sonar data, or 0.

    """

    ixsize = didson_info['ixsize']
    rmin = didson_info['windowstart']
    rmax = rmin + didson_info['windowlength']
    halffov = didson_info['halffov']
    nbeams = didson_info['numbeams']
    nbins = didson_info['samplesperchannel']

    degtorad = 3.14159 / 180  # conversion of degrees to radians
    radtodeg = 180 / 3.14159  # conversion of radians to degrees

    d2 = rmax * np.cos(halffov * degtorad)  # see drawing (distance from point scan touches image boundary to origin)
    d3 = rmin * np.cos(halffov * degtorad)  # see drawing (bottom of image frame to r,theta origin in meters)
    c1 = (nbins - 1) / (rmax - rmin)  # precalcualtion of constants used in do loop below
    c2 = (nbeams - 1) / (2 * halffov)

    gamma = ixsize / (2 * rmax * np.sin(halffov * degtorad))  # Ratio of pixel number to position in meters
    iysize = int(np.fix(gamma * (rmax - d3) + 0.5))  # number of pixels in image in vertical direction
    svector = np.zeros(ixsize * iysize, dtype=np.uint32)  # make vector and fill in later
    ix = np.arange(1, ixsize + 1)  # pixels in x dimension
    x = ((ix - 1) - ixsize / 2) / gamma  # convert from pixels to meters

    isize = [iysize, ixsize]

    for iy in range(1, iysize + 1):
        y = rmax - (iy - 1) / gamma  # convert from pixels to meters
        r = np.sqrt(y**2 + x**2)  # convert to polar cooridinates
        theta = radtodeg * np.arctan2(x, y)  # theta is in degrees
        binnum = np.rint((r - rmin) * c1 + 1.5).astype(np.uint32)  # the rangebin number
        beamnum = __lens_distortion(nbeams, theta)  # remove lens distortion using empirical formula

        # find position in sample array expressed as a vector
        # make pos = 0 if outside sector, else give it the offset in the sample array
        pos = (beamnum > 0) * (beamnum <= nbeams) * (binnum > 0) * (binnum <= nbins) * ((beamnum - 1) * nbins + binnum)
        svector[(ix - 1) * iysize + iy - 1] = pos  # The offset in this array is the pixel offset in the image array
        # The value at this offset is the offset in the sample array

    svector[svector == 0] = 1  # set all zero elements to one to satisfy matlab indexing rules.
    svector -= 1

    svector = np.fliplr(
        np.arange(didson_info['samplesperchannel'] * didson_info['numbeams']).reshape(
            didson_info['samplesperchannel'],
            didson_info['numbeams']).T.flat[svector.reshape(ixsize, iysize).T.flatten()].reshape(isize)).flatten()
    return isize, svector  # Output the calculated y size of the image array and the map vector


def __FasterDIDSONRead(file, didson_info, start_frame, end_frame):
    """ Load raw frames from DIDSON.
    
    Parameters
    ----------
    file : file-like object, string, or pathlib.Path
        The DIDSON or ARIS file to read.
    didson_info : dict
        Dictionary of extracted headers and computed sonar values.
    start_frame : int
        Zero-indexed start of frame range (inclusive).
    end_frame : int
        End of frame range (exclusive).

    Returns
    -------
    raw_frames : (end_frame - start_frame, framesize) ndarray, np.uint8
        Extracted and flattened raw sonar measurements for frame range.

    """

    if hasattr(file, 'read'):
        file_ctx = contextlib.nullcontext(file)
    else:
        file_ctx = open(file, 'rb')

    with file_ctx as fid:
        framesize = didson_info['samplesperchannel'] * didson_info['numbeams']
        frameheadersize = didson_info['frameheadersize']

        fid.seek(didson_info['fileheadersize'] + start_frame * (frameheadersize + framesize) + frameheadersize, 0)

        return np.array([
            np.frombuffer(fid.read(framesize + frameheadersize)[:framesize], dtype=np.uint8)
            for _ in range(end_frame - start_frame)
        ],
                        dtype=np.uint8)


def load_frames(didson_info, file=None, start_frame=-1, end_frame=-1):
    """ Load and warp DIDSON or ARIS frames into images.
    
    Parameters
    ----------
    didson_info : dict
        Dictionary of extracted headers and computed sonar values.
    file : file-like object, string, or pathlib.Path, optional
        The DIDSON or ARIS file to read. Defaults to `filename` in `didson_info`.
    start_frame : int, optional
        Zero-indexed start of frame range (inclusive). Defaults to the first available.
    end_frame : int, optional
        End of frame range (exclusive). Defaults to the last available frame.

    Returns
    -------
    frames : (end_frame - start_frame, iysize, ixsize) ndarray, np.uint8
        Warped-to-scale sonar image tensor.

    """

    if file is None:
        file = didson_info['filename']

    if hasattr(file, 'read'):
        file_ctx = contextlib.nullcontext(file)
    else:
        file_ctx = open(file, 'rb')

    with file_ctx as fid:
        if start_frame == -1:
            start_frame = didson_info['startframe']
        if end_frame == -1:
            end_frame = didson_info['endframe'] or didson_info['numframes']

        if didson_info['version'][-1] == 5:
            isize = [didson_info['ydim'], didson_info['xdim']]
            aris_frame = SimpleNamespace(**didson_info)

            beam_width_data = pd.read_csv(
                os.path.join(didson_info['beam_width_dir'], didson_info['camera_type'] + '.csv'))

            sample_read_rows, sample_read_cols, image_write_rows, image_write_cols = pyARIS.compute_mapping_from_sample_to_image(
                didson_info['pixel_meter_size'], isize[1], isize[0], didson_info['x_meter_start'],
                didson_info['y_meter_start'], aris_frame, beam_width_data)

            svector = np.zeros(isize[0] * isize[1], dtype=np.uint32)
            svector[image_write_rows * isize[1] +
                    image_write_cols] = sample_read_rows * didson_info['numbeams'] + didson_info[
                        'numbeams'] - sample_read_cols - 1

        else:
            isize, svector = __mapscan(didson_info)

        # Record the proportion of measurements that are present in the warp (increases as ixsize increases)
        didson_info['proportion_warp'] = len(
            np.unique(svector)) / (didson_info['numbeams'] * didson_info['samplesperchannel'])

        frames = __FasterDIDSONRead(fid, didson_info, start_frame, end_frame)
        frames[:, 0] = 0
        return frames[:, svector].reshape(end_frame - start_frame, *isize)


def __mpmap(func, iterable, processes=os.cpu_count() - 1, niceness=1, threading=False, flatten=False):
    """ Helper function to add simple multiprocessing capabilities.
    
    Parameters
    ----------
    func : function
        Function to be mapped.
    iterable : iterable
        Domain to be mapped over.
    processes : int, optional
        Number of processes to spawn. Default is one for all but one CPU core.
    niceness : int, optional
        Process niceness.
    threading : bool, optional
        If enabled replaces multiprocessing with multithreading
    flatten : bool, optional
        If enabled chains map output together before returning.
        
    Returns
    -------
    output : list
        Image of mapped func over iterable.

    """

    import multiprocess as mp
    import multiprocess.dummy

    def initializer():
        os.nice(niceness)

    pool_class = mp.dummy.Pool if threading else mp.Pool

    pool = pool_class(processes=processes, initializer=initializer)

    out = pool.map(func, iterable)

    if flatten:
        out = list(itertools.chain.from_iterable(out))

    pool.close()
    pool.join()

    return out


def save_frames(path, frames, pad_zeros=False, multiprocessing=False, ydim=None, xdim=None, quality='web_high'):
    """ Save frames as JPEG images.
    
    Parameters
    ----------
    path : string or pathlib.Path
        Directory to output images to or zip file.
    frames : (end_frame - start_frame, iysize, ixsize) ndarray, np.uint8
        Warped-to-scale sonar image tensor.
    pad_zeros : bool, optional
        If enabled adds appropriately padded zeros to filenames so alphabetic sort of images returns expected ordering.
        Note that this option is turned off by default for compatibility with vatic.js which requires that filenames
        are not padded.
    multiprocessing : bool, optional
        If enabled adds multi-process optimization for writing images.
    ydim : int, optional
        If provided resizes image to given ydim before saving.
    xdim : int, optional
        If provided resizes image to given xdim before saving.
    quality : int or str
        Either integer 1-100 or JPEG compression preset seen here:
        https://github.com/python-pillow/Pillow/blob/master/src/PIL/JpegPresets.py

    """

    path = str(path)

    to_zip = path.endswith('.zip')

    if to_zip:
        path = os.path.splitext(path)[0]

    if not os.path.exists(path):
        os.mkdir(path)

    if pad_zeros:
        filename = f'{path}/{{:0{int(np.ceil(np.log10(len(frames))))}}}.jpg'
    else:
        filename = f'{path}/{{}}.jpg'

    ydim = ydim or frames.shape[1]
    xdim = xdim or frames.shape[2]

    viridis = get_cmap()

    def f(n):
        Image.fromarray(viridis(n[1], bytes=True)[..., :3]).resize((xdim, ydim)).save(filename.format(n[0]),
                                                                                      quality=quality)

    ns = enumerate(frames)
    if multiprocessing:
        __mpmap(f, ns)
    else:
        list(map(f, ns))

    if to_zip:
        make_archive(path, 'zip', path)
        rmtree(path)
