import argparse, json, math, os, sys
import random

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

import numpy as np

# Annotation colors
colors = ('r', 'b', 'g', 'c', 'm', 'y', 'k', 'w')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('frames', type=str, help='directory containing image frames labeled beginning at 0')
    parser.add_argument('json', type=str, help='a json file containing annotations')
    parser.add_argument('--sort', type=str, choices=['diagonal', 'width'], help='sort files by annotation length')
    #parser.add_argument('-s', '--save', type=str, help='save')

    args = parser.parse_args()

    assert os.path.exists(args.frames), '%s does not exist' % args.frames
    #assert args.save is None or os.path.exists(args.save), '%s does not exist' % args.save

    annotations = {}
    pixel_meter_size = -1
    clip_dim = []
    # Collect annotations from json file, but don't draw
    with open(args.json) as json_file:
        json_data = json.load(json_file)
        pixel_meter_size = json_data['info']['pixel_meter_size']
        clip_dim = json_data['info']['clip_dim']
        for annotation in json_data['annotations']:
            # The annotations in the json only have an image_id, not
            # the filename of the image, so in order to find the
            # matching frames we search for the image that contains
            # the matching id tag in the json and take it's file_name
            # attribute.
            image_id = annotation['image_id']
            file_name = ''
            for image in json_data['images']:
                if image['id'] == image_id:
                    file_name = image['file_name']
                    break
            # Possibly faster to only look up the first one and
            # then add one each time to get the file name since
            # annotations in a file should be in order?

            bbox = annotation['bbox']
            
            # Translate upper left to bottom left
            bbox[1] += bbox[3];

            annotations[file_name] = bbox

    index = 0
    if args.sort == 'diagonal':
        file_names = [ item[0] for item in sorted(annotations.items(), key=lambda kv: math.sqrt(kv[1][2]*kv[1][2] + kv[1][3]*kv[1][3]), reverse=True) ]
    elif args.sort == 'width':
        file_names = [ item[0] for item in sorted(annotations.items(), key=lambda kv: kv[1][2], reverse=True) ]
    else:
        file_names = list(annotations.keys())

    lines = {}

    # Stage image and annotations
    def draw_image_with_annotations(file_name):
        image_path = os.path.join(args.frames, file_names[index])
        if os.path.exists(image_path):
            ax.cla()
            image = Image.open(image_path)
            ax.imshow(np.array(image))
            image.close()
            if file_name in lines:
                plt.plot(lines[file_name][0], lines[file_name][1], color='r')
                ax.figure.canvas.draw()
        else:
            sys.stderr.write(image_path + 'does not exist.\n')

    def key_event(e):
        nonlocal index, file_names

        if e.key == 'right':
            index += 1
        elif e.key == 'left':
            index -= 1
        # Line segment drawer.  Click two points after hitting 'n'.
        elif e.key == 'n':
            ax = plt.gca()
            xy = plt.ginput(2)

            x = [p[0] for p in xy]
            y = [p[1] for p in xy]
            line = plt.plot(x,y)
            ax.figure.canvas.draw()

            lines[file_names[index]] = (x, y)
        elif e.key == 'q':
            max_length = 0.0
            for line in lines.values():
                max_length = max(max_length, math.sqrt((line[0][0] - line[0][1])**2 + (line[1][0] - line[1][1])**2))
            print(max_length*pixel_meter_size)
            exit()
        else:
            return
        index %= len(file_names)
        draw_image_with_annotations(file_names[index])
        fig.canvas.draw()

    fig = plt.figure()
    fig.canvas.mpl_connect('key_press_event', key_event)
    ax = fig.add_subplot(111)

    draw_image_with_annotations(file_names[index])
    plt.pause(1)
    plt.show()

if __name__ == '__main__':
    main()
