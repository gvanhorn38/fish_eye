# Download the exported model [here](https://bit.ly/frozen_trout)  


# Converting ARIS into image zipfiles that can be provided to annotators:
```
gen_clips.py --aris_dir [location of source files]
             --clip_dir [location to output unzipped images]
             --river_name [eg. kenai]
             --river_location [eg. wa]
             --zip_location [location to output zipped images for annotation]
```

# Annotate zip files:
https://kulits.github.io/vatic.js/index.html

# Convert outputs of annotation tool to common format:
```
store_annotations.py --xml_dir [location of annotations created in the previous step]
                     --output_path [location of place to put converted annotations]
                     --clip_dir [location of clip_dir from gen_clips.py]
```

# Prediction:
### Generate images from source files:
```
gvh/gen_clips.py --aris_dir [location of source files]
             --clip_dir [location to output unzipped images]
             --river_name [eg. kenai]
             --river_location [eg. wa]
```

### Predict on the images:
```
predict.py --path_to_frozen_graph [location of exported model]
           --path_to_image_dir [clip_dir from previous step]
           --path_to_output_dir [directory to output predictions]
```

### Create direction counts from predictions:
```
fish_tracker.py --path_to_json [path_to_output_dir from previous step]
```
