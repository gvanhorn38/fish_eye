// FileHeader.h

// THIS IS GENERATED WITH GenerateHeader, DO NOT MODIFY

#ifndef ARIS_ARISFILEHEADER_H
#define ARIS_ARISFILEHEADER_H

#include <stdint.h>

#define ARIS_FILE_SIGNATURE  0x05464444
#define ARIS_FRAME_SIGNATURE 0x05464444

#pragma pack(push, 1)

// Defines the metadata at the start of an ARIS recording.
struct ArisFileHeader {

    // File format version DDF_05 = 0x05464444
    uint32_t Version;

    // Total frames in file
    // Note: Writers should populate; readers should calculate the number of frames from file size & beams*samples.
    uint32_t FrameCount;

    // Initial recorded frame rate
    // OBSOLETE: See frame header instead.
    uint32_t FrameRate;

    // Non-zero if HF, zero if LF
    // OBSOLETE: See frame header instead.
    uint32_t HighResolution;

    // ARIS 3000 = 128/64, ARIS 1800 = 96/48, ARIS 1200 = 48
    // Note: Writers should populate; readers should see frame header instead.
    uint32_t NumRawBeams;

    // 1/Sample Period
    // OBSOLETE: See frame header instead.
    float SampleRate;

    // Number of range samples in each beam
    // Note: Writers should populate; readers should see frame header instead.
    uint32_t SamplesPerChannel;

    // Relative gain in dB:  0 - 40
    // OBSOLETE: See frame header instead.
    uint32_t ReceiverGain;

    // Image window start range in meters (code [0..31] in DIDSON)
    // OBSOLETE: See frame header instead.
    float WindowStart;

    // Image window length in meters  (code [0..3] in DIDSON)
    // OBSOLETE: See frame header instead.
    float WindowLength;

    // Non-zero = lens down (DIDSON) or lens up (ARIS), zero = opposite
    // OBSOLETE: See frame header instead.
    uint32_t Reverse;

    // Sonar serial number
    uint32_t SN;

    // Date that file was recorded
    char strDate[32];

    // User input to identify file in 256 characters
    char strHeaderID[256];

    // User-defined integer quantity
    int32_t UserID1;

    // User-defined integer quantity
    int32_t UserID2;

    // User-defined integer quantity
    int32_t UserID3;

    // User-defined integer quantity
    int32_t UserID4;

    // First frame number from source file (for DIDSON snippet files)
    uint32_t StartFrame;

    // Last frame number from source file (for DIDSON snippet files)
    uint32_t EndFrame;

    // Non-zero indicates time lapse recording
    uint32_t TimeLapse;

    // Number of frames/seconds between recorded frames
    uint32_t RecordInterval;

    // Frames or seconds interval
    uint32_t RadioSeconds;

    // Record every Nth frame
    uint32_t FrameInterval;

    // See DDF_04 file format document
    // OBSOLETE: Obsolete.
    uint32_t Flags;

    // See DDF_04 file format document
    uint32_t AuxFlags;

    // Sound velocity in water
    // OBSOLETE: See frame header instead.
    uint32_t Sspd;

    // See DDF_04 file format document
    uint32_t Flags3D;

    // DIDSON software version that recorded the file
    uint32_t SoftwareVersion;

    // Water temperature code:  0 = 5-15C, 1 = 15-25C, 2 = 25-35C
    uint32_t WaterTemp;

    // Salinity code:  0 = fresh, 1 = brackish, 2 = salt
    uint32_t Salinity;

    // Added for ARIS but not used
    uint32_t PulseLength;

    // Added for ARIS but not used
    uint32_t TxMode;

    // Reserved for future use
    uint32_t VersionFGPA;

    // Reserved for future use
    uint32_t VersionPSuC;

    // Frame index of frame used for thumbnail image of file
    uint32_t ThumbnailFI;

    // Total file size in bytes
    // OBSOLETE: Do not use; query your filesystem instead.
    uint64_t FileSize;

    // Reserved for future use
    // OBSOLETE: Obsolete; not used.
    uint64_t OptionalHeaderSize;

    // Reserved for future use
    // OBSOLETE: Obsolete; not used.
    uint64_t OptionalTailSize;

    // DIDSON_ADJUSTED_VERSION_MINOR
    // OBSOLETE: Obsolete.
    uint32_t VersionMinor;

    // Non-zero if telephoto lens (large lens, hi-res lens, big lens) is present
    // OBSOLETE: See frame header instead.
    uint32_t LargeLens;

    // Padding to fill out to 1024 bytes
    char padding[568];

};

#pragma pack(pop)

// In general the struct above should be used rather than the offsets.
// The 'ArisFileHeader' prefix prevents name conflicts between the file and frame headers
enum ArisFileHeaderOffsets {
    ArisFileHeaderOffset_Version             =    0,

    ArisFileHeaderOffset_FrameCount          =    4,

    // OBSOLETE: See frame header instead.
    ArisFileHeaderOffset_FrameRate           =    8,

    // OBSOLETE: See frame header instead.
    ArisFileHeaderOffset_HighResolution      =   12,

    ArisFileHeaderOffset_NumRawBeams         =   16,

    // OBSOLETE: See frame header instead.
    ArisFileHeaderOffset_SampleRate          =   20,

    ArisFileHeaderOffset_SamplesPerChannel   =   24,

    // OBSOLETE: See frame header instead.
    ArisFileHeaderOffset_ReceiverGain        =   28,

    // OBSOLETE: See frame header instead.
    ArisFileHeaderOffset_WindowStart         =   32,

    // OBSOLETE: See frame header instead.
    ArisFileHeaderOffset_WindowLength        =   36,

    // OBSOLETE: See frame header instead.
    ArisFileHeaderOffset_Reverse             =   40,

    ArisFileHeaderOffset_SN                  =   44,

    ArisFileHeaderOffset_strDate             =   48,

    ArisFileHeaderOffset_strHeaderID         =   80,

    ArisFileHeaderOffset_UserID1             =  336,

    ArisFileHeaderOffset_UserID2             =  340,

    ArisFileHeaderOffset_UserID3             =  344,

    ArisFileHeaderOffset_UserID4             =  348,

    ArisFileHeaderOffset_StartFrame          =  352,

    ArisFileHeaderOffset_EndFrame            =  356,

    ArisFileHeaderOffset_TimeLapse           =  360,

    ArisFileHeaderOffset_RecordInterval      =  364,

    ArisFileHeaderOffset_RadioSeconds        =  368,

    ArisFileHeaderOffset_FrameInterval       =  372,

    // OBSOLETE: Obsolete.
    ArisFileHeaderOffset_Flags               =  376,

    ArisFileHeaderOffset_AuxFlags            =  380,

    // OBSOLETE: See frame header instead.
    ArisFileHeaderOffset_Sspd                =  384,

    ArisFileHeaderOffset_Flags3D             =  388,

    ArisFileHeaderOffset_SoftwareVersion     =  392,

    ArisFileHeaderOffset_WaterTemp           =  396,

    ArisFileHeaderOffset_Salinity            =  400,

    ArisFileHeaderOffset_PulseLength         =  404,

    ArisFileHeaderOffset_TxMode              =  408,

    ArisFileHeaderOffset_VersionFGPA         =  412,

    ArisFileHeaderOffset_VersionPSuC         =  416,

    ArisFileHeaderOffset_ThumbnailFI         =  420,

    // OBSOLETE: Do not use; query your filesystem instead.
    ArisFileHeaderOffset_FileSize            =  424,

    // OBSOLETE: Obsolete; not used.
    ArisFileHeaderOffset_OptionalHeaderSize  =  432,

    // OBSOLETE: Obsolete; not used.
    ArisFileHeaderOffset_OptionalTailSize    =  440,

    // OBSOLETE: Obsolete.
    ArisFileHeaderOffset_VersionMinor        =  448,

    // OBSOLETE: See frame header instead.
    ArisFileHeaderOffset_LargeLens           =  452,

};


#endif // !ARIS_ARISFILEHEADER_H