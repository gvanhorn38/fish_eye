"""
Utility functions for converting the beam width header files into
python arrays.

See : https://github.com/SoundMetrics/aris-file-sdk/tree/master/beam-width-metrics

"""

import glob
import os
import re

import pandas as pd

def parse_beam_header_file(fp):
    """ Utility to parse the beam width header files.
    """

    # example of what we are trying to parse:
    # DEFINE_BEAMWIDTH3(0, -13.5735, -13.7893, -13.3577)

    pattern = re.compile(r"^DEFINE_BEAMWIDTH3\D*(\d+), ([-+]?\d*\.\d+), ([-+]?\d*\.\d+), ([-+]?\d*\.\d+)")

    beam_angles = []

    with open(fp) as f:
        for line in f:
            m = pattern.match(line)
            if m:

                beam_num = int(m.group(1))
                beam_center = float(m.group(2))
                beam_left = float(m.group(3))
                beam_right = float(m.group(4))

                beam_angles.append([beam_num, beam_center, beam_left, beam_right])

    # Simple sanity check
    for i in range(len(beam_angles)):
        assert beam_angles[i][0] == i

    beam_angles = pd.DataFrame(beam_angles, columns=['beam_num', 'beam_center', 'beam_left', 'beam_right'])

    return beam_angles


def convert_beam_header_files(beam_dir):
    """ Convert the aris-file-sdk/beam-width-metrics directory to pandas data frames.
    """

    system_beam_angles = {}

    for fp in glob.glob(os.path.join(beam_dir, "BeamWidths*")):

        beam_angles = parse_beam_header_file(fp)
        name = os.path.splitext(os.path.basename(fp))[0]
        system_type = name.split("BeamWidths_")[1]

        system_beam_angles[system_type] = beam_angles

    return system_beam_angles


def make_csv_files_for_beam_widths(beam_dir, output_dir):
    """ Convert the aris-file-sdk/beam-width-metrics directory to pandas data frames
    and save them as csv files.
    """

    system_beam_angles = convert_beam_header_files(beam_dir)

    for system_type, beam_angles in system_beam_angles.items():

        beam_angles.to_csv(os.path.join(output_dir, system_type + ".csv"), index=False)



def load_beam_width_data(frame, beam_width_dir):
    """ Load in the beam spacing file that corresponds to the correct ARIS setup for this frame.
    """

    system_type = frame.thesystemtype
    beam_count = frame.BeamCount
    used_telephoto = frame.largelens

    beam_width_fn = None

    # ARIS 1800
    if system_type == 0:

        if beam_count == 48:

            if used_telephoto:
                # ARIS_Telephoto_48
                beam_width_fn = 'ARIS_Telephoto_48.csv'
            else:
                # ARIS1800_1200_48
                beam_width_fn = 'ARIS1800_1200_48.csv'

        elif beam_count == 96:

            if used_telephoto:
                # ARIS_Telephoto_96
                beam_width_fn = 'ARIS_Telephoto_96.csv'
            else:
                # ARIS1800_96
                beam_width_fn = 'ARIS1800_96.csv'

        else:
            raise ValueEror("Invalid Beam Count %d for ARIS 1800" % (beam_count,))

    # ARIS 3000
    elif system_type == 1:

        if used_telephoto:
            raise ValueEror("Don't know telephoto beam widths for ARIS 3000")

        if beam_count == 64:
            # ARIS3000_64
            beam_width_fn = 'ARIS3000_64.csv'

        elif beam_count == 128:
            # ARIS3000_128
            beam_width_fn = 'ARIS3000_128.csv'

        else:
            raise ValueEror("Invalid Beam Count %d for ARIS 3000" % (beam_count,))

    # ARIS 1200
    elif system_type == 2:

        if beam_count != 48:
            raise ValueEror("Invalid Beam Count %d for ARIS 1200" % (beam_count,))

        if used_telephoto:
            # ARIS_Telephoto_48
            beam_width_fn = 'ARIS_Telephoto_48.csv'
        else:
            # ARIS1800_1200_48
            beam_width_fn = 'ARIS1800_1200_48.csv'

    else:
        raise ValueError("Unknown System Type: %s" % (system_type,))


    beam_width_fp = os.path.join(beam_width_dir, beam_width_fn)

    # return pd.read_csv(beam_width_fp)
    return (pd.read_csv(beam_width_fp), beam_width_fn.replace('.csv', ''))





# /Users/GVH/Code/soundmetrics/aris-file-sdk/beam-width-metrics