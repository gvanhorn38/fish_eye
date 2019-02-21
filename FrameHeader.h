// FrameHeader.h

// THIS IS GENERATED WITH GenerateHeader, DO NOT MODIFY

#ifndef ARIS_ARISFRAMEHEADER_H
#define ARIS_ARISFRAMEHEADER_H

#include <stdint.h>

#define ARIS_FILE_SIGNATURE  0x05464444
#define ARIS_FRAME_SIGNATURE 0x05464444

#pragma pack(push, 1)

// Defines the metadata at the start of an ARIS frame.
struct ArisFrameHeader {

    // Frame number in file
    uint32_t FrameIndex;

    // PC time stamp when recorded; microseconds since epoch (Jan 1st 1970)
    uint64_t FrameTime;

    // ARIS file format version = 0x05464444
    uint32_t Version;

    uint32_t Status;

    // On-sonar microseconds since epoch (Jan 1st 1970)
    uint64_t sonarTimeStamp;

    uint32_t TS_Day;

    uint32_t TS_Hour;

    uint32_t TS_Minute;

    uint32_t TS_Second;

    uint32_t TS_Hsecond;

    uint32_t TransmitMode;

    // Window start in meters
    float WindowStart;

    // Window length in meters
    float WindowLength;

    uint32_t Threshold;

    int32_t Intensity;

    // Note: 0-24 dB
    uint32_t ReceiverGain;

    // CPU temperature
    // Note: Celsius
    uint32_t DegC1;

    // Power supply temperature
    // Note: Celsius
    uint32_t DegC2;

    // % relative humidity
    uint32_t Humidity;

    // Focus units 0-1000
    uint32_t Focus;

    // OBSOLETE: Unused.
    uint32_t Battery;

    float UserValue1;

    float UserValue2;

    float UserValue3;

    float UserValue4;

    float UserValue5;

    float UserValue6;

    float UserValue7;

    float UserValue8;

    // Platform velocity from AUV integration
    float Velocity;

    // Platform depth from AUV integration
    float Depth;

    // Platform altitude from AUV integration
    float Altitude;

    // Platform pitch from AUV integration
    float Pitch;

    // Platform pitch rate from AUV integration
    float PitchRate;

    // Platform roll from AUV integration
    float Roll;

    // Platform roll rate from AUV integration
    float RollRate;

    // Platform heading from AUV integration
    float Heading;

    // Platform heading rate from AUV integration
    float HeadingRate;

    // Sonar compass heading output
    float CompassHeading;

    // Sonar compass pitch output
    float CompassPitch;

    // Sonar compass roll output
    float CompassRoll;

    // from auxiliary GPS sensor
    double Latitude;

    // from auxiliary GPS sensor
    double Longitude;

    // Note: special for PNNL
    float SonarPosition;

    uint32_t ConfigFlags;

    float BeamTilt;

    float TargetRange;

    float TargetBearing;

    uint32_t TargetPresent;

    // OBSOLETE: Unused.
    uint32_t FirmwareRevision;

    uint32_t Flags;

    // Source file frame number for CSOT output files
    uint32_t SourceFrame;

    // Water temperature from housing temperature sensor
    float WaterTemp;

    uint32_t TimerPeriod;

    // Sonar X location for 3D processing
    // Note: Bluefin, external sensor data
    float SonarX;

    // Sonar Y location for 3D processing
    float SonarY;

    // Sonar Z location for 3D processing
    float SonarZ;

    // X2 pan output
    float SonarPan;

    // X2 tilt output
    float SonarTilt;

    // X2 roll output
    float SonarRoll;

    float PanPNNL;

    float TiltPNNL;

    float RollPNNL;

    // Note: special for Bluefin HAUV or other AUV integration
    double VehicleTime;

    // GPS output from NMEA GGK message
    float TimeGGK;

    // GPS output from NMEA GGK message
    uint32_t DateGGK;

    // GPS output from NMEA GGK message
    uint32_t QualityGGK;

    // GPS output from NMEA GGK message
    uint32_t NumSatsGGK;

    // GPS output from NMEA GGK message
    float DOPGGK;

    // GPS output from NMEA GGK message
    float EHTGGK;

    // external sensor
    float HeaveTSS;

    // GPS year output
    uint32_t YearGPS;

    // GPS month output
    uint32_t MonthGPS;

    // GPS day output
    uint32_t DayGPS;

    // GPS hour output
    uint32_t HourGPS;

    // GPS minute output
    uint32_t MinuteGPS;

    // GPS second output
    uint32_t SecondGPS;

    // GPS 1/100th second output
    uint32_t HSecondGPS;

    // Sonar mount location pan offset for 3D processing; meters
    float SonarPanOffset;

    // Sonar mount location tilt offset for 3D processing
    float SonarTiltOffset;

    // Sonar mount location roll offset for 3D processing
    float SonarRollOffset;

    // Sonar mount location X offset for 3D processing
    float SonarXOffset;

    // Sonar mount location Y offset for 3D processing
    float SonarYOffset;

    // Sonar mount location Z offset for 3D processing
    float SonarZOffset;

    // 3D processing transformation matrix
    float Tmatrix[16];

    // Calculated as 1e6/SamplePeriod
    float SampleRate;

    // X-axis sonar acceleration
    float AccellX;

    // Y-axis sonar acceleration
    float AccellY;

    // Z-axis sonar acceleration
    float AccellZ;

    // ARIS ping mode
    // Note: 1..12
    uint32_t PingMode;

    // Frequency
    // Note: 1 = HF, 0 = LF
    uint32_t FrequencyHiLow;

    // Width of transmit pulse
    // Note: 4..100 microseconds
    uint32_t PulseWidth;

    // Ping cycle time
    // Note: 1802..65535 microseconds
    uint32_t CyclePeriod;

    // Downrange sample rate
    // Note: 4..100 microseconds
    uint32_t SamplePeriod;

    // 1 = Transmit ON, 0 = Transmit OFF
    uint32_t TransmitEnable;

    // Instantaneous frame rate between frame N and frame N-1
    // Note: microseconds
    float FrameRate;

    // Sound velocity in water calculated from water temperature depth and salinity setting
    // Note: m/s
    float SoundSpeed;

    // Number of downrange samples in each beam
    uint32_t SamplesPerBeam;

    // 1 = 150V ON (Max Power), 0 = 150V OFF (Min Power, 12V)
    uint32_t Enable150V;

    // Delay from transmit until start of sampling (window start) in usec, [930..65535]
    uint32_t SampleStartDelay;

    // 1 = telephoto lens (large lens, big lens, hi-res lens) present
    uint32_t LargeLens;

    // 1 = ARIS 3000, 0 = ARIS 1800, 2 = ARIS 1200
    uint32_t TheSystemType;

    // Sonar serial number as labeled on housing
    uint32_t SonarSerialNumber;

    // Reserved.
    // OBSOLETE: Obsolete
    uint64_t ReservedEK;

    // Error flag code bits
    uint32_t ArisErrorFlagsUint;

    // Missed packet count for Ethernet statistics reporting
    uint32_t MissedPackets;

    // Version number of ArisApp sending frame data
    uint32_t ArisAppVersion;

    // Reserved for future use
    uint32_t Available2;

    // 1 = frame data already ordered into [beam,sample] array, 0 = needs reordering
    uint32_t ReorderedSamples;

    // Water salinity code:  0 = fresh, 15 = brackish, 35 = salt
    uint32_t Salinity;

    // Depth sensor output
    // Note: psi
    float Pressure;

    // Battery input voltage before power steering
    // Note: mV
    float BatteryVoltage;

    // Main cable input voltage before power steering
    // Note: mV
    float MainVoltage;

    // Input voltage after power steering; filtered voltage
    // Note: mV
    float SwitchVoltage;

    // Note: Added 14-Aug-2012 for AutomaticRecording
    uint32_t FocusMotorMoving;

    // Note: Added 16-Aug (first two bits = 12V, second two bits = 150V, 00 = not changing, 01 = turning on, 10 = turning off)
    uint32_t VoltageChanging;

    uint32_t FocusTimeoutFault;

    uint32_t FocusOverCurrentFault;

    uint32_t FocusNotFoundFault;

    uint32_t FocusStalledFault;

    uint32_t FPGATimeoutFault;

    uint32_t FPGABusyFault;

    uint32_t FPGAStuckFault;

    uint32_t CPUTempFault;

    uint32_t PSUTempFault;

    uint32_t WaterTempFault;

    uint32_t HumidityFault;

    uint32_t PressureFault;

    uint32_t VoltageReadFault;

    uint32_t VoltageWriteFault;

    // Focus shaft current position
    // Note: 0..1000 motor units
    uint32_t FocusCurrentPosition;

    // Commanded pan position
    float TargetPan;

    // Commanded tilt position
    float TargetTilt;

    // Commanded roll position
    float TargetRoll;

    uint32_t PanMotorErrorCode;

    uint32_t TiltMotorErrorCode;

    uint32_t RollMotorErrorCode;

    // Low-resolution magnetic encoder absolute pan position (NaN indicates no arm detected for axis since 2.6.0.8403)
    float PanAbsPosition;

    // Low-resolution magnetic encoder absolute tilt position (NaN indicates no arm detected for axis since 2.6.0.8403)
    float TiltAbsPosition;

    // Low-resolution magnetic encoder absolute roll position (NaN indicates no arm detected for axis since 2.6.0.8403)
    float RollAbsPosition;

    // Accelerometer outputs from AR2 CPU board sensor
    // Note: G
    float PanAccelX;

    // Note: G
    float PanAccelY;

    // Note: G
    float PanAccelZ;

    // Note: G
    float TiltAccelX;

    // Note: G
    float TiltAccelY;

    // Note: G
    float TiltAccelZ;

    // Note: G
    float RollAccelX;

    // Note: G
    float RollAccelY;

    // Note: G
    float RollAccelZ;

    // Cookie indices for command acknowlege in frame header
    uint32_t AppliedSettings;

    // Cookie indices for command acknowlege in frame header
    uint32_t ConstrainedSettings;

    // Cookie indices for command acknowlege in frame header
    uint32_t InvalidSettings;

    // If true delay is added between sending out image data packets
    uint32_t EnableInterpacketDelay;

    // packet delay factor in us (does not include function overhead time)
    uint32_t InterpacketDelayPeriod;

    // Total time the sonar has been running over its lifetime.
    // Note: seconds
    uint32_t Uptime;

    // Major version number
    uint16_t ArisAppVersionMajor;

    // Minor version number
    uint16_t ArisAppVersionMinor;

    // Sonar time when frame cycle is initiated in hardware
    uint64_t GoTime;

    // AR2 pan velocity
    // Note: degrees/second
    float PanVelocity;

    // AR2 tilt velocity
    // Note: degrees/second
    float TiltVelocity;

    // AR2 roll velocity
    // Note: degrees/second
    float RollVelocity;

    // Age of the last GPS fix acquired; capped at 0xFFFFFFFF; zero if none
    // Note: microseconds
    uint32_t GpsTimeAge;

    // bit 0 = Defender
    uint32_t SystemVariant;

    // Padding to fill out to 1024 bytes
    char padding[288];

};

#pragma pack(pop)

// In general the struct above should be used rather than the offsets.
// The 'ArisFrameHeader' prefix prevents name conflicts between the file and frame headers
enum ArisFrameHeaderOffsets {
    ArisFrameHeaderOffset_FrameIndex         =    0,

    ArisFrameHeaderOffset_FrameTime          =    4,

    ArisFrameHeaderOffset_Version            =   12,

    ArisFrameHeaderOffset_Status             =   16,

    ArisFrameHeaderOffset_sonarTimeStamp     =   20,

    ArisFrameHeaderOffset_TS_Day             =   28,

    ArisFrameHeaderOffset_TS_Hour            =   32,

    ArisFrameHeaderOffset_TS_Minute          =   36,

    ArisFrameHeaderOffset_TS_Second          =   40,

    ArisFrameHeaderOffset_TS_Hsecond         =   44,

    ArisFrameHeaderOffset_TransmitMode       =   48,

    ArisFrameHeaderOffset_WindowStart        =   52,

    ArisFrameHeaderOffset_WindowLength       =   56,

    ArisFrameHeaderOffset_Threshold          =   60,

    ArisFrameHeaderOffset_Intensity          =   64,

    ArisFrameHeaderOffset_ReceiverGain       =   68,

    ArisFrameHeaderOffset_DegC1              =   72,

    ArisFrameHeaderOffset_DegC2              =   76,

    ArisFrameHeaderOffset_Humidity           =   80,

    ArisFrameHeaderOffset_Focus              =   84,

    // OBSOLETE: Unused.
    ArisFrameHeaderOffset_Battery            =   88,

    ArisFrameHeaderOffset_UserValue1         =   92,

    ArisFrameHeaderOffset_UserValue2         =   96,

    ArisFrameHeaderOffset_UserValue3         =  100,

    ArisFrameHeaderOffset_UserValue4         =  104,

    ArisFrameHeaderOffset_UserValue5         =  108,

    ArisFrameHeaderOffset_UserValue6         =  112,

    ArisFrameHeaderOffset_UserValue7         =  116,

    ArisFrameHeaderOffset_UserValue8         =  120,

    ArisFrameHeaderOffset_Velocity           =  124,

    ArisFrameHeaderOffset_Depth              =  128,

    ArisFrameHeaderOffset_Altitude           =  132,

    ArisFrameHeaderOffset_Pitch              =  136,

    ArisFrameHeaderOffset_PitchRate          =  140,

    ArisFrameHeaderOffset_Roll               =  144,

    ArisFrameHeaderOffset_RollRate           =  148,

    ArisFrameHeaderOffset_Heading            =  152,

    ArisFrameHeaderOffset_HeadingRate        =  156,

    ArisFrameHeaderOffset_CompassHeading     =  160,

    ArisFrameHeaderOffset_CompassPitch       =  164,

    ArisFrameHeaderOffset_CompassRoll        =  168,

    ArisFrameHeaderOffset_Latitude           =  172,

    ArisFrameHeaderOffset_Longitude          =  180,

    ArisFrameHeaderOffset_SonarPosition      =  188,

    ArisFrameHeaderOffset_ConfigFlags        =  192,

    ArisFrameHeaderOffset_BeamTilt           =  196,

    ArisFrameHeaderOffset_TargetRange        =  200,

    ArisFrameHeaderOffset_TargetBearing      =  204,

    ArisFrameHeaderOffset_TargetPresent      =  208,

    // OBSOLETE: Unused.
    ArisFrameHeaderOffset_FirmwareRevision   =  212,

    ArisFrameHeaderOffset_Flags              =  216,

    ArisFrameHeaderOffset_SourceFrame        =  220,

    ArisFrameHeaderOffset_WaterTemp          =  224,

    ArisFrameHeaderOffset_TimerPeriod        =  228,

    ArisFrameHeaderOffset_SonarX             =  232,

    ArisFrameHeaderOffset_SonarY             =  236,

    ArisFrameHeaderOffset_SonarZ             =  240,

    ArisFrameHeaderOffset_SonarPan           =  244,

    ArisFrameHeaderOffset_SonarTilt          =  248,

    ArisFrameHeaderOffset_SonarRoll          =  252,

    ArisFrameHeaderOffset_PanPNNL            =  256,

    ArisFrameHeaderOffset_TiltPNNL           =  260,

    ArisFrameHeaderOffset_RollPNNL           =  264,

    ArisFrameHeaderOffset_VehicleTime        =  268,

    ArisFrameHeaderOffset_TimeGGK            =  276,

    ArisFrameHeaderOffset_DateGGK            =  280,

    ArisFrameHeaderOffset_QualityGGK         =  284,

    ArisFrameHeaderOffset_NumSatsGGK         =  288,

    ArisFrameHeaderOffset_DOPGGK             =  292,

    ArisFrameHeaderOffset_EHTGGK             =  296,

    ArisFrameHeaderOffset_HeaveTSS           =  300,

    ArisFrameHeaderOffset_YearGPS            =  304,

    ArisFrameHeaderOffset_MonthGPS           =  308,

    ArisFrameHeaderOffset_DayGPS             =  312,

    ArisFrameHeaderOffset_HourGPS            =  316,

    ArisFrameHeaderOffset_MinuteGPS          =  320,

    ArisFrameHeaderOffset_SecondGPS          =  324,

    ArisFrameHeaderOffset_HSecondGPS         =  328,

    ArisFrameHeaderOffset_SonarPanOffset     =  332,

    ArisFrameHeaderOffset_SonarTiltOffset    =  336,

    ArisFrameHeaderOffset_SonarRollOffset    =  340,

    ArisFrameHeaderOffset_SonarXOffset       =  344,

    ArisFrameHeaderOffset_SonarYOffset       =  348,

    ArisFrameHeaderOffset_SonarZOffset       =  352,

    ArisFrameHeaderOffset_Tmatrix            =  356,

    ArisFrameHeaderOffset_SampleRate         =  420,

    ArisFrameHeaderOffset_AccellX            =  424,

    ArisFrameHeaderOffset_AccellY            =  428,

    ArisFrameHeaderOffset_AccellZ            =  432,

    ArisFrameHeaderOffset_PingMode           =  436,

    ArisFrameHeaderOffset_FrequencyHiLow     =  440,

    ArisFrameHeaderOffset_PulseWidth         =  444,

    ArisFrameHeaderOffset_CyclePeriod        =  448,

    ArisFrameHeaderOffset_SamplePeriod       =  452,

    ArisFrameHeaderOffset_TransmitEnable     =  456,

    ArisFrameHeaderOffset_FrameRate          =  460,

    ArisFrameHeaderOffset_SoundSpeed         =  464,

    ArisFrameHeaderOffset_SamplesPerBeam     =  468,

    ArisFrameHeaderOffset_Enable150V         =  472,

    ArisFrameHeaderOffset_SampleStartDelay   =  476,

    ArisFrameHeaderOffset_LargeLens          =  480,

    ArisFrameHeaderOffset_TheSystemType      =  484,

    ArisFrameHeaderOffset_SonarSerialNumber  =  488,

    // OBSOLETE: Obsolete
    ArisFrameHeaderOffset_ReservedEK         =  492,

    ArisFrameHeaderOffset_ArisErrorFlagsUint =  500,

    ArisFrameHeaderOffset_MissedPackets      =  504,

    ArisFrameHeaderOffset_ArisAppVersion     =  508,

    ArisFrameHeaderOffset_Available2         =  512,

    ArisFrameHeaderOffset_ReorderedSamples   =  516,

    ArisFrameHeaderOffset_Salinity           =  520,

    ArisFrameHeaderOffset_Pressure           =  524,

    ArisFrameHeaderOffset_BatteryVoltage     =  528,

    ArisFrameHeaderOffset_MainVoltage        =  532,

    ArisFrameHeaderOffset_SwitchVoltage      =  536,

    ArisFrameHeaderOffset_FocusMotorMoving   =  540,

    ArisFrameHeaderOffset_VoltageChanging    =  544,

    ArisFrameHeaderOffset_FocusTimeoutFault  =  548,

    ArisFrameHeaderOffset_FocusOverCurrentFault =  552,

    ArisFrameHeaderOffset_FocusNotFoundFault =  556,

    ArisFrameHeaderOffset_FocusStalledFault  =  560,

    ArisFrameHeaderOffset_FPGATimeoutFault   =  564,

    ArisFrameHeaderOffset_FPGABusyFault      =  568,

    ArisFrameHeaderOffset_FPGAStuckFault     =  572,

    ArisFrameHeaderOffset_CPUTempFault       =  576,

    ArisFrameHeaderOffset_PSUTempFault       =  580,

    ArisFrameHeaderOffset_WaterTempFault     =  584,

    ArisFrameHeaderOffset_HumidityFault      =  588,

    ArisFrameHeaderOffset_PressureFault      =  592,

    ArisFrameHeaderOffset_VoltageReadFault   =  596,

    ArisFrameHeaderOffset_VoltageWriteFault  =  600,

    ArisFrameHeaderOffset_FocusCurrentPosition =  604,

    ArisFrameHeaderOffset_TargetPan          =  608,

    ArisFrameHeaderOffset_TargetTilt         =  612,

    ArisFrameHeaderOffset_TargetRoll         =  616,

    ArisFrameHeaderOffset_PanMotorErrorCode  =  620,

    ArisFrameHeaderOffset_TiltMotorErrorCode =  624,

    ArisFrameHeaderOffset_RollMotorErrorCode =  628,

    ArisFrameHeaderOffset_PanAbsPosition     =  632,

    ArisFrameHeaderOffset_TiltAbsPosition    =  636,

    ArisFrameHeaderOffset_RollAbsPosition    =  640,

    ArisFrameHeaderOffset_PanAccelX          =  644,

    ArisFrameHeaderOffset_PanAccelY          =  648,

    ArisFrameHeaderOffset_PanAccelZ          =  652,

    ArisFrameHeaderOffset_TiltAccelX         =  656,

    ArisFrameHeaderOffset_TiltAccelY         =  660,

    ArisFrameHeaderOffset_TiltAccelZ         =  664,

    ArisFrameHeaderOffset_RollAccelX         =  668,

    ArisFrameHeaderOffset_RollAccelY         =  672,

    ArisFrameHeaderOffset_RollAccelZ         =  676,

    ArisFrameHeaderOffset_AppliedSettings    =  680,

    ArisFrameHeaderOffset_ConstrainedSettings =  684,

    ArisFrameHeaderOffset_InvalidSettings    =  688,

    ArisFrameHeaderOffset_EnableInterpacketDelay =  692,

    ArisFrameHeaderOffset_InterpacketDelayPeriod =  696,

    ArisFrameHeaderOffset_Uptime             =  700,

    ArisFrameHeaderOffset_ArisAppVersionMajor =  704,

    ArisFrameHeaderOffset_ArisAppVersionMinor =  706,

    ArisFrameHeaderOffset_GoTime             =  708,

    ArisFrameHeaderOffset_PanVelocity        =  716,

    ArisFrameHeaderOffset_TiltVelocity       =  720,

    ArisFrameHeaderOffset_RollVelocity       =  724,

    ArisFrameHeaderOffset_GpsTimeAge         =  728,

    ArisFrameHeaderOffset_SystemVariant      =  732,

};


#endif // !ARIS_ARISFRAMEHEADER_H