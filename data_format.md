
We are typically given an ARIS file and a "count file" that contains the human counts of fish at some temporal resolution. The "count file" might be a csv file, a text file, or something else. We'll create a json file that stores this information in a more convenient/universal format:

```
{   // Information for a single clip
    "clip_id" :               // Unique id for this clip (perhaps a UUID?)
    "aris_filename" :         // Path to the ARIS file
    "clip_name" :             // Basename of annotation files
    "start_frame" :           // Start frame for this "count event", used to index into the ARIS file
    "end_frame" :             // End frame for this "count event", used to index into the ARIS file
    "start_time" :            // Start time in for this "count event" (this should be the sonartimestamp of the start_frame )
    "end_time " :             // End time for this "count event" (this should be the sonartimestamp of the end_frame )
    "upstream_direction" :    // Either `left` or `right`
    "fish": [                  // Should have one entry for each fish
        {
            "frame" : ,        // Manual marking frame number
            "direction" : ,    // Either `left`, `right`, or `undefined`
            "length" : ,       // Length in meters
            "x" : ,            // x position of marking
            "y" : ,            // y position of marking
        }
    ],
    "aris_info" : {            // Needed for generating a warped image from the raw ARIS samples
        "camera_type" : ,      // ARIS camera type
        "framerate" : ,        // Frames per second
        "pixel_meter_size" : , // The size of a pixel in meters
        "xdim" : ,             // The width of the warped image
        "ydim" : ,             // The height of the warped image
        "x_meter_start" : ,    // x start in meters 
        "y_meter_start" : ,    // y start in meters
        "x_meter_stop" : ,     // x stop in meters
        "y_meter_stop' : ,     // y stop in meters
    }
}
```


When a sequence of frames are annotated from an ARIS file (i.e. a "clip"), we will produce the following json file:

```
{   // Annotation information for a single "clip"
    "clip_id" :                // a unique clip id, should match the `clip_id` in the clip info dictionary above.
    "aris_filename" :          // the name of the associated aris file
    "start_frame" :            // Start frame for this "clip", used to index into the ARIS file
    "end_frame" :              // End frame for this "clip", used to index into the ARIS file
    "upstream_direction" :     // Either `left` or `right`
    "clip_meter_width" :       // Width of a frame in meters
    "clip_meter_height" :      // Height of a frame in meters
    "frames" : [                                      // Should have one entry for each frame
        {
            "frame_num" : ,                           // the frame number from the ARIS file
            "fish" : [                                // should have one entry for each fish that is present in this frame
                {
                    "fish_id" :                       // fish track id
                    "box" : [xmin, ymin, xmax, ymax]  // in normalized coordinates (multiply by `xdim` and `ydim` to get unnormalized coordinates)
                    "visible" :                       // 0 means not visible (is this necessary?), 1 means visible
                    "human_labeled" :                 // 1 or 0 for whether a human did the annotation or if it was interpolated 
                }
            ]
        }
    ],
    "fish" : [                        // Should have one entry for each fish
        {
            "id" :                    // fish track id (should be unique) (0 based, not unique across clips)
            "length" :                // computed fish length in meters
            "direction" :             // computed swimming direction {left, right, none}
            "start_frame_index" :     // first frame this fish appears in
            "end_frame_index" :       // last frame this fish appears in 
            "color" :                 // a unique hex color value for this fish
        }
    ]
}
