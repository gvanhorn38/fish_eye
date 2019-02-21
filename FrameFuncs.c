// FrameFuncs.c

#include "FrameFuncs.h"

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