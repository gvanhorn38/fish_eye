"use strict";

class FramesManager {
  constructor() {
    this.frames = {
      totalFrames: () => { return 0; }
    };
    this.onReset = [];
  }

  set(frames) {
    this.frames = frames;
    for (let i = 0; i < this.onReset.length; i++) {
      this.onReset[i]();
    }
  }
}

function blobToImage(blob) {
  return new Promise((result, _) => {
    let img = new Image();
    img.onload = function() {
      result(img);
      URL.revokeObjectURL(this.src);
    };
    img.src = URL.createObjectURL(blob);
  });
}

function getDate() {
  var today = new Date();
  var dd = String(today.getDate()).padStart(2, '0');
  var mm = String(today.getMonth() + 1).padStart(2, '0');
  var yyyy = today.getFullYear();
  today = mm + '/' + dd + '/' + yyyy;
  return today;
}

/**
 * Extracts the frame sequence from a previously generated zip file.
 */
function extractFramesFromZip(config, file) {
  return new Promise((resolve, _) => {
    JSZip
      .loadAsync(file)
      .then((zip) => {
        let totalFrames = 0;
        for (let i = 0; ; i++) {
          let file = zip.file(i + config.imageExtension);
          if (file == null) {
            totalFrames = i;
            break;
          }
        }

        resolve({
          totalFrames: () => { return totalFrames; },
          getFrame: (frameNumber) => {
            return new Promise((resolve, _) => {
              let file = zip.file(frameNumber + config.imageExtension);
              file
                .async('arraybuffer')
                .then((content) => {
                  let blob = new Blob([ content ], {type: config.imageMimeType});
                  resolve(blob);
                });
            });
          }
        });
      });
  });
}

/**
 * Represents the coordinates of a bounding box
 */
class BoundingBox {
  constructor(x, y, width, height) {
    this.x = x;
    this.y = y;
    this.width = width;
    this.height = height;
  }
}

/**
 * Represents a bounding box at a particular frame.
 */
class AnnotatedFrame {
  constructor(frameNumber, bbox, isGroundTruth, stationaryCount) {
    this.frameNumber = frameNumber;
    this.bbox = bbox;
    this.isGroundTruth = isGroundTruth;
    this.stationaryCount = stationaryCount;
  }

  isVisible() {
    return this.bbox != null;
  }

  isStationary() {
    return this.stationaryCount % 5 != 0;
  }
}

/**
 * Represents an object bounding boxes throughout the entire frame sequence.
 */
class AnnotatedObject {
  constructor() {
    this.frames = [];
  }

  add(frame) {
    for (let i = 0; i < this.frames.length; i++) {
      if (this.frames[i].frameNumber == frame.frameNumber) {
        this.frames[i] = frame;
        return;
      } else if (this.frames[i].frameNumber > frame.frameNumber) {
        this.frames.splice(i, 0, frame);
        this.injectInvisibleFrameAtOrigin();
        return;
      }
    }

    this.frames.push(frame);
    this.injectInvisibleFrameAtOrigin();
  }

  get(frameNumber) {
    for (let i = 0; i < this.frames.length; i++) {
      let currentFrame = this.frames[i];
      if (currentFrame.frameNumber == frameNumber) {
        return currentFrame;
      } else if (currentFrame.frameNumber > frameNumber) {
        break;
      }
    }
    return null;
  }

  injectInvisibleFrameAtOrigin() {
    if (this.frames.length == 0 || this.frames[0].frameNumber > 0) {
      this.frames.splice(0, 0, new AnnotatedFrame(0, null, false, 0));
    }
  }
}

/**
 * Tracks annotated objects throughout a frame sequence.
 */
class AnnotatedObjectsTracker {
  constructor(framesManager) {
    this.framesManager = framesManager;
    this.annotatedObjects = [];
    this.lastFrame = -1;
    this.ctx = document.createElement('canvas').getContext('2d');

    this.framesManager.onReset.push(() => {
      this.annotatedObjects = [];
      this.lastFrame = -1;
    });
  }

  getFrameWithObjects(frameNumber) {
    return new Promise((resolve, _) => {
      let i = this.startFrame(frameNumber);

      let trackNextFrame = () => {
        this.track(i).then((frameWithObjects) => {
          if (i == frameNumber) {
            resolve(frameWithObjects);
          } else {
            i++;
            trackNextFrame();
          }
        });
      };

      trackNextFrame();
    });
  }

  startFrame(frameNumber) {
    for (; frameNumber >= 0; frameNumber--) {
      let allObjectsHaveData = true;

      for (let i = 0; i < this.annotatedObjects.length; i++) {
        let annotatedObject = this.annotatedObjects[i];
        if (annotatedObject.get(frameNumber) == null) {
          allObjectsHaveData = false;
          break;
        }
      }

      if (allObjectsHaveData) {
        return frameNumber;
      }
    }

    throw 'corrupted object annotations';
  }

  track(frameNumber) {
    return new Promise((resolve, _) => {
      this.framesManager.frames.getFrame(frameNumber).then((blob) => {
        blobToImage(blob).then((img) => {
          let result = [];
          for (let i = 0; i < this.annotatedObjects.length; i++) {
            let annotatedObject = this.annotatedObjects[i];
            let annotatedFrame = annotatedObject.get(frameNumber);
            if (annotatedFrame == null) {
              let lastAnnotatedFrame = annotatedObject.get(frameNumber - 1);
              let stationaryCount = 0;
              if (annotatedObject.stationary == 1) {
                stationaryCount = lastAnnotatedFrame.stationaryCount + 1;
              }
              annotatedFrame = new AnnotatedFrame(frameNumber, lastAnnotatedFrame.bbox, false, stationaryCount);
              if (annotatedFrame == null) {
                throw 'tracking must be done sequentially';
              }
              annotatedObject.add(annotatedFrame);
            }
            result.push({annotatedObject: annotatedObject, annotatedFrame: annotatedFrame});
          }
          resolve({img: img, objects: result});
        });
      });
    });
  }
};
