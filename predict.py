from absl import app
from absl import flags
import json
import os
from pathlib import Path
import tensorflow as tf

flags.DEFINE_string(
    'path_to_frozen_graph', None, 'Path to frozen_inference_graph.pb.'
)
flags.DEFINE_string(
    'path_to_image_dir', None, 
    '''
    Path to image directory if no json provided.
    Can be either the directory directly containing images or directory with contents:
    $path_to_image_dir/
    └── */
        └── $framedir_name/
            └── *.jpg
    '''
)
flags.DEFINE_string(
    'path_to_json', None, 'Path to json or directory of jsons, if no image directory provided.'
)
flags.DEFINE_string(
    'path_to_output_dir', None, 'Directory to output json.'
)
flags.DEFINE_string(
    'framedir_name', '', 'Name of subfolder containing images or \'\' otherwise.'
)
flags.DEFINE_string(
    'output_json_name', None, 'Optional output name for a batch of files. \
                        Only useful if there is a single json or folder of images.'
)
flags.DEFINE_bool(
	'verbose', False, 'Adds extra debugging information.'
)
# TODO
# flags.DEFINE_integer(
#     'batch_size', 20, 'Number of images to be processed at once.'
# )
flags.mark_flag_as_required('path_to_frozen_graph')
FLAGS = flags.FLAGS

IMG_HEIGHT = 600
IMG_WIDTH = 300

def main(argv):
    assert bool(FLAGS.path_to_image_dir) ^ bool(FLAGS.path_to_json), \
                        'Must define either path_to_image_dir or path_to_json.'

    assert bool(FLAGS.path_to_output_dir) ^ bool(FLAGS.output_json_name), \
                        'Must define either path_to_output_dir or output_json_name.'
    
    clips = {}
    if FLAGS.path_to_json is not None:
        assert os.path.exists(FLAGS.path_to_json), 'path_to_json_dir does not exist.'

        # Is a single json
        if os.path.isfile(FLAGS.path_to_json):
            jsons = Path(FLAGS.path_to_json)
        # Is a directory containing jsons
        else:
            jsons = Path(FLAGS.path_to_json).glob('*.json')
        
        for json_file in jsons:
            with open(json_file) as file:
                clips[json_file.name] = [annotation['filename'] for annotation in json.load(file)]

    if FLAGS.path_to_image_dir is not None:
        assert os.path.exists(FLAGS.path_to_image_dir), 'path_to_image_dir does not exist.'

        # Is path_to_image_dir terminal
        if os.path.exists(os.path.join(FLAGS.path_to_image_dir, '0.jpg')):
            folders = Path(FLAGS.path_to_image_dir)
        else:
            folders = [f for f in Path(FLAGS.path_to_image_dir).iterdir() if f.is_dir()]
        
        for folder in folders:
            clips[folder.name + '.json'] = Path(os.path.join(folder, FLAGS.framedir_name)).glob('*')

    # Path to frozen detection graph. This is the actual model that is used for the object detection.
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(FLAGS.path_to_frozen_graph, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

        with tf.Session() as sess:
            tf.compat.v1.enable_eager_execution()
            image_tensor = tf.compat.v1.get_default_graph().get_tensor_by_name('image_tensor:0')

            tensor_dict = {}
            for key in ['num_detections', 'detection_boxes', 'detection_scores']:
                tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(key + ':0')

            for output_name, frames in clips.items():
                predictions = []

                for image_path in frames:
                    image_path = str(image_path)
                    if FLAGS.verbose:
                        print(image_path)

                    img = tf.io.read_file(image_path)
                    img = tf.image.decode_jpeg(img, channels=3)
                    height, width, _ = img.shape
                    img = tf.image.resize(img, [IMG_HEIGHT, IMG_WIDTH]).numpy()[tf.newaxis]

                    # Run inference
                    output_dict = sess.run(tensor_dict, feed_dict={image_tensor: img})
                    bboxes = output_dict['detection_boxes'][0][:int(output_dict['num_detections'][0])].tolist()
                    scores = output_dict['detection_scores'][0][:int(output_dict['num_detections'][0])].tolist()

                    prediction = {}
                    prediction['filename'] = image_path
                    prediction['class'] = {
                        'label': 1,
                        'text': 'fish'
                    }
                    prediction['height'] = int(height)
                    prediction['width'] = int(width)
                    prediction['object'] = {
                        'bbox': {
                            'xmin': [],
                            'xmax': [],
                            'ymin': [],
                            'ymax': [],
                            'label': [],
                            'score': []
                        },
                        'count': len(bboxes)
                    }

                    for bbox, score in zip(bboxes, scores):
                        prediction['object']['bbox']['xmin'].append(bbox[1])
                        prediction['object']['bbox']['xmax'].append(bbox[3])
                        prediction['object']['bbox']['ymin'].append(bbox[0])
                        prediction['object']['bbox']['ymax'].append(bbox[2])
                        prediction['object']['bbox']['label'].append(1)
                        prediction['object']['bbox']['score'].append(score)
                    print(prediction)
                    predictions.append(prediction)

                predictions = sorted(predictions, key=lambda x: int(Path(x['filename']).stem))

                if FLAGS.output_json_name is not None:
                    with open(FLAGS.output_json_name, 'w') as output:
                        json.dump(predictions, output, indent=2)
                    return
                else:
                    print(os.path.join(FLAGS.path_to_output_dir, output_name))
                    with open(os.path.join(FLAGS.path_to_output_dir, output_name), 'w') as output:
                        json.dump(predictions, output, indent=2)

if __name__ == '__main__':
  app.run(main)