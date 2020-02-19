import argparse
import cv2 as cv
import glob
import os

parser = argparse.ArgumentParser()
parser.add_argument('--input', type=str, help='Path to a video or a sequence of image.', default='vtest.avi')
parser.add_argument('--algo', type=str, help='Background subtraction method (KNN, MOG2).', default='MOG2')
parser.add_argument('--threshold', type=int, default=16)
parser.add_argument('--framedir_name', type=str, default='frames', help='name of folder containing frames (eg. frames, frames-bs)')
args = parser.parse_args()

for directory in os.listdir(args.input):
    backSub = cv.createBackgroundSubtractorMOG2(500, 22)
    
    clipdir = args.input + directory
    framedir = os.path.join(clipdir, args.framedir_name, '')
    newframedir = os.path.join(clipdir, args.framedir_name.strip('/') + '-bs/')

    if not os.path.exists(newframedir):
        os.mkdir(newframedir)
    # Populate backSub history
    for i in range(len([_ for _ in os.listdir(framedir)])):
        frame = str(i) + '.jpg'
        fgMask = backSub.apply(cv.imread(framedir + frame))
    # Save file
    for i in range(len([_ for _ in os.listdir(framedir)])):
        frame = str(i) + '.jpg'
        fgMask = backSub.apply(cv.imread(framedir + frame))
        cv.imwrite(newframedir + frame, fgMask)
    print(directory)