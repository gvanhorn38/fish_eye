// FrameFuncs.h

#include <stddef.h>
#include <stdint.h>

#ifndef FRAMEFUNCS_H
#define FRAMEFUNCS_H

// Returns the number of beams used for the specified pingmode.
size_t get_beams_from_pingmode(uint32_t pingmode);

#endif // !FRAMEFUNCS_H