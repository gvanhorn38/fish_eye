from absl import app
from absl import flags
import cv2 as cv
import glob
import os

flags.DEFINE_string(
    'input', None, 'Path to a video or a sequence of image.'
)
flags.DEFINE_integer(
    'threshold', 22, 'Location of XML annotations (default is nested in clips).'
)
flags.DEFINE_string(
    'framedir_name', 'frames', 'Name of folder containing frames (eg. frames, frames-bs).'
)
FLAGS = flags.FLAGS

def main(argv):
    for directory in os.listdir(FLAGS.input):
        backSub = cv.createBackgroundSubtractorMOG2(1000, FLAGS.threshold)
        
        clipdir = os.path.join(FLAGS.input, directory)
        framedir = os.path.join(clipdir, FLAGS.framedir_name, '')
        newframedir = os.path.join(clipdir, FLAGS.framedir_name.rstrip('/') + '-bs/')
        print(clipdir, framedir, newframedir)
        if not os.path.exists(newframedir):
            os.mkdir(newframedir)

        # Populate backSub history
        for i in range(len(os.listdir(framedir))):
            frame = str(i) + '.jpg'
            fgMask = backSub.apply(cv.imread(framedir + frame))

        # Save file
        for i in range(len(os.listdir(framedir))):
            frame = str(i) + '.jpg'
            fgMask = backSub.apply(cv.imread(framedir + frame))
            cv.imwrite(newframedir + frame, fgMask)
        print(directory)

if __name__ == '__main__':
    app.run(main)