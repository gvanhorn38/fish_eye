import json
import numpy as np
import os
import tensorflow as tf

from PIL import Image

from absl import app
from absl import flags

flags.DEFINE_string(
    'path_to_frozen_graph', None, 'Path to frozen_inference_graph.pb.')
flags.DEFINE_string(
    'path_to_image_dir', None, 'Path to image directory.')
FLAGS = flags.FLAGS

def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)

def main(argv):
  flags.mark_flag_as_required('path_to_frozen_graph')
  flags.mark_flag_as_required('path_to_image_dir')

  # Path to frozen detection graph. This is the actual model that is used for the object detection.
  PATH_TO_FROZEN_GRAPH = FLAGS.path_to_frozen_graph

  detection_graph = tf.Graph()
  with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
      serialized_graph = fid.read()
      od_graph_def.ParseFromString(serialized_graph)
      tf.import_graph_def(od_graph_def, name='')

  # If you want to test the code with your images, just add path to the images to the TEST_IMAGE_PATHS.
  PATH_TO_TEST_IMAGES_DIR = FLAGS.path_to_image_dir

  TEST_IMAGE_PATHS = sorted(os.listdir(PATH_TO_TEST_IMAGES_DIR), key=lambda x: int(os.path.splitext(x)[0]))

  predictions = []

  with detection_graph.as_default():
    with tf.Session() as sess:
      image_tensor = tf.compat.v1.get_default_graph().get_tensor_by_name('image_tensor:0')
      for image_name in TEST_IMAGE_PATHS:
        image_path = os.path.join(PATH_TO_TEST_IMAGES_DIR, image_name)
        image = Image.open(image_path)
        # the array based representation of the image will be used later in order to prepare the
        # result image with boxes and labels on it.
        image_np = load_image_into_numpy_array(image)
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image_np, axis=0)

        tensor_dict = {}
        for key in ['num_detections', 'detection_boxes']:
          tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(key + ':0')

        # Run inference
        output_dict = sess.run(tensor_dict, feed_dict={image_tensor: image_np_expanded})
        bboxes = output_dict['detection_boxes'][0][:int(output_dict['num_detections'][0])].tolist()

        prediction = {}
        prediction['filename'] = image_path
        prediction['class'] = {
          'label': 1,
          'text': 'fish'
        }
        prediction['object'] = {
          'bbox': {
            'xmin': [],
            'xmax': [],
            'ymin': [],
            'ymax': [],
            'label': []
          },
          'count': len(bboxes)
        }

        for bbox in bboxes:
          prediction['object']['bbox']['xmin'].append(bbox[0])
          prediction['object']['bbox']['xmax'].append(bbox[1])
          prediction['object']['bbox']['ymin'].append(bbox[2])
          prediction['object']['bbox']['ymax'].append(bbox[3])
          prediction['object']['bbox']['label'].append(1)
        predictions.append(prediction)
  with open('./predictions.json' , 'w') as output:
    json.dump(predictions, output)

if __name__ == '__main__':
  app.run(main)