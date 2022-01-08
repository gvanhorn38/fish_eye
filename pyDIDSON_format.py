"""
DIDSON and ARIS file and frame header formats
"""

file_attributes_3 = {
    'version': '4s',
    'numframes': 'i',
    'framerate': 'i',
    'resolution': 'i',  # 0=lo 1 = Hi
    'numbeams': 'i',  # 48 Lo 96 Hi for standard mode
    'samplerate': 'f',
    'samplesperchannel': 'i',
    'receivergain': 'i',  # 0-40 dB
    'windowstart': 'i',  # Windowstart 1 to 31 
    'windowlength': 'i',  # Windowlength coded as 0 to 3 
    'reverse': 'i',
    'serialnumber': 'i',
    'date': '32s',  # date file was made
    'idstring': '256s',  # User supplied identification notes
    'id1': 'i',  # four user supplied integers
    'id2': 'i',
    'id3': 'i',
    'id4': 'i',
    'startframe': 'i',  # used if this is a snippet file from source file
    'endframe': 'i',  # Used if this is a snippet file from source file
    'timelapse': 'i',  # Logic 0 or 1 (1 = timelapse active);
    'recordInterval': 'i',  # Ask Bill
    'radioseconds': 'i',  # Needed for timelapse -- ask Bill
    'frameinterval': 'i',  # Interval between frames in time lapse
    'userassigned': '136s',  # User assigned space
}

file_attributes_4 = {
    'version': '4s',
    'numframes': 'i',
    'framerate': 'i',
    'resolution': 'i',  # 0=lo 1 = Hi
    'numbeams': 'i',  # 48 Lo 96 Hi for standard mode
    'samplerate': 'f',
    'samplesperchannel': 'i',
    'receivergain': 'i',  # 0-40 dB
    'windowstart': 'i',  # Windowstart 1 to 31 
    'windowlength': 'i',  # Windowlength coded as 0 to 3 
    'reverse': 'i',
    'serialnumber': 'i',
    'date': '32s',  # date file was made
    'idstring': '256s',  # User supplied identification notes
    'id1': 'i',  # four user supplied integers
    'id2': 'i',
    'id3': 'i',
    'id4': 'i',
    'startframe': 'i',  # used if this is a snippet file from source file
    'endframe': 'i',  # Used if this is a snippet file from source file
    'timelapse': 'i',  # Logic 0 or 1 (1 = timelapse active);
    'recordInterval': 'i',  # Ask Bill
    'radioseconds': 'i',  # Needed for timelapse -- ask Bill
    'frameinterval': 'i',  # Interval between frames in time lapse
    'userassigned': '136s',  # User assigned space
}

file_attributes_5 = {
    'version': '4s',
    'numframes': 'I',  # Total frames in file
    'framerate': 'I',  # Initial recorded frame rate
    'resolution': 'I',  # Non-zero if HF, zero if LF
    'numbeams': 'I',  # ARIS 3000 = 128/64, ARIS 1800 = 96/48, ARIS 1200 = 48
    'samplerate': 'f',  # 1/Sample Period
    'samplesperchannel': 'I',  # Number of range samples in each beam
    'receivergain': 'I',  # Relative gain in dB:  0 - 40
    'windowstart': 'f',  # Image window start range in meters (code [0..31] in DIDSON)
    'windowlength': 'f',  # Image window length in meters  (code [0..3] in DIDSON)
    'reverse': 'I',  # Non-zero = lens down (DIDSON) or lens up (ARIS), zero = opposite
    'serialnumber': 'I',  # Sonar serial number
    'strdate': '32s',  # Date that file was recorded
    'idstring': '256s',  # User input to identify file in 256 characters
    'id1': 'i',  # User-defined integer quantity
    'id2': 'i',  # User-defined integer quantity
    'id3': 'i',  # User-defined integer quantity
    'id4': 'i',  # User-defined integer quantity
    'startframe': 'I',  # First frame number from source file (for DIDSON snippet files)
    'endframe': 'I',  # Last frame number from source file (for DIDSON snippet files)
    'timelapse': 'I',  # Non-zero indicates time lapse recording
    'recordInterval': 'I',  # Number of frames/seconds between recorded frames
    'radioseconds': 'I',  # Frames or seconds interval
    'frameinterval': 'I',  # Record every Nth frame
    'flags': 'I',  # See DDF_04 file format document
    'auxflags': 'I',  # See DDF_04 file format document
    'sspd': 'I',  # Sound velocity in water
    'flags3d': 'I',  # See DDF_04 file format document
    'softwareversion': 'I',  # DIDSON software version that recorded the file
    'watertemperature': 'I',  # Water temperature code:  0 = 5-15C, 1 = 15-25C, 2 = 25-35C
    'salinity': 'I',  # Salinity code:  0 = fresh, 1 = brackish, 2 = salt
    'pulselength': 'I',  # Added for ARIS but not used
    'txmode': 'I',  # Added for ARIS but not used
    'versionfgpa': 'I',  # Reserved for future use
    'versionpsuc': 'I',  # Reserved for future use
    'thumbnailfi': 'I',  # Frame index of frame used for thumbnail image of file
    'filesize': 'Q',  # Total file size in bytes
    'optionalheadersize': 'Q',  # Reserved for future use
    'optionaltailsize': 'Q',  # Reserved for future use
    'versionminor': 'I',  # DIDSON_ADJUSTED_VERSION_MINOR
    'largelens': 'I',  # Non-zero if telephoto lens (large lens, hi-res lens, big lens) is present
    'userassigned': '568s',  # Free space for user
}

frame_attributes_3 = {
    'framenumber': 'i',
    'frametime': 'i',
    'frametime2': 'i',
    'version': '4s',
    'status': 'i',
    'year': 'i',
    'month': 'i',
    'day': 'i',
    'hour': 'i',
    'minute': 'i',
    'second': 'i',
    'hsecond': 'i',
    'transmit': 'i',  # bit2 = 2.0 MHz, bit1 = Enable, bit0 = HF_MODE
    'windowstart': 'i',  # This will be updated at the end of this routine
    'windowlength': 'i',  # Add 2 if low resolution (index between 1 and 6)
    'threshold': 'i',
    'intensity': 'i',
    'receivergain': 'i',
    'degc1': 'i',
    'degc2': 'i',
    'humidity': 'i',
    'focus': 'i',
    'battery': 'i',
    'status1': '16s',  # User defined and supplied
    'status2': '8s',  # User defined and supplied
    'panwcom': 'f',  # Return from Pan/Tilt if used when compass present
    'tiltwcom': 'f',  # Return from Pan/Tilt if used when compass is present
    'velocity': 'f',  # Platform variables supplied by user
    'depth': 'f',
    'altitude': 'f',
    'pitch': 'f',
    'pitchrate': 'f',
    'roll': 'f',
    'rollrate': 'f',
    'heading': 'f',
    'headingrate': 'f',
    'sonarpan': 'f',
    'sonartilt': 'f',  # Read from compass if used, Read from Pan/Tilt if used and no compass
    'sonarroll': 'f',  # Read from compass if used, Read from Pan/Tilt if used and no compass
    'latitude': 'd',
    'longitude': 'd',
    'sonarposition': 'f',
    'configflags': 'i',  # bit0: 1=classic, 0=extended windows; bit1: 0=Standard, 1=LR
    'userassigned': '60s',  # Free space for user
}

frame_attributes_4 = {
    'framenumber': 'i',
    'frametime': 'i',
    'frametime2': 'i',
    'version': '4s',
    'status': 'i',
    'year': 'i',
    'month': 'i',
    'day': 'i',
    'hour': 'i',
    'minute': 'i',
    'second': 'i',
    'hsecond': 'i',
    'transmit': 'i',  # bit2 = 2.0 MHz, bit1 = Enable, bit0 = HF_MODE
    'windowstart': 'i',  # This will be updated at the end of this routine
    'windowlength': 'i',  # Add 2 if low resolution (index between 1 and 6)
    'threshold': 'i',
    'intensity': 'i',
    'receivergain': 'i',
    'degc1': 'i',
    'degc2': 'i',
    'humidity': 'i',
    'focus': 'i',
    'battery': 'i',
    'status1': '16s',  # User defined and supplied
    'status2': '8s',  # User defined and supplied
    'panwcom': 'f',  # Return from Pan/Tilt if used when compass present
    'tiltwcom': 'f',  # Return from Pan/Tilt if used when compass is present
    'velocity': 'f',  # Platform variables supplied by user
    'depth': 'f',
    'altitude': 'f',
    'pitch': 'f',
    'pitchrate': 'f',
    'roll': 'f',
    'rollrate': 'f',
    'heading': 'f',
    'headingrate': 'f',
    'sonarpan': 'f',
    'sonartilt': 'f',  # Read from compass if used, Read from Pan/Tilt if used and no compass
    'sonarroll': 'f',  # Read from compass if used, Read from Pan/Tilt if used and no compass
    'latitude': 'd',
    'longitude': 'd',
    'sonarposition': 'f',
    'configflags': 'i',  # bit0: 1=classic, 0=extended windows; bit1: 0=Standard, 1=LR
    'userassigned': '828s',  # Move pointer to end of frame header of length 1024 bytes
}

frame_attributes_5 = {
    'framenumber': 'I',
    'frametime': 'Q',  # Recording timestamp
    'version': '4s',
    'status': 'I',
    'sonartimestamp': 'Q',
    'tsday': 'I',
    'tshour': 'I',
    'tsminute': 'I',
    'tssecond': 'I',
    'tshsecond': 'I',
    'transmitmode': 'I',
    'windowstart': 'f',
    'windowlength': 'f',
    'threshold': 'I',
    'intensity': 'i',
    'receivergain': 'I',
    'degc1': 'I',
    'degc2': 'I',
    'humidity': 'I',
    'focus': 'I',
    'battery': 'I',
    'uservalue1': 'f',
    'uservalue2': 'f',
    'uservalue3': 'f',
    'uservalue4': 'f',
    'uservalue5': 'f',
    'uservalue6': 'f',
    'uservalue7': 'f',
    'uservalue8': 'f',
    'velocity': 'f',
    'depth': 'f',
    'altitude': 'f',
    'pitch': 'f',
    'pitchrate': 'f',
    'roll': 'f',
    'rollrate': 'f',
    'heading': 'f',
    'headingrate': 'f',
    'compassheading': 'f',
    'compasspitch': 'f',
    'compassroll': 'f',
    'latitude': 'd',
    'longitude': 'd',
    'sonarposition': 'f',
    'configflags': 'I',
    'beamtilt': 'f',
    'targetrange': 'f',
    'targetbearing': 'f',
    'targetpresent': 'I',
    'firmwarerevision': 'I',
    'flags': 'I',
    'sourceframe': 'I',
    'watertemp': 'f',
    'timerperiod': 'I',
    'sonarx': 'f',
    'sonary': 'f',
    'sonarz': 'f',
    'sonarpan': 'f',
    'sonartilt': 'f',
    'sonarroll': 'f',
    'panpnnl': 'f',
    'tiltpnnl': 'f',
    'rollpnnl': 'f',
    'vehicletime': 'd',
    'timeggk': 'f',
    'dateggk': 'I',
    'qualityggk': 'I',
    'numsatsggk': 'I',
    'dopggk': 'f',
    'ehtggk': 'f',
    'heavetss': 'f',
    'yeargps': 'I',
    'monthgps': 'I',
    'daygps': 'I',
    'hourgps': 'I',
    'minutegps': 'I',
    'secondgps': 'I',
    'hsecondgps': 'I',
    'sonarpanoffset': 'f',
    'sonartiltoffset': 'f',
    'sonarrolloffset': 'f',
    'sonarxoffset': 'f',
    'sonaryoffset': 'f',
    'sonarzoffset': 'f',
    'tmatrix': '64s',
    'samplerate': 'f',
    'accellx': 'f',
    'accelly': 'f',
    'accellz': 'f',
    'pingmode': 'I',
    'frequencyhilow': 'I',
    'pulsewidth': 'I',
    'cycleperiod': 'I',
    'sampleperiod': 'I',
    'transmitenable': 'I',
    'framerate': 'f',
    'soundspeed': 'f',
    'samplesperbeam': 'I',
    'enable150v': 'I',
    'samplestartdelay': 'I',
    'largelens': 'I',
    'thesystemtype': 'I',
    'sonarserialnumber': 'I',
    'encryptedkey': 'Q',
    'ariserrorflagsuint': 'I',
    'missedpackets': 'I',
    'arisappversion': 'I',
    'available2': 'I',
    'reorderedsamples': 'I',
    'salinity': 'I',
    'pressure': 'f',
    'batteryvoltage': 'f',
    'mainvoltage': 'f',
    'switchvoltage': 'f',
    'focusmotormoving': 'I',
    'voltagechanging': 'I',
    'focustimeoutfault': 'I',
    'focusovercurrentfault': 'I',
    'focusnotfoundfault': 'I',
    'focusstalledfault': 'I',
    'fpgatimeoutfault': 'I',
    'fpgabusyfault': 'I',
    'fpgastuckfault': 'I',
    'cputempfault': 'I',
    'psutempfault': 'I',
    'watertempfault': 'I',
    'humidityfault': 'I',
    'pressurefault': 'I',
    'voltagereadfault': 'I',
    'voltagewritefault': 'I',
    'focuscurrentposition': 'I',
    'targetpan': 'f',
    'targettilt': 'f',
    'targetroll': 'f',
    'panmotorerrorcode': 'I',
    'tiltmotorerrorcode': 'I',
    'rollmotorerrorcode': 'I',
    'panabsposition': 'f',
    'tiltabsposition': 'f',
    'rollabsposition': 'f',
    'panaccelx': 'f',
    'panaccely': 'f',
    'panaccelz': 'f',
    'tiltaccelx': 'f',
    'tiltaccely': 'f',
    'tiltaccelz': 'f',
    'rollaccelx': 'f',
    'rollaccely': 'f',
    'rollaccelz': 'f',
    'appliedsettings': 'I',
    'constrainedsettings': 'I',
    'invalidsettings': 'I',
    'enableinterpacketdelay': 'I',
    'interpacketdelayperiod': 'I',
    'uptime': 'I',
    'arisappversionmajor': 'H',
    'arisappversionminor': 'H',
    'gotime': 'Q',
    'panvelocity': 'f',
    'tiltvelocity': 'f',
    'rollvelocity': 'f',
    'sentinel': 'I',
    'userassigned': '292s',  # Free space for user
}
