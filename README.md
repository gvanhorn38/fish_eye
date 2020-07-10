# fish_eye
Analyzing ARIS data to detect, track, and count fish.


# Compile C Functions

You can run the makefile, created for Mac:
```
$ make
```

Or you can modify the below line to create the `.so` file for your own platform:
```
$ gcc -DNDEBUG -shared -Wl,-install_name,arisparse -o arisparse.so -fPIC -O1 -Wall parse.c
```



# Annotation

### 1. Convert ARIS files into image zip files

To convert the raw ARIS data into zipped files of frames that can be provided to annotators, run the following:
```
$ python gen_clips.py --aris_dir [location of source files] --clip_dir [location to output unzipped images] --river_name [eg kenai] --river_location [eg wa] --zip_location [path to output zipped images]
```

### 2. Annotate clips

Annotate zip files with the following link: https://kulits.github.io/vatic.js/index.html

### 3. Convert output of annotation tool

To convert the output of the above annotation tool, run the following:
```
$ python store_coco.py --xml_dir [location of annotations from tool output] --output_path [location of place to store converted annotations] --clip_dir [location of clip_dir from gen_clips.py]
```



# Prediction

### 1. Generate images

To generate images from ARIS source files, run the following:
```
$ python gen_clips.py --aris_dir [location of source files] --clip_dir [location to output unzipped images] --river_name [eg kenai] --river_location [eg wa]
```

### 2. Predict on images

To predict on the output images, run the following:
```
$ python predict.py --path_to_frozen_graph [location of exported model] --path_to_image_dir [clip_dir from previous step] --path_to_output_dir [directory to store output predictions]
```

### 3. Track and count fish

To get direction counts from the predictions (this will print out counts of the number of right-going, left-going, and stationary fish), run the following:
```
$ python fish_tracker.py --path_to_json [path_to_output_dir from previous step, either json or directory of jsons]
```



# Re-training Model

### 1. Generate annotations

Complete all the steps as outlined the "Annotation" section.

### 2. Combine all annotations

To combine all json annotation files that will be used in training, run the following:
```
$ python combine_json.py --input_dir [path to json annotations] --output_path [path to store combined json]
```

### 3. Create tfrecords

To create the tfrecords data format for training, run the following:
```
$ python create_tfrecords.py --dataset_path [output_path from previous step] --prefix_train --output_dir [folder to place tfrecord files] --store_images --shuffle --threads --shards
```

### 4. Train model

To train the Tensorflow model, run the following:
```
$ python model_main.py
```

### 5. Export model

To export the model for prediction, run the following:
```
$ python export_inference_graph.py --pipeline_config_path [path to model .config file] --trained_checkpoint_prefix --output_directory [path to output exported model]
```
