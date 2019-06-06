# -*- coding: utf-8 -*-
"""
===================================================
A python interface for ARIS files
===================================================

Last modified on: January 31, 2017
The most recent version can be found at: https://github.com/EminentCodfish/pyARIS

@author: Chris Rillahan
"""

import struct, array, pytz, datetime, tqdm
import subprocess as sp
from matplotlib import cm as colormap
from PIL import Image, ImageFont, ImageDraw
import numpy as np
from beams import load_beam_width_data


class ARIS_File:
    'This is a class container for the ARIS file headers'

    def __init__(self, filename, version_number, FrameCount, FrameRate, HighResolution, NumRawBeams, SampleRate, SamplesPerChannel, ReceiverGain,
                 WindowStart, WindowLength, Reverse, SN, strDate, strHeaderID, UserID1, UserID2, UserID3, UserID4, StartFrame,EndFrame,
                 TimeLapse, RecordInterval, RadioSeconds, FrameInterval, Flags, AuxFlags, Sspd, Flags3D, SoftwareVersion, WaterTemp,
                 Salinity, PulseLength, TxMode, VersionFGPA, VersionPSuC, ThumbnailFI, FileSize, OptionalHeaderSize, OptionalTailSize,
                 VersionMinor, LargeLens):
                     self.filename = filename #Name of the ARIS file
                     self.version_number = version_number #File format version DDF_05 = 0x05464444
                     #OBSOLETE: Calculate the number of frames from file size & beams*samples.
                     self.FrameCount = FrameCount #Total frames in file
                     #OBSOLETE: See frame header instead.
                     self.FrameRate = FrameRate #Initial recorded frame rate
                     #OBSOLETE: See frame header instead.
                     self.HighResolution = HighResolution #Non-zero if HF, zero if LF
                     #OBSOLETE: See frame header instead.
                     self.NumRawBeams = NumRawBeams #ARIS 3000 = 128/64, ARIS 1800 = 96/48, ARIS 1200 = 48
                     #OBSOLETE: See frame header instead.
                     self.SampleRate = SampleRate #1/Sample Period
                     #OBSOLETE: See frame header instead.
                     self.SamplesPerChannel = SamplesPerChannel #Number of range samples in each beam
                     #OBSOLETE: See frame header instead.
                     self.ReceiverGain = ReceiverGain #Relative gain in dB:  0 - 40
                     #OBSOLETE: See frame header instead.
                     self.WindowStart = WindowStart #Image window start range in meters (code [0..31] in DIDSON)
                     #OBSOLETE: See frame header instead.
                     self.WindowLength = WindowLength #Image window length in meters  (code [0..3] in DIDSON)
                     #OBSOLETE: See frame header instead.
                     self.Reverse = Reverse #Non-zero = lens down (DIDSON) or lens up (ARIS), zero = opposite
                     self.SN = SN  #Sonar serial number
                     self.strDate = strDate #Date that file was recorded
                     self.strHeaderID = strHeaderID #User input to identify file in 256 characters
                     self.UserID1 = UserID1 #User-defined integer quantity
                     self.UserID2 = UserID2 #User-defined integer quantity
                     self.UserID3 = UserID3 #User-defined integer quantity
                     self.UserID4 = UserID4 #User-defined integer quantity
                     self.StartFrame = StartFrame #First frame number from source file (for DIDSON snippet files)
                     self.EndFrame = EndFrame #Last frame number from source file (for DIDSON snippet files)
                     self.TimeLapse = TimeLapse #Non-zero indicates time lapse recording
                     self.RecordInterval = RecordInterval #Number of frames/seconds between recorded frames
                     self.RadioSeconds = RadioSeconds #Frames or seconds interval
                     self.FrameInterval = FrameInterval #Record every Nth frame
                     self.Flags = Flags #See DDF_04 file format document (OBSOLETE)
                     self.AuxFlags = AuxFlags #See DDF_04 file format document
                     #OBSOLETE: See frame header instead.
                     self.Sspd = Sspd #Sound velocity in water
                     self.Flags3D = Flags3D #See DDF_04 file format document
                     self.SoftwareVersion = SoftwareVersion #DIDSON software version that recorded the file
                     self.WaterTemp = WaterTemp #Water temperature code:  0 = 5-15C, 1 = 15-25C, 2 = 25-35C
                     self.Salinity = Salinity #Salinity code:  0 = fresh, 1 = brackish, 2 = salt
                     self.PulseLength = PulseLength #Added for ARIS but not used
                     self.TxMode = TxMode #Added for ARIS but not used
                     self.VersionFGPA = VersionFGPA #Reserved for future use
                     self.VersionPSuC = VersionPSuC #Reserved for future use
                     self.ThumbnailFI = ThumbnailFI #Frame index of frame used for thumbnail image of file
                     #OBSOLETE: Do not use; query your filesystem instead.
                     self.FileSize = FileSize #Total file size in bytes
                     self.OptionalHeaderSize = OptionalHeaderSize#Reserved for future use (Obsolete, not used)
                     self.OptionalTailSize = OptionalTailSize #Reserved for future use (Obsolete, not used)
                     self.VersionMinor = VersionMinor #DIDSON_ADJUSTED_VERSION_MINOR (Obsolete)
                     self.LargeLens = LargeLens #Non-zero if telephoto lens (large lens, hi-res lens, big lens) is present

    def __len__(self):
         return self.FrameCount

    def __repr__(self):
        return 'ARIS File: ' + self.filename

    def info(self):
        print('Filename: ' + str(self.filename))
        print('Software Version: ' + str(self.SoftwareVersion))
        print('ARIS S/N: ' + str(self.SN))
        print('File size: ' + str(self.FileSize))
        print('Number of Frames: ' + str(self.FrameCount))
        print('Beam Count: ' + str(self.NumRawBeams))
        print('Samples/Beam: ' + str(self.SamplesPerChannel))

class ARIS_Frame(ARIS_File):
    """This is a class container for the ARIS frame dataPI"""

    def __init__(self, frameindex, frametime, version, status, sonartimestamp, tsday, tshour, tsminute, tssecond, tshsecond, transmitmode,
                 windowstart, windowlength, threshold, intensity, receivergain, degc1, degc2, humidity, focus, battery, uservalue1, uservalue2,
                 uservalue3,  uservalue4,  uservalue5, uservalue6, uservalue7, uservalue8,  velocity, depth, altitude, pitch, pitchrate, roll,
                 rollrate, heading, headingrate, compassheading, compasspitch, compassroll, latitude, longitude, sonarposition, configflags,
                 beamtilt, targetrange, targetbearing, targetpresent, firmwarerevision, flags, sourceframe, watertemp, timerperiod, sonarx,
                 sonary, sonarz, sonarpan, sonartilt, sonarroll, panpnnl, tiltpnnl, rollpnnl, vehicletime, timeggk, dateggk, qualityggk, numsatsggk,
                 dopggk, ehtggk, heavetss, yeargps, monthgps, daygps, hourgps, minutegps, secondgps, hsecondgps, sonarpanoffset, sonartiltoffset,
                 sonarrolloffset, sonarxoffset, sonaryoffset, sonarzoffset, tmatrix, samplerate, accellx, accelly, accellz, pingmode, frequencyhilow,
                 pulsewidth, cycleperiod, sampleperiod, transmitenable, framerate, soundspeed, samplesperbeam, enable150v, samplestartdelay, largelens,
                 thesystemtype, sonarserialnumber, encryptedkey, ariserrorflagsuint, missedpackets, arisappversion, available2, reorderedsamples,
                 salinity, pressure, batteryvoltage, mainvoltage, switchvoltage, focusmotormoving, voltagechanging, focustimeoutfault, focusovercurrentfault,
                 focusnotfoundfault, focusstalledfault, fpgatimeoutfault, fpgabusyfault, fpgastuckfault, cputempfault, psutempfault, watertempfault,
                 humidityfault, pressurefault, voltagereadfault, voltagewritefault, focuscurrentposition, targetpan, targettilt, targetroll, panmotorerrorcode,
                 tiltmotorerrorcode, rollmotorerrorcode, panabsposition, tiltabsposition, rollabsposition, panaccelx, panaccely, panaccelz, tiltaccelx,
                 tiltaccely, tiltaccelz, rollaccelx, rollaccely, rollaccelz, appliedsettings, constrainedsettings, invalidsettings, enableinterpacketdelay,
                 interpacketdelayperiod, uptime, arisappversionmajor, arisappversionminor, gotime, panvelocity, tiltvelocity, rollvelocity, sentinel):

                    self.frameindex = frameindex #Frame number in file
                    self.frametime = frametime #PC time stamp when recorded; microseconds since epoch (Jan 1st 1970)
                    self.version = version #ARIS file format version = 0x05464444
                    self.status = status
                    self.sonartimestamp = sonartimestamp #On-sonar microseconds since epoch (Jan 1st 1970)
                    self.tsday = tsday
                    self.tshour = tshour
                    self.tsminute = tsminute
                    self.tssecond = tssecond
                    self.tshsecond = tshsecond
                    self.transmitmode = transmitmode
                    self.windowstart = windowstart #Window start in meters
                    self.windowlength = windowlength #Window length in meters
                    self.threshold = threshold
                    self.intensity = intensity
                    self.receivergain = receivergain #Note: 0-24 dB
                    self.degc1 = degc1 #CPU temperature (C)
                    self.degc2 = degc2 #Power supply temperature (C)
                    self.humidity = humidity #% relative humidity
                    self.focus = focus #Focus units 0-1000
                    self.battery = battery #OBSOLETE: Unused.
                    self.uservalue1 = uservalue1
                    self.uservalue2 = uservalue2
                    self.uservalue3 = uservalue3
                    self.uservalue4 = uservalue4
                    self.uservalue5 = uservalue5
                    self.uservalue6 = uservalue6
                    self.uservalue7 = uservalue7
                    self.uservalue8 = uservalue8
                    self.velocity = velocity # Platform velocity from AUV integration
                    self.depth = depth # Platform depth from AUV integration
                    self.altitude = altitude # Platform altitude from AUV integration
                    self.pitch = pitch # Platform pitch from AUV integration
                    self.pitchrate = pitchrate # Platform pitch rate from AUV integration
                    self.roll = roll # Platform roll from AUV integration
                    self.rollrate = rollrate # Platform roll rate from AUV integration
                    self.heading = heading # Platform heading from AUV integration
                    self.headingrate = headingrate # Platform heading rate from AUV integration
                    self.compassheading = compassheading # Sonar compass heading output
                    self.compasspitch = compasspitch # Sonar compass pitch output
                    self.compassroll = compassroll # Sonar compass roll output
                    self.latitude = latitude # from auxiliary GPS sensor
                    self.longitude = longitude # from auxiliary GPS sensor
                    self.sonarposition = sonarposition # special for PNNL
                    self.configflags = configflags
                    self.beamtilt = beamtilt
                    self.targetrange = targetrange
                    self.targetbearing = targetbearing
                    self.targetpresent = targetpresent
                    self.firmwarerevision = firmwarerevision #OBSOLETE: Unused.
                    self.flags = flags
                    self.sourceframe = sourceframe # Source file frame number for CSOT output files
                    self.watertemp = watertemp # Water temperature from housing temperature sensor
                    self.timerperiod = timerperiod
                    self.sonarx = sonarx # Sonar X location for 3D processing
                    self.sonary = sonary # Sonar Y location for 3D processing
                    self.sonayz = sonarz # Sonar Z location for 3D processing
                    self.sonarpan = sonarpan # X2 pan output
                    self.sonartilt = sonartilt # X2 tilt output
                    self.sonarroll = sonarroll # X2 roll output                                                                                                                       **** End of DDF_03 frame header data ****
                    self.panpnnl = panpnnl
                    self.tiltpnnl = tiltpnnl
                    self.rollpnnl = rollpnnl
                    self.vehicletime = vehicletime # special for Bluefin Robotics HAUV or other AUV integration
                    self.timeggk = timeggk # GPS output from NMEA GGK message
                    self.dateggk = dateggk # GPS output from NMEA GGK message
                    self.qualityggk = qualityggk # GPS output from NMEA GGK message
                    self.numsatsggk = numsatsggk # GPS output from NMEA GGK message
                    self.dopggk = dopggk # GPS output from NMEA GGK message
                    self.ehtggk = ehtggk # GPS output from NMEA GGK message
                    self.heavetss = heavetss # external sensor
                    self.yeargps = yeargps # GPS year output
                    self.monthgps = monthgps # GPS month output
                    self.daygps = daygps # GPS day output
                    self.hourgps = hourgps # GPS hour output
                    self.minutegps = minutegps # GPS minute output
                    self.secondgps = secondgps # GPS second output
                    self.hsecondgps = hsecondgps # GPS 1/100th second output
                    self.sonarpanoffset = sonarpanoffset # Sonar mount location pan offset for 3D processing
                    self.sonartiltoffset = sonartiltoffset # Sonar mount location tilt offset for 3D processing
                    self.sonarrolloffset = sonarrolloffset # Sonar mount location roll offset for 3D processing
                    self.sonarxoffset = sonarxoffset # Sonar mount location X offset for 3D processing
                    self.sonaryoffset = sonaryoffset # Sonar mount location Y offset for 3D processing
                    self.sonarzoffset = sonarzoffset # Sonar mount location Z offset for 3D processing
                    self.tmatirx = tmatrix # 3D processing transformation matrix
                    self.samplerate = samplerate # Calculated as 1e6/SamplePeriod
                    self.accellx = accellx # X-axis sonar acceleration
                    self.accelly = accelly # Y-axis sonar acceleration
                    self.accellz = accellz # Z-axis sonar acceleration
                    self.pingmode = pingmode # ARIS ping mode [1..12]
                    self.frequencyhilow = frequencyhilow # 1 = HF, 0 = LF
                    self.pulsewidth = pulsewidth # Width of transmit pulse in usec, [4..100]
                    self.cycleperiod = cycleperiod # Ping cycle time in usec, [1802..65535]
                    self.sampleperiod = sampleperiod # Downrange sample rate in usec, [4..100]
                    self.tranmitenable = transmitenable # 1 = Transmit ON, 0 = Transmit OFF
                    self.framerate = framerate # Instantaneous frame rate between frame N and frame N-1
                    self.soundspeed = soundspeed # Sound velocity in water calculated from water temperature and salinity setting
                    self.samplesperbeam = samplesperbeam # Number of downrange samples in each beam
                    self.enable150v = enable150v # 1 = 150V ON (Max Power), 0 = 150V OFF (Min Power, 12V)
                    self.samplestartdelay = samplestartdelay # Delay from transmit until start of sampling (window start) in usec, [930..65535]
                    self.largelens = largelens # 1 = telephoto lens (large lens, big lens, hi-res lens) present
                    self.thesystemtype = thesystemtype # 1 = ARIS 3000, 0 = ARIS 1800, 2 = ARIS 1200
                    self.sonarserialnumber = sonarserialnumber # Sonar serial number as labeled on housing
                    self.encryptedkey = encryptedkey # Reserved for future use
                    self.ariserrorflagsuint = ariserrorflagsuint # Error flag code bits
                    self.missedpackets = missedpackets # Missed packet count for Ethernet statistics reporting
                    self.arisappversion = arisappversion # Version number of ArisApp sending frame data
                    self.available2 = available2 # Reserved for future use
                    self.reorderedsamples = reorderedsamples # 1 = frame data already ordered into [beam,sample] array, 0 = needs reordering
                    self.salinity = salinity # Water salinity code:  0 = fresh, 15 = brackish, 35 = salt
                    self.pressure = pressure # Depth sensor output in meters (psi)
                    self.batteryvoltage = batteryvoltage # Battery input voltage before power steering
                    self.mainvoltage = mainvoltage # Main cable input voltage before power steering
                    self.switchvoltage = switchvoltage # Input voltage after power steering
                    self.focusmotormoving = focusmotormoving # Added 14-Aug-2012 for AutomaticRecording
                    self.voltagechanging = voltagechanging # Added 16-Aug (first two bits = 12V, second two bits = 150V, 00 = not changing, 01 = turning on, 10 = turning off)
                    self.focustimeoutfault = focustimeoutfault
                    self.focusovercurrentfault = focusovercurrentfault
                    self.focusnotfoundfault = focusnotfoundfault
                    self.focusstalledfault = focusstalledfault
                    self.fpgatimeoutfault = fpgatimeoutfault
                    self.fpgabusyfault = fpgabusyfault
                    self.fpgastuckfault = fpgastuckfault
                    self.cputempfault = cputempfault
                    self.psutempfault = psutempfault
                    self.watertempfault = watertempfault
                    self.humidityfault = humidityfault
                    self.pressurefault = pressurefault
                    self.voltagereadfault = voltagereadfault
                    self.voltagewritefault = voltagewritefault
                    self.focuscurrentposition = focuscurrentposition # Focus shaft current position in motor units [0.1000]
                    self.targetpan = targetpan # Commanded pan position
                    self.targettilt = targettilt # Commanded tilt position
                    self.targetroll = targetroll # Commanded roll position
                    self.panmotorerrorcode = panmotorerrorcode
                    self.tiltmotorerrorcode = tiltmotorerrorcode
                    self.rollmotorerrorcode = rollmotorerrorcode
                    self.panabsposition = panabsposition # Low-resolution magnetic encoder absolute pan position
                    self.tiltabsposition = tiltabsposition # Low-resolution magnetic encoder absolute tilt position
                    self.rollabsposition = rollabsposition # Low-resolution magnetic encoder absolute roll position
                    self.panaccelx = panaccelx # Accelerometer outputs from AR2 CPU board sensor
                    self.panaccely = panaccely
                    self.panaccelz = panaccelz
                    self.tiltaccelx = tiltaccelx
                    self.tiltaccely = tiltaccely
                    self.tiltaccelz = tiltaccelz
                    self.rollaccelx = rollaccelx
                    self.rollaccely = rollaccely
                    self.rollccelz = rollaccelz
                    self.appliedsettings = appliedsettings # Cookie indices for command acknowlege in frame header
                    self.constrainedsettings = constrainedsettings
                    self.invalidsettings = invalidsettings
                    self.enableinterpacketdelay = enableinterpacketdelay # If true delay is added between sending out image data packets
                    self.interpacketdelayperiod = interpacketdelayperiod # packet delay factor in us (does not include function overhead time)
                    self.uptime = uptime # Total number of seconds sonar has been running
                    self.arisappverionmajor = arisappversionmajor # Major version number
                    self.arisappversionminor = arisappversionminor # Minor version number
                    self.gotime = gotime # Sonar time when frame cycle is initiated in hardware
                    self.panvelocity = panvelocity # AR2 pan velocity in degrees/second
                    self.tiltvelocity = tiltvelocity # AR2 tilt velocity in degrees/second
                    self.rollvelocity = rollvelocity # AR2 roll velocity in degrees/second
                    self.sentinel = sentinel # Used to measure the frame header size

    def __repr__(self):
        return 'ARIS Frame Number: ' + str(self.frameindex)

    def info(self):
        print('Frame Number: ' + str(self.frameindex))
        print('Frame Time: ' + str(datetime.datetime.fromtimestamp(self.sonartimestamp/1000000, pytz.timezone('UTC')).strftime('%Y-%m-%d %H:%M:%S.%f')))
        print('Frame Rate: ' + str(self.framerate))
        print('Window Start: ' + str(self.windowstart))
        print('Window Length: ' + str(self.windowlength))
        print('Ping Mode: ' + str(self.pingmode))
        print('Frequency: ' + str(self.frequencyhilow))


def DataImport(filename, startFrame = 1, frameBuffer = 0):
    """DataImport reads in the file specified by the filename.  The function populates
    a ARIS_File data structure.  This function then calls the FrameRead() method
    to load a starting frame.

    Parameters
    -----------
    filename    : Input file (*.aris)
    startFrame  : The first frame to be populated into the data structure
    frameBuffer : This parameter is passed into the FrameRead method.  It adds a
        specified number of pixels around the edges of the remapped frame.

    Returns
    -------
    output_data : a ARIS_File data structure
    frame : An ARIS_Frame data structure

    Notes
    -------
    Basic frame attributes can be found by calling the file.info() method.
    A list of all the frames attributes can be found by using dir(file), some
        of these may or may not be used by the ARIS.
    """

    try:
        data = open(filename, 'rb')
    except:
        print('File Error: An error occurred trying to read the file.')
        raise

    #Start reading file header
    version_number      = struct.unpack('I', data.read(4))[0]
    FrameCount          = struct.unpack('I', data.read(4))[0]
    FrameRate           = struct.unpack('I', data.read(4))[0]
    HighResolution      = struct.unpack('I', data.read(4))[0]
    NumRawBeams         = struct.unpack('I', data.read(4))[0]
    SampleRate          = struct.unpack('f', data.read(4))[0]
    SamplesPerChannel   = struct.unpack('I', data.read(4))[0]
    ReceiverGain        = struct.unpack('I', data.read(4))[0]
    WindowStart         = struct.unpack('f', data.read(4))[0]
    WindowLength        = struct.unpack('f', data.read(4))[0]
    Reverse             = struct.unpack('I', data.read(4))[0]
    SN                  = struct.unpack('I', data.read(4))[0]
    strDate             = struct.unpack('32s', data.read(32))[0]
    strHeaderID         = struct.unpack('256s', data.read(256))[0]
    UserID1             = struct.unpack('i', data.read(4))[0]
    UserID2             = struct.unpack('i', data.read(4))[0]
    UserID3             = struct.unpack('i', data.read(4))[0]
    UserID4             = struct.unpack('i', data.read(4))[0]
    StartFrame          = struct.unpack('I', data.read(4))[0]
    EndFrame            = struct.unpack('I', data.read(4))[0]
    TimeLapse           = struct.unpack('I', data.read(4))[0]
    RecordInterval      = struct.unpack('I', data.read(4))[0]
    RadioSeconds        = struct.unpack('I', data.read(4))[0]
    FrameInterval       = struct.unpack('I', data.read(4))[0]
    Flags               = struct.unpack('I', data.read(4))[0]
    AuxFlags            = struct.unpack('I', data.read(4))[0]
    Sspd                = struct.unpack('I', data.read(4))[0]
    Flags3D             = struct.unpack('I', data.read(4))[0]
    SoftwareVersion     = struct.unpack('I', data.read(4))[0]
    WaterTemp           = struct.unpack('I', data.read(4))[0]
    Salinity            = struct.unpack('I', data.read(4))[0]
    PulseLength         = struct.unpack('I', data.read(4))[0]
    TxMode              = struct.unpack('I', data.read(4))[0]
    VersionFGPA         = struct.unpack('I', data.read(4))[0]
    VersionPSuC         = struct.unpack('I', data.read(4))[0]
    ThumbnailFI         = struct.unpack('I', data.read(4))[0]
    FileSize            = struct.unpack('Q', data.read(8))[0]
    OptionalHeaderSize  = struct.unpack('Q', data.read(8))[0]
    OptionalTailSize    = struct.unpack('Q', data.read(8))[0]
    VersionMinor        = struct.unpack('I', data.read(4))[0]
    LargeLens           = struct.unpack('I', data.read(4))[0]

    #Create data structure
    output_data = ARIS_File(filename, version_number, FrameCount, FrameRate, HighResolution, NumRawBeams, SampleRate, SamplesPerChannel, ReceiverGain,
                 WindowStart, WindowLength, Reverse, SN, strDate, strHeaderID, UserID1, UserID2, UserID3, UserID4, StartFrame,EndFrame,
                 TimeLapse, RecordInterval, RadioSeconds, FrameInterval, Flags, AuxFlags, Sspd, Flags3D, SoftwareVersion, WaterTemp,
                 Salinity, PulseLength, TxMode, VersionFGPA, VersionPSuC, ThumbnailFI, FileSize, OptionalHeaderSize, OptionalTailSize,
                 VersionMinor, LargeLens)

    #Close data file
    data.close()

    #Create an empty container for the lookup table
    output_data.LUP = None

    #Load the first frame
    frame = FrameRead(output_data, startFrame)

    #Return the data structure
    return output_data, frame

def FrameRead(ARIS_data, frameIndex, frameBuffer = None):
    """The FrameRead function loads in the specified frame data from the raw ARIS data.
    The function then calls the remapARIS() function which remaps the raw data into
    a 2D real world projection.

    Parameters
    -----------
    ARIS_data : ARIS data structure returned via pyARIS.DataImport()
    frameIndex : frame number
    frameBuffer : This parameter add a specified number of pixels around the edges
                    of the remapped frame.

    Returns
    -------
    output : a frame data structure

    Notes
    -------
    Basic frame attributes can be found by calling the frame.info() method.
    A list of all the frames attributes can be found by using dir(frame), some
        of these may or may not be used by the ARIS.
    """

    FrameSize = ARIS_data.NumRawBeams*ARIS_data.SamplesPerChannel

    frameoffset = (1024+(frameIndex*(1024+(FrameSize))))

    data = open(ARIS_data.filename, 'rb')
    data.seek(frameoffset, 0)

    frameindex          = struct.unpack('I', data.read(4))[0] #Frame number in file
    frametime           = struct.unpack('Q', data.read(8))[0] #PC time stamp when recorded; microseconds since epoch (Jan 1st 1970)
    version             = struct.unpack('I', data.read(4))[0] #ARIS file format version = 0x05464444
    status              = struct.unpack('I', data.read(4))[0]
    sonartimestamp      = struct.unpack('Q', data.read(8))[0] #On-sonar microseconds since epoch (Jan 1st 1970)
    tsday               = struct.unpack('I', data.read(4))[0]
    tshour              = struct.unpack('I', data.read(4))[0]
    tsminute            = struct.unpack('I', data.read(4))[0]
    tssecond            = struct.unpack('I', data.read(4))[0]
    tshsecond           = struct.unpack('I', data.read(4))[0]
    transmitmode        = struct.unpack('I', data.read(4))[0]
    windowstart         = struct.unpack('f', data.read(4))[0] #Window start in meters
    windowlength        = struct.unpack('f', data.read(4))[0] #Window length in meters
    threshold           = struct.unpack('I', data.read(4))[0]
    intensity           = struct.unpack('i', data.read(4))[0]
    receivergain        = struct.unpack('I', data.read(4))[0] #Note: 0-24 dB
    degc1               = struct.unpack('I', data.read(4))[0] #CPU temperature (C)
    degc2               = struct.unpack('I', data.read(4))[0] #Power supply temperature (C)
    humidity            = struct.unpack('I', data.read(4))[0] #% relative humidity
    focus               = struct.unpack('I', data.read(4))[0] #Focus units 0-1000
    battery             = struct.unpack('I', data.read(4))[0] #OBSOLETE: Unused.
    uservalue1          = struct.unpack('f', data.read(4))[0]
    uservalue2          = struct.unpack('f', data.read(4))[0]
    uservalue3          = struct.unpack('f', data.read(4))[0]
    uservalue4          = struct.unpack('f', data.read(4))[0]
    uservalue5          = struct.unpack('f', data.read(4))[0]
    uservalue6          = struct.unpack('f', data.read(4))[0]
    uservalue7          = struct.unpack('f', data.read(4))[0]
    uservalue8          = struct.unpack('f', data.read(4))[0]
    velocity            = struct.unpack('f', data.read(4))[0] # Platform velocity from AUV integration
    depth               = struct.unpack('f', data.read(4))[0] # Platform depth from AUV integration
    altitude            = struct.unpack('f', data.read(4))[0] # Platform altitude from AUV integration
    pitch               = struct.unpack('f', data.read(4))[0] # Platform pitch from AUV integration
    pitchrate           = struct.unpack('f', data.read(4))[0] # Platform pitch rate from AUV integration
    roll                = struct.unpack('f', data.read(4))[0] # Platform roll from AUV integration
    rollrate            = struct.unpack('f', data.read(4))[0] # Platform roll rate from AUV integration
    heading             = struct.unpack('f', data.read(4))[0] # Platform heading from AUV integration
    headingrate         = struct.unpack('f', data.read(4))[0] # Platform heading rate from AUV integration
    compassheading      = struct.unpack('f', data.read(4))[0] # Sonar compass heading output
    compasspitch        = struct.unpack('f', data.read(4))[0] # Sonar compass pitch output
    compassroll         = struct.unpack('f', data.read(4))[0] # Sonar compass roll output
    latitude            = struct.unpack('d', data.read(8))[0] # from auxiliary GPS sensor
    longitude           = struct.unpack('d', data.read(8))[0] # from auxiliary GPS sensor
    sonarposition       = struct.unpack('f', data.read(4))[0] # special for PNNL
    configflags         = struct.unpack('I', data.read(4))[0]
    beamtilt            = struct.unpack('f', data.read(4))[0]
    targetrange         = struct.unpack('f', data.read(4))[0]
    targetbearing       = struct.unpack('f', data.read(4))[0]
    targetpresent       = struct.unpack('I', data.read(4))[0]
    firmwarerevision    = struct.unpack('I', data.read(4))[0] #OBSOLETE: Unused.
    flags               = struct.unpack('I', data.read(4))[0]
    sourceframe         = struct.unpack('I', data.read(4))[0] # Source file frame number for CSOT output files
    watertemp           = struct.unpack('f', data.read(4))[0] # Water temperature from housing temperature sensor
    timerperiod         = struct.unpack('I', data.read(4))[0]
    sonarx              = struct.unpack('f', data.read(4))[0] # Sonar X location for 3D processing
    sonary              = struct.unpack('f', data.read(4))[0] # Sonar Y location for 3D processing
    sonarz              = struct.unpack('f', data.read(4))[0] # Sonar Z location for 3D processing
    sonarpan            = struct.unpack('f', data.read(4))[0] # X2 pan output
    sonartilt           = struct.unpack('f', data.read(4))[0] # X2 tilt output
    sonarroll           = struct.unpack('f', data.read(4))[0] # X2 roll output                                                                                                                       **** End of DDF_03 frame header data ****
    panpnnl             = struct.unpack('f', data.read(4))[0]
    tiltpnnl            = struct.unpack('f', data.read(4))[0]
    rollpnnl            = struct.unpack('f', data.read(4))[0]
    vehicletime         = struct.unpack('d', data.read(8))[0] # special for Bluefin Robotics HAUV or other AUV integration
    timeggk             = struct.unpack('f', data.read(4))[0] # GPS output from NMEA GGK message
    dateggk             = struct.unpack('I', data.read(4))[0] # GPS output from NMEA GGK message
    qualityggk          = struct.unpack('I', data.read(4))[0] # GPS output from NMEA GGK message
    numsatsggk          = struct.unpack('I', data.read(4))[0] # GPS output from NMEA GGK message
    dopggk              = struct.unpack('f', data.read(4))[0] # GPS output from NMEA GGK message
    ehtggk              = struct.unpack('f', data.read(4))[0] # GPS output from NMEA GGK message
    heavetss            = struct.unpack('f', data.read(4))[0] # external sensor
    yeargps             = struct.unpack('I', data.read(4))[0] # GPS year output
    monthgps            = struct.unpack('I', data.read(4))[0] # GPS month output
    daygps              = struct.unpack('I', data.read(4))[0] # GPS day output
    hourgps             = struct.unpack('I', data.read(4))[0] # GPS hour output
    minutegps           = struct.unpack('I', data.read(4))[0] # GPS minute output
    secondgps           = struct.unpack('I', data.read(4))[0] # GPS second output
    hsecondgps          = struct.unpack('I', data.read(4))[0] # GPS 1/100th second output
    sonarpanoffset      = struct.unpack('f', data.read(4))[0] # Sonar mount location pan offset for 3D processing
    sonartiltoffset     = struct.unpack('f', data.read(4))[0] # Sonar mount location tilt offset for 3D processing
    sonarrolloffset     = struct.unpack('f', data.read(4))[0] # Sonar mount location roll offset for 3D processing
    sonarxoffset        = struct.unpack('f', data.read(4))[0] # Sonar mount location X offset for 3D processing
    sonaryoffset        = struct.unpack('f', data.read(4))[0] # Sonar mount location Y offset for 3D processing
    sonarzoffset        = struct.unpack('f', data.read(4))[0] # Sonar mount location Z offset for 3D processing
    tmatrix = array.array('f')                                # 3D processing transformation matrix
    for i in range(16):
        tmatrix.append(struct.unpack('f', data.read(4))[0])
    samplerate          = struct.unpack('f', data.read(4))[0] # Calculated as 1e6/SamplePeriod
    accellx             = struct.unpack('f', data.read(4))[0] # X-axis sonar acceleration
    accelly             = struct.unpack('f', data.read(4))[0] # Y-axis sonar acceleration
    accellz             = struct.unpack('f', data.read(4))[0] # Z-axis sonar acceleration
    pingmode            = struct.unpack('I', data.read(4))[0] # ARIS ping mode [1..12]
    frequencyhilow      = struct.unpack('I', data.read(4))[0] # 1 = HF, 0 = LF
    pulsewidth          = struct.unpack('I', data.read(4))[0] # Width of transmit pulse in usec, [4..100]
    cycleperiod         = struct.unpack('I', data.read(4))[0] # Ping cycle time in usec, [1802..65535]
    sampleperiod        = struct.unpack('I', data.read(4))[0] # Downrange sample rate in usec, [4..100]
    transmitenable      = struct.unpack('I', data.read(4))[0] # 1 = Transmit ON, 0 = Transmit OFF
    framerate           = struct.unpack('f', data.read(4))[0] # Instantaneous frame rate between frame N and frame N-1
    soundspeed          = struct.unpack('f', data.read(4))[0] # Sound velocity in water calculated from water temperature and salinity setting
    samplesperbeam      = struct.unpack('I', data.read(4))[0] # Number of downrange samples in each beam
    enable150v          = struct.unpack('I', data.read(4))[0] # 1 = 150V ON (Max Power), 0 = 150V OFF (Min Power, 12V)
    samplestartdelay    = struct.unpack('I', data.read(4))[0] # Delay from transmit until start of sampling (window start) in usec, [930..65535]
    largelens           = struct.unpack('I', data.read(4))[0] # 1 = telephoto lens (large lens, big lens, hi-res lens) present
    thesystemtype       = struct.unpack('I', data.read(4))[0] # 1 = ARIS 3000, 0 = ARIS 1800, 2 = ARIS 1200
    sonarserialnumber   = struct.unpack('I', data.read(4))[0] # Sonar serial number as labeled on housing
    encryptedkey        = struct.unpack('Q', data.read(8))[0] # Reserved for future use
    ariserrorflagsuint  = struct.unpack('I', data.read(4))[0] # Error flag code bits
    missedpackets       = struct.unpack('I', data.read(4))[0] # Missed packet count for Ethernet statistics reporting
    arisappversion      = struct.unpack('I', data.read(4))[0] # Version number of ArisApp sending frame data
    available2          = struct.unpack('I', data.read(4))[0] # Reserved for future use
    reorderedsamples    = struct.unpack('I', data.read(4))[0] # 1 = frame data already ordered into [beam,sample] array, 0 = needs reordering
    salinity            = struct.unpack('I', data.read(4))[0] # Water salinity code:  0 = fresh, 15 = brackish, 35 = salt
    pressure            = struct.unpack('f', data.read(4))[0] # Depth sensor output in meters (psi)
    batteryvoltage      = struct.unpack('f', data.read(4))[0] # Battery input voltage before power steering
    mainvoltage         = struct.unpack('f', data.read(4))[0] # Main cable input voltage before power steering
    switchvoltage       = struct.unpack('f', data.read(4))[0] # Input voltage after power steering
    focusmotormoving    = struct.unpack('I', data.read(4))[0] # Added 14-Aug-2012 for AutomaticRecording
    voltagechanging     = struct.unpack('I', data.read(4))[0] # Added 16-Aug (first two bits = 12V, second two bits = 150V, 00 = not changing, 01 = turning on, 10 = turning off)
    focustimeoutfault   = struct.unpack('I', data.read(4))[0]
    focusovercurrentfault = struct.unpack('I', data.read(4))[0]
    focusnotfoundfault  = struct.unpack('I', data.read(4))[0]
    focusstalledfault   = struct.unpack('I', data.read(4))[0]
    fpgatimeoutfault    = struct.unpack('I', data.read(4))[0]
    fpgabusyfault       = struct.unpack('I', data.read(4))[0]
    fpgastuckfault      = struct.unpack('I', data.read(4))[0]
    cputempfault        = struct.unpack('I', data.read(4))[0]
    psutempfault        = struct.unpack('I', data.read(4))[0]
    watertempfault      = struct.unpack('I', data.read(4))[0]
    humidityfault       = struct.unpack('I', data.read(4))[0]
    pressurefault       = struct.unpack('I', data.read(4))[0]
    voltagereadfault    = struct.unpack('I', data.read(4))[0]
    voltagewritefault   = struct.unpack('I', data.read(4))[0]
    focuscurrentposition = struct.unpack('I', data.read(4))[0] # Focus shaft current position in motor units [0.1000]
    targetpan           = struct.unpack('f', data.read(4))[0] # Commanded pan position
    targettilt          = struct.unpack('f', data.read(4))[0] # Commanded tilt position
    targetroll          = struct.unpack('f', data.read(4))[0] # Commanded roll position
    panmotorerrorcode   = struct.unpack('I', data.read(4))[0]
    tiltmotorerrorcode  = struct.unpack('I', data.read(4))[0]
    rollmotorerrorcode  = struct.unpack('I', data.read(4))[0]
    panabsposition      = struct.unpack('f', data.read(4))[0] # Low-resolution magnetic encoder absolute pan position
    tiltabsposition     = struct.unpack('f', data.read(4))[0] # Low-resolution magnetic encoder absolute tilt position
    rollabsposition     = struct.unpack('f', data.read(4))[0] # Low-resolution magnetic encoder absolute roll position
    panaccelx           = struct.unpack('f', data.read(4))[0] # Accelerometer outputs from AR2 CPU board sensor
    panaccely           = struct.unpack('f', data.read(4))[0]
    panaccelz           = struct.unpack('f', data.read(4))[0]
    tiltaccelx          = struct.unpack('f', data.read(4))[0]
    tiltaccely          = struct.unpack('f', data.read(4))[0]
    tiltaccelz          = struct.unpack('f', data.read(4))[0]
    rollaccelx          = struct.unpack('f', data.read(4))[0]
    rollaccely          = struct.unpack('f', data.read(4))[0]
    rollaccelz          = struct.unpack('f', data.read(4))[0]
    appliedsettings     = struct.unpack('I', data.read(4))[0] # Cookie indices for command acknowlege in frame header
    constrainedsettings = struct.unpack('I', data.read(4))[0]
    invalidsettings     = struct.unpack('I', data.read(4))[0]
    enableinterpacketdelay = struct.unpack('I', data.read(4))[0] # If true delay is added between sending out image data packets
    interpacketdelayperiod = struct.unpack('I', data.read(4))[0] # packet delay factor in us (does not include function overhead time)
    uptime              = struct.unpack('I', data.read(4))[0] # Total number of seconds sonar has been running
    arisappversionmajor = struct.unpack('H', data.read(2))[0] # Major version number
    arisappversionminor = struct.unpack('H', data.read(2))[0] # Minor version number
    gotime              = struct.unpack('Q', data.read(8))[0] # Sonar time when frame cycle is initiated in hardware
    panvelocity         = struct.unpack('f', data.read(4))[0] # AR2 pan velocity in degrees/second
    tiltvelocity        = struct.unpack('f', data.read(4))[0] # AR2 tilt velocity in degrees/second
    rollvelocity        = struct.unpack('f', data.read(4))[0] # AR2 roll velocity in degrees/second
    sentinel            = struct.unpack('I', data.read(4))[0] # Used to measure the frame header size

    #Create the ARIS_frame data structure and add the meta-data
    output = ARIS_Frame(frameindex, frametime, version, status, sonartimestamp, tsday, tshour, tsminute, tssecond, tshsecond, transmitmode,
                 windowstart, windowlength, threshold, intensity, receivergain, degc1, degc2, humidity, focus, battery, uservalue1, uservalue2,
                 uservalue3,  uservalue4,  uservalue5, uservalue6, uservalue7, uservalue8,  velocity, depth, altitude, pitch, pitchrate, roll,
                 rollrate, heading, headingrate, compassheading, compasspitch, compassroll, latitude, longitude, sonarposition, configflags,
                 beamtilt, targetrange, targetbearing, targetpresent, firmwarerevision, flags, sourceframe, watertemp, timerperiod, sonarx,
                 sonary, sonarz, sonarpan, sonartilt, sonarroll, panpnnl, tiltpnnl, rollpnnl, vehicletime, timeggk, dateggk, qualityggk, numsatsggk,
                 dopggk, ehtggk, heavetss, yeargps, monthgps, daygps, hourgps, minutegps, secondgps, hsecondgps, sonarpanoffset, sonartiltoffset,
                 sonarrolloffset, sonarxoffset, sonaryoffset, sonarzoffset, tmatrix, samplerate, accellx, accelly, accellz, pingmode, frequencyhilow,
                 pulsewidth, cycleperiod, sampleperiod, transmitenable, framerate, soundspeed, samplesperbeam, enable150v, samplestartdelay, largelens,
                 thesystemtype, sonarserialnumber, encryptedkey, ariserrorflagsuint, missedpackets, arisappversion, available2, reorderedsamples,
                 salinity, pressure, batteryvoltage, mainvoltage, switchvoltage, focusmotormoving, voltagechanging, focustimeoutfault, focusovercurrentfault,
                 focusnotfoundfault, focusstalledfault, fpgatimeoutfault, fpgabusyfault, fpgastuckfault, cputempfault, psutempfault, watertempfault,
                 humidityfault, pressurefault, voltagereadfault, voltagewritefault, focuscurrentposition, targetpan, targettilt, targetroll, panmotorerrorcode,
                 tiltmotorerrorcode, rollmotorerrorcode, panabsposition, tiltabsposition, rollabsposition, panaccelx, panaccely, panaccelz, tiltaccelx,
                 tiltaccely, tiltaccelz, rollaccelx, rollaccely, rollaccelz, appliedsettings, constrainedsettings, invalidsettings, enableinterpacketdelay,
                 interpacketdelayperiod, uptime, arisappversionmajor, arisappversionminor, gotime, panvelocity, tiltvelocity, rollvelocity, sentinel)


    #Add the frame data
    if pingmode in [1,2]:
        ARIS_Frame.BeamCount = 48
    if pingmode in [3,4,5]:
        ARIS_Frame.BeamCount = 96
    if pingmode in [6,7,8]:
        ARIS_Frame.BeamCount = 64
    if pingmode in [9,10,11,12]:
        ARIS_Frame.BeamCount = 128

    data.seek(frameoffset+1024, 0)
    frame = np.empty([samplesperbeam, ARIS_Frame.BeamCount], dtype=float)
    for r in range(len(frame)):
        for c in range(len(frame[r])):
            frame[r][c] = struct.unpack('B', data.read(1))[0]
    frame = np.fliplr(frame)

    #Remap the data from 0-255 to 0-80 dB
    #remap = lambda t: (t * 80)/255
    #vfunc = np.vectorize(remap)
    #frame = vfunc(frame)

    output.frame_data = frame
    output.WinStart = output.samplestartdelay * 0.000001 * output.soundspeed / 2

    #Close the data file
    data.close()

    return output


def get_box_for_sample(beam_num, bin_num, frame, beam_data):
    """ Get the box coordinates (in meters) for a sample.
    This is a non-axis aligned box.
    Returns:
        back left, back right, front right, front left
    """

    sample_start_delay = frame.samplestartdelay # usec
    sound_speed = frame.soundspeed # meters / sec
    sample_period = frame.sampleperiod # usec

    WindowStart = sample_start_delay * 1e-6 * sound_speed / 2 # meters
    sample_length = sample_period * 1e-6 * sound_speed / 2. # meters

    bin_front_edge_distance = WindowStart + sample_length * bin_num
    bin_back_edge_distance = WindowStart + sample_length* (bin_num + 1)

    beam_angles = beam_data[beam_data['beam_num'] == beam_num]
    a1 = beam_angles['beam_left'].iloc[0]
    a2 = beam_angles['beam_right'].iloc[0]
    c = beam_angles['beam_center'].iloc[0]

    # I can't figure out whats going on with the beam spacing in the files.
    # Once the center point crosses 0, the ordering of the left and right angles swap...
    # For now I'll assume the y axis is the common line. Positive angles go to the left,
    # negative angles go to the right
    left = max(a1, a2)
    right = min(a1, a2)

    # Left Edge
    beam_left_angle = np.deg2rad(left)
    rot_matrix = np.array([[np.cos(beam_left_angle), -np.sin(beam_left_angle)], [np.sin(beam_left_angle), np.cos(beam_left_angle)]])

    vec = np.array([0, bin_back_edge_distance])
    bin_left_back_point = np.matmul(rot_matrix, vec)

    vec = np.array([0, bin_front_edge_distance])
    bin_left_front_point = np.matmul(rot_matrix, vec)

    # Right Edge
    beam_right_angle = np.deg2rad(right)
    rot_matrix = np.array([[np.cos(beam_right_angle), -np.sin(beam_right_angle)], [np.sin(beam_right_angle), np.cos(beam_right_angle)]])

    vec = np.array([0, bin_front_edge_distance])
    bin_right_front_point = np.matmul(rot_matrix, vec)

    vec = np.array([0, bin_back_edge_distance])
    bin_right_back_point = np.matmul(rot_matrix, vec)


    return bin_left_back_point, bin_right_back_point, bin_right_front_point, bin_left_front_point


def xy_to_sample(x, y, frame, beam_data):
    """ Convert an x,y location (in meters) to a beam sample.
    Returns:
        beam num
        bin num
    """

    # Get the angle
    angle = np.rad2deg(np.arctan(x / y))

    beam_num = beam_data[(beam_data['beam_left'] <= angle) & (angle <= beam_data['beam_right'])]

    if beam_num.shape[0] == 0:
        return None, None

    beam_num = beam_num['beam_num'].iloc[0]

    # Get the distance
    hyp =  y / np.cos(np.arctan(x / y))

    # Take into account the window start
    hyp -= frame.WinStart

    # Sample length
    bin_length = frame.sampleperiod * 0.000001 * frame.soundspeed / 2.

    # Convert to bins
    bin_num = int(hyp / bin_length)

    if bin_num < 0 or bin_num > (frame.BeamCount - 1):
        return None, None

    return beam_num, bin_num


def get_minimum_pixel_meter_size(frame, beam_width_data):
    """ Compute the smallest pixel size that will bound a sample.
    """

    all_widths = []
    all_heights = []

    for beam_num in range(frame.BeamCount):
        bl, br, fr, fl = get_box_for_sample(beam_num, 0, frame, beam_width_data)

        # determine the axis aligned box around this sample box.
        xs = [bl[0], br[0], fr[0], fl[0]]
        ys = [bl[1], br[1], fr[1], fl[1]]
        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)

        width = max_x - min_x
        height = max_y - min_y

        all_widths.append(width)
        all_heights.append(height)

    min_width = min(all_widths)
    min_height = min(all_heights)

    return min(min_width, min_height)

def compute_image_bounds(pixel_meter_size, frame, beam_width_data, additional_pixel_padding_x=0, additional_pixel_padding_y=0):
    """ Given the size of a pixel in meters, compute the bounds of an image that will contain the frame.
    """

    # Compute the projected locations of all samples so that we can get the extent
    all_bl = []
    all_br = []
    all_fr = []
    all_fl = []

    for beam_num in [0, frame.BeamCount / 2, frame.BeamCount - 1]:
        for bin_num in  [0, frame.samplesperbeam - 1]:
            bl, br, fr, fl = get_box_for_sample(beam_num, bin_num, frame, beam_width_data)

            all_bl.append(bl)
            all_br.append(br)
            all_fr.append(fr)
            all_fl.append(fl)

    all_bl = np.array(all_bl)
    all_br = np.array(all_br)
    all_fr = np.array(all_fr)
    all_fl = np.array(all_fl)

    # Get the xdim extent
    min_back_left = np.min(all_bl[:,0])
    min_back_right = np.min(all_br[:,0])
    min_front_left = np.min(all_fl[:,0])
    min_front_right = np.min(all_fr[:,0])
    assert min_back_left < min_back_right
    assert min_back_left < min_front_left
    assert min_back_left < min_front_right

    max_back_left = np.max(all_bl[:,0])
    max_back_right = np.max(all_br[:,0])
    max_front_left = np.max(all_fl[:,0])
    max_front_right = np.max(all_fr[:,0])
    assert max_back_right > max_back_left
    assert max_back_right > max_front_left
    assert max_back_right > max_front_right

    xdim_extent = np.array([min_back_left, max_back_right])


    # Get the ydim extent
    min_back_left = np.min(all_bl[:,1])
    min_back_right = np.min(all_br[:,1])
    min_front_left = np.min(all_fl[:,1])
    min_front_right = np.min(all_fr[:,1])
    min_front = min(min_front_left, min_front_right)
    assert min_front < min_back_right
    assert min_front < min_back_left


    max_back_left = np.max(all_bl[:,1])
    max_back_right = np.max(all_br[:,1])
    max_front_left = np.max(all_fl[:,1])
    max_front_right = np.max(all_fr[:,1])
    max_back = max(max_back_left, max_back_right)
    assert max_back > max_front_right
    assert max_back > max_front_left

    ydim_extent = np.array([min_front, max_back])

    # Determine which meter location corresponds to our "target center"
    bl, br, fr, fl = get_box_for_sample(frame.BeamCount / 2, 0, frame, beam_width_data)
    target_center_x = (fl[0] + fr[0]) / 2.
    target_center_y = (bl[1] + fl[1]) / 2.

    # Determine the x dimension size and what this corresponds to in meters
    extra_padding_x = pixel_meter_size + pixel_meter_size * additional_pixel_padding_x

    # X Min
    xmin_len = target_center_x - xdim_extent[0]
    xp = xmin_len % pixel_meter_size
    xmin_padded = xdim_extent[0] - (extra_padding_x - xp)
    xmin_len = target_center_x - xmin_padded
    x_min_cells = np.abs(xmin_len / pixel_meter_size)
    x_min_meters = target_center_x - xmin_len
    assert x_min_meters <= xdim_extent[0]


    # X Max
    xmax_len = xdim_extent[1] - target_center_x
    xp = xmax_len % pixel_meter_size
    xmax_padded = xdim_extent[1] + (extra_padding_x - xp)
    xmax_len = xmax_padded - target_center_x
    x_max_cells = np.abs(xmax_len / pixel_meter_size)
    x_max_meters = target_center_x + xmax_len
    assert x_max_meters >= xdim_extent[1]


    # if we want a specific beam to be the in the middle of the image then we should take the max?
    xdim = int(x_min_cells + x_max_cells)
    x_meter_start = x_min_meters
    x_meter_stop = x_max_meters

    # Determine the y dimension size and what this corresponds to in meters
    extra_padding_y = pixel_meter_size + pixel_meter_size * additional_pixel_padding_y

    # Y Min
    ymin_len = target_center_y - ydim_extent[0]
    yp = ymin_len % pixel_meter_size
    ymin_padded = ydim_extent[0] - ( extra_padding_y - yp)
    ymin_len = target_center_y - ymin_padded
    y_min_cells = np.abs(ymin_len / pixel_meter_size)
    y_min_meters = target_center_y - ymin_len
    assert y_min_meters <= ydim_extent[0]

    # Y Max
    ymax_len = ydim_extent[1] - target_center_y
    yp = ymax_len % pixel_meter_size
    ymax_padded = ydim_extent[1] + (extra_padding_y - yp)
    ymax_len = ymax_padded - target_center_y
    y_max_cells = np.abs(ymax_len / pixel_meter_size)
    y_max_meters = target_center_y + ymax_len
    assert y_max_meters >= ydim_extent[1]

    ydim = int(y_min_cells + y_max_cells)
    y_meter_start = y_max_meters
    y_meter_stop = y_min_meters

    return xdim, ydim, x_meter_start, y_meter_start, x_meter_stop, y_meter_stop


def compute_mapping_from_sample_to_image(pixel_meter_size, xdim, ydim, x_meter_start, y_meter_start, frame, beam_width_data):

    x_meter_values = np.array([x_meter_start + i * pixel_meter_size for i in range(xdim)])
    y_meter_values = np.array([y_meter_start - i * pixel_meter_size for i in range(ydim)])

    YY, XX = np.meshgrid(y_meter_values, x_meter_values, indexing='ij')
    XYpairs = np.vstack([ XX.reshape(-1), YY.reshape(-1) ]).T

    II, JJ = np.meshgrid(np.arange(ydim), np.arange(xdim), indexing='ij')
    IJpairs = np.vstack([ II.reshape(-1), JJ.reshape(-1)]).T

    # Get the angle of the xy pairs
    angles = np.rad2deg(np.arctan(XYpairs[:,0] / XYpairs[:,1]))

    # Discard pairs that have an angle that is out of range
    min_angle = beam_width_data['beam_left'].min()
    max_angle = beam_width_data['beam_right'].max()
    valid_pairs = (angles > min_angle) & (angles < max_angle)
    angles = angles[valid_pairs]
    XYpairs = XYpairs[valid_pairs]
    IJpairs = IJpairs[valid_pairs]

    # Get the distance of the xy paris
    hyp =  XYpairs[:,1] / np.cos(np.arctan(XYpairs[:,0] / XYpairs[:,1]))

    # Take into account the window start
    hyp -= frame.WinStart

    # Sample length
    bin_length = frame.sampleperiod * 0.000001 * frame.soundspeed / 2.

    # Convert to bins
    bin_nums = (hyp / bin_length).astype(np.int)

    # Discard pairs that have a distance that is out of range
    valid_pairs = (bin_nums >= 0) & (bin_nums < frame.samplesperbeam)
    bin_nums = bin_nums[valid_pairs]
    angles = angles[valid_pairs]
    XYpairs = XYpairs[valid_pairs]
    IJpairs = IJpairs[valid_pairs]


    beam_edges = beam_width_data['beam_left'].to_numpy()
    beam_nums = np.digitize(angles, beam_edges) - 1

    # For each valid x,y pair compute which beam it falls into
    write_to = [] # (i, j) of image
    read_from = [] # (bin_num, beam_num) of frame data
    for index in range(XYpairs.shape[0]):

        bin_num = bin_nums[index]
        beam_num = beam_nums[index]

        write_to.append(IJpairs[index])
        read_from.append((bin_num, beam_num))

    read_from = np.array(read_from)
    read_from_rows = np.array(read_from[:,0])
    read_from_cols = np.array(read_from[:,1])

    write_to = np.array(write_to)
    write_to_rows = np.array(write_to[:,0])
    write_to_cols = np.array(write_to[:,1])

    return read_from_rows, read_from_cols, write_to_rows, write_to_cols


def make_video(data,
    xdim, ydim, sample_read_rows, sample_read_cols, image_write_rows, image_write_cols,
    filename, fps = 24.0, start_frame = 1, end_frame = None, timestamp = False, fontsize = 30, ts_pos = (0,0)):
    """Output video using the ffmpeg pipeline. The current implementation
    outputs compresses png files and outputs a mp4.

    Parameters
    -----------
    data : (Str) ARIS data structure returned via pyARIS.DataImport()
    filename : (Str) output filename.  Must include file extension (i.e. 'video.mp4')
    fps : (Float) Output video frame rate (frames per second). Default = 24 fps
    start_frame, end_frame : (Int) Range of frames included in the output video
    timestamp : (Bool) Add the timestamp from the sonar to the video frames
    fontsize : (Int) Size of timestamp font
    ts_pos : (Tuple) (x,y) location of the timestamp

    Returns
    -------
    Returns a video into the current working directory

    Notes
    ------
    Currently this function looks for ffmpeg.exe in the current working directory.
    Must have the '*.mp4' file extension.
    Uses the tqdm package to display a status bar.

    Example
    -------
    >>> pyARIS.VideoExport(data, 'test_video.mp4', fps = 24)

    """

    #Command to send via the command prompt which specifies the pipe parameters
    command = ['ffmpeg',
           '-y', # (optional) overwrite output file if it exists
           '-f', 'image2pipe',
           '-vcodec', 'png', #'mjpeg',
           '-r', '1',
           '-r', str(fps), # frames per second
           '-i', '-', # The input comes from a pipe
           '-an', # Tells FFMPEG not to expect any audio
           '-vcodec', 'mpeg4',
           '-b:v', '5000k',
           filename,
           '-hide_banner',
           '-loglevel', 'panic']

    #Open the pipe
    pipe = sp.Popen(command, stdin=sp.PIPE)

    if end_frame == None:
        end_frame = data.FrameCount


    cm = colormap.get_cmap('viridis')

    #Iterate through the dataframes and push to pipe
    font = ImageFont.truetype("./arial.ttf", fontsize)
    for i in tqdm.tqdm(range(start_frame, end_frame)):
        frame = FrameRead(data, i)
        frame_image = np.zeros([ydim, xdim], dtype=np.uint8)
        frame_image[image_write_rows, image_write_cols] = frame.frame_data[sample_read_rows, sample_read_cols]
        im = Image.fromarray(cm(frame_image, bytes=True))

        if timestamp == True:
            ts = str(datetime.datetime.fromtimestamp(frame.sonartimestamp/1000000, pytz.timezone('UTC')).strftime('%Y-%m-%d %H:%M:%S'))
            text = "%s\n%d" % (ts, i)
            draw = ImageDraw.Draw(im)
            draw.text(ts_pos,text,font=font, fill = 'white')

        im.save(pipe.stdin, 'PNG')

    pipe.stdin.close()