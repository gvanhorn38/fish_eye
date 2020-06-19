from absl import app
from absl import flags
import json
import os

flags.DEFINE_string(
	'input_dir', None, 'Path to directory of json files to be combined.'
)
flags.DEFINE_string(
	'output_path', None, 'Path to output combined json.'
)
flags.mark_flag_as_required('input_dir')
flags.mark_flag_as_required('output_path')
FLAGS = flags.FLAGS

def main(argv):
	total = []
	for file in os.listdir(FLAGS.input_dir):
		total += json.load(open(os.path.join(FLAGS.input_dir, file)))
	json.dump(total, open(FLAGS.output_path, 'w'), default=str, indent=2)
	
if __name__ == '__main__':
	app.run(main)