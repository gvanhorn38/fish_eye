/*
On macOSX you can compile this file for python usage with:
$ gcc -DNDEBUG -shared -Wl,-install_name,arisparse -o arisparse.so -fPIC -O1 -Wall parse.c

On ubuntu you can compile this file for python usage with:
$ gcc -DNDEBUG -shared -Wl,-soname,arisparse -o arisparse.so -fPIC -O1 -Wall parse.c
*/

#include "stdio.h"
#include "FileHeader.h"
#include "FrameHeader.h"
#include "FrameFuncs.h"
//#include <math.h>
#include <stddef.h>
#include <string.h>

#define CANT_OPEN_INPUT     -2
#define CANT_OPEN_OUTPUT    -3
#define NOT_ARIS_FILE       -4
#define CORRUPT_ARIS_FILE   -5
#define IO_ERROR            -6


size_t get_beams_from_pingmode(uint32_t pingmode) {

    switch (pingmode) {
    case  1:
    case  2:
        return 48;

    case  3:
    case  4:
    case  5:
        return 96;

    case  6:
    case  7:
    case  8:
        return 64;

    case  9:
    case 10:
    case 11:
    case 12:
        return 128;
    }

    return 0;
}

int get_video_stats(const char* inputPath, long * samples_per_beam, long * num_beams, long * num_frames) {

    FILE* fpIn = NULL;
    struct ArisFileHeader fileHeader;
    struct ArisFrameHeader frameHeader;
    long fileSize = 0, dataSize = 0, frameSize = 0;

    fpIn = fopen(inputPath, "rb");
    if (!fpIn) {
        fprintf(stderr, "Couldn't open the input file.\n");
        return CANT_OPEN_INPUT;
    }

    if (fseek(fpIn, 0, SEEK_END)) {
        fprintf(stderr, "Couldn't determine file size.\n");
        return IO_ERROR;
    }

    fileSize = ftell(fpIn);
    fseek(fpIn, 0, SEEK_SET);
    dataSize = fileSize - sizeof(struct ArisFileHeader);

    if (fread(&fileHeader, sizeof(fileHeader), 1, fpIn) != 1) {
        fprintf(stderr, "Couldn't read complete file header.\n");
        return NOT_ARIS_FILE;
    }

    if (fileHeader.Version != ARIS_FILE_SIGNATURE) {
        fprintf(stderr, "Invalid file header.\n");
        return NOT_ARIS_FILE;
    }

    if (fread(&frameHeader, sizeof(frameHeader), 1, fpIn) != 1) {
        fprintf(stderr, "Couldn't read first frame buffer.\n");
        return CORRUPT_ARIS_FILE;
    }

    // ARIS recordings have a consistent frame size all the way through the file.
    frameSize = (long)(frameHeader.SamplesPerBeam * get_beams_from_pingmode(frameHeader.PingMode));

    *samples_per_beam = frameHeader.SamplesPerBeam;
    *num_beams = get_beams_from_pingmode(frameHeader.PingMode);
    *num_frames = dataSize / frameSize;

    return 0;
}

int get_frame_data(const char* inputPath, int frame_index, uint8_t * frameData, uint32_t * SampleStartDelay, float * SoundSpeed, uint32_t * SamplePeriod) {

    FILE* fpIn = NULL;
    struct ArisFileHeader fileHeader;
    struct ArisFrameHeader frameHeader;
    long fileSize = 0, dataSize = 0, frameSize = 0;

    fpIn = fopen(inputPath, "rb");
    if (!fpIn) {
        fprintf(stderr, "Couldn't open the input file.\n");
        return CANT_OPEN_INPUT;
    }

    if (fseek(fpIn, 0, SEEK_END)) {
        fprintf(stderr, "Couldn't determine file size.\n");
        return IO_ERROR;
    }

    fileSize = ftell(fpIn);
    fseek(fpIn, 0, SEEK_SET);
    dataSize = fileSize - sizeof(struct ArisFileHeader);

    if (fread(&fileHeader, sizeof(fileHeader), 1, fpIn) != 1) {
        fprintf(stderr, "Couldn't read complete file header.\n");
        return NOT_ARIS_FILE;
    }

    if (fileHeader.Version != ARIS_FILE_SIGNATURE) {
        fprintf(stderr, "Invalid file header.\n");
        return NOT_ARIS_FILE;
    }

    if (fread(&frameHeader, sizeof(frameHeader), 1, fpIn) != 1) {
        fprintf(stderr, "Couldn't read first frame buffer.\n");
        return CORRUPT_ARIS_FILE;
    }


    frameSize = (long)(frameHeader.SamplesPerBeam * get_beams_from_pingmode(frameHeader.PingMode));

    if (frame_index == 0){
        if (fread(frameData, frameSize, 1, fpIn) != 1){
            fprintf(stderr, "Couldn't read frame data at index %d.\n", frame_index);
        }
    }
    else{
        // Seek past the 0th frame data
        fseek(fpIn, frameSize, SEEK_CUR);

        // Skip all the frames up to the desired index
        fseek(fpIn, (frameSize + sizeof(frameHeader)) * (frame_index - 1), SEEK_CUR);

        // Read in the frame header
        if (fread(&frameHeader, sizeof(frameHeader), 1, fpIn) != 1) {
            fprintf(stderr, "Couldn't read frame header at index %d.\n", frame_index);
            return CORRUPT_ARIS_FILE;
        }
        // Read in the frame data
        if (fread(frameData, frameSize, 1, fpIn) != 1){
            fprintf(stderr, "Couldn't read frame data at index %d.\n", frame_index);
        }

    }

    *SampleStartDelay = frameHeader.SampleStartDelay;
    *SoundSpeed = frameHeader.SoundSpeed;
    *SamplePeriod = frameHeader.SamplePeriod;

    //float WindowStart   = frameHeader.SampleStartDelay * 1e-6 * frameHeader.SoundSpeed / 2;
    //float WindowLength  = frameHeader.SamplePeriod * frameHeader.SamplesPerBeam * 1e-6 * frameHeader.SoundSpeed / 2;
    //float RangeStart       = WindowStart;
    //float RangeEnd         = WindowStart + WindowLength;
    //float SampleRange = WindowStart + frameHeader.SamplePeriod * idx * 1e-6 * frameHeader.SoundSpeed  / 2;
    //float SampleLength     = frameHeader.SamplePeriod *  1e-6 * frameHeader.SoundSpeed  / 2;

    return 0;
}
