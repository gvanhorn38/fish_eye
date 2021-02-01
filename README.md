# Converting ARIS into image zipfiles that can be provided to annotators:
```
gen_clips.py --aris_dir [location of source files]
             --clip_dir [location to output unzipped images]
             --dump_dir [location to output json dumps of created clips]
             --river_name [eg. kenai]
             --river_location [eg. ak]
             --zip_location [location to output zipped images for annotation]
```

# Annotate zip files:
https://kulits.github.io/vatic.js/index.html

# Convert outputs of annotation tool to common format:
```
convert_annotations.py --json_dump_path [path to json dump of annotated files created in the previous step]
                       --xml_dir [location of annotations created in the previous step]
                       --output_path [location of place to put converted annotations]
```
