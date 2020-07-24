from absl import app
from absl import flags
import cv2 as cv
import numpy as np
import os

flags.DEFINE_string(
    'input', None, 'Path to a video or a sequence of image.'
)
flags.DEFINE_string(
    'framedir_name', 'frames', 'Name of folder containing frames (eg. frames, frames-bs).'
)
FLAGS = flags.FLAGS

def main(argv):
    for directory in os.listdir(FLAGS.input):
        backSubs = [cv.createBackgroundSubtractorKNN(1000, 200),
                    cv.createBackgroundSubtractorMOG2(1000, 22),
                    cv.createBackgroundSubtractorMOG2(1000, 15)]
        
        clipdir = os.path.join(FLAGS.input, directory)
        framedir = os.path.join(clipdir, FLAGS.framedir_name, '')
        newframedir = os.path.join(clipdir, FLAGS.framedir_name.rstrip('/') + '-bs/')
        
        if not os.path.exists(newframedir):
            os.mkdir(newframedir)

        # Populate backSub history
        for i in range(len(os.listdir(framedir))):
            frame = str(i) + '.jpg'
            im = cv.imread(framedir + frame)
            for backSub in backSubs:
                backSub.apply(im)

        # Save file
        for i in range(len(os.listdir(framedir))):
            frame = str(i) + '.jpg'
            im = cv.imread(framedir + frame)
            out = []
            for backSub in backSubs:
                out.append(backSub.apply(im))
            cv.imwrite(newframedir + frame, np.dstack(out))
        print(directory)

if __name__ == '__main__':
    app.run(main)
