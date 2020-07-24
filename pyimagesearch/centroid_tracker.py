'''
Creates a simple tracker class using a centroid tracking algorithm 
(taken and modified from pyimagesearch.com)
'''

# import the necessary packages
from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np

class CentroidTracker():
	def __init__(self, width, height, maxDist=0.25, maxDisappeared=10, minFrames=5, minOtherFrames=20):
		# initialize the next unique fish ID along with two ordered
		# dictionaries used to keep track of mapping a given fish
		# ID to its centroid and number of consecutive frames it has
		# been marked as "disappeared", respectively
		self.nextObjectID = 0
		self.objects = OrderedDict()
		self.disappeared = OrderedDict()
		self.numFrames = OrderedDict()
		self.tracks = OrderedDict() # number of frames for each track

		# The maximum distance (normalized) that consecutive frames can
		# be from each other
		self.maxDist = maxDist

		# store the number of maximum consecutive frames a given
		# fish is allowed to be marked as "disappeared" until we
		# need to deregister the fish from tracking
		self.maxDisappeared = maxDisappeared

		# store the minimum number of consecutive frames a given
		# track must have to be counted as a valid fish
		self.minFrames = minFrames

		# store the minimum number of consecutive frames a stationary
		# fish track must contain to be counted
		self.minOtherFrames = minOtherFrames

		# stores the width and height dimensions of the frames
		self.width = width
		self.height = height

		# keeps track of when fish enters and leaves
		self.track = {'enter': '', 'exit': ''}

		# counts the number of "left" stream and "right" stream fish:
		self.counts = {'left': 0, 'right': 0, 'other': 0}


	def getCounts(self):
		return self.counts

	# This function checks if there are any remaining fish not deregistered.
	def getRemainingFish(self):
		leftoverCounts = {'right': 0, 'left': 0, 'other': 0}
		for key, value in self.objects.items():
			# If valid fish track
			if self.numFrames[key] > self.minFrames:
				if self.objects[key][0] < self.width / 2:
					self.track['exit'] = 'L'
				else:
					self.track['exit'] = 'R'

				if self.track['enter'] == 'L' and self.track['exit'] == 'R':
					leftoverCounts['right'] += 1
				elif self.track['enter'] == 'R' and self.track['exit'] == 'L':
					leftoverCounts['left'] += 1
				else:
					if self.numFrames[key] > self.minOtherFrames:
						leftoverCounts['other'] += 1

		return leftoverCounts


	def register(self, centroid):
		# when registering an object we use the next available object
		# ID to store the centroid
		entrance = ''
		if centroid[0] < self.width / 2:
			entrance = 'L'
		else:
			entrance = 'R'

		self.objects[self.nextObjectID] = centroid
		self.disappeared[self.nextObjectID] = 0
		self.numFrames[self.nextObjectID] = 1
		self.tracks[self.nextObjectID] = {'enter': entrance}
		self.nextObjectID += 1

	def deregister(self, objectID):
		# to deregister an object ID we delete the object ID from
		# both of our respective dictionaries
		
		# Setting some minimum number of frames required to be counted as a track
		if self.numFrames[objectID] > self.minFrames:
			if self.objects[objectID][0] < self.width / 2:
				self.tracks[objectID]['exit'] = 'L'
			else:
				self.tracks[objectID]['exit'] = 'R'
			
			if self.tracks[objectID]['enter'] == 'L' and self.tracks[objectID]['exit'] == 'R':
				self.counts['right'] += 1
			elif self.tracks[objectID]['enter'] == 'R' and self.tracks[objectID]['exit'] == 'L':
				self.counts['left'] += 1
			else:
				if self.numFrames[objectID] > self.minOtherFrames:
					self.counts['other'] += 1

		del self.objects[objectID]
		del self.disappeared[objectID]
		del self.numFrames[objectID]
		del self.tracks[objectID]

	def update(self, rects):
		# check to see if the list of input bounding box rectangles
		# is empty
		if len(rects) == 0:
			# loop over any existing tracked objects and mark them
			# as disappeared
			for objectID in list(self.disappeared.keys()):
				self.disappeared[objectID] += 1

				# if we have reached a maximum number of consecutive
				# frames where a given object has been marked as
				# missing, deregister it
				if self.disappeared[objectID] > self.maxDisappeared:
					self.deregister(objectID)

			# return early as there are no centroids or tracking info
			# to update
			return self.objects

		# initialize an array of input centroids for the current frame
		inputCentroids = np.zeros((len(rects), 2), dtype='float')

		# loop over the bounding box rectangles
		for (i, (startX, startY, deltaX, deltaY)) in enumerate(rects):
			# use the bounding box coordinates to derive the centroid
			cX = startX + deltaX / 2.0
			cY = startY + deltaY / 2.0
			inputCentroids[i] = (cX, cY)

		# if we are currently not tracking any objects take the input
		# centroids and register each of them
		if len(self.objects) == 0:
			for i in range(0, len(inputCentroids)):
				self.register(inputCentroids[i])

		# otherwise, we are currently tracking objects so we need to
		# try to match the input centroids to existing object
		# centroids
		else:
			# grab the set of object IDs and corresponding centroids
			objectIDs = list(self.objects.keys())
			objectCentroids = list(self.objects.values())

			# compute the distance between each pair of object
			# centroids and input centroids, respectively -- our
			# goal will be to match an input centroid to an existing
			# object centroid
			D = dist.cdist(np.array(objectCentroids), inputCentroids)

			# in order to perform this matching we must (1) find the
			# smallest value in each row and then (2) sort the row
			# indexes based on their minimum values so that the row
			# with the smallest value is at the *front* of the index
			# list
			rows = D.min(axis=1).argsort()

			# next, we perform a similar process on the columns by
			# finding the smallest value in each column and then
			# sorting using the previously computed row index list
			cols = D.argmin(axis=1)[rows]

			# in order to determine if we need to update, register,
			# or deregister an object we need to keep track of which
			# of the rows and column indexes we have already examined
			usedRows = set()
			usedCols = set()

			# loop over the combination of the (row, column) index
			# tuples
			for (row, col) in zip(rows, cols):
				# if we have already examined either the row or
				# column value before, ignore it
				# val
				if row in usedRows or col in usedCols:
					continue

				# if the distance between the fish centroid and its
				# new centroid is greater than maxDist, the new
				# bbox is probably not of the same track. Ignore it.
				if D[row][col] > self.maxDist:
					continue
				
				# otherwise, grab the object ID for the current row,
				# set its new centroid, increase the number of tracks,
				# and reset the disappeared counter.
				objectID = objectIDs[row]
				self.objects[objectID] = inputCentroids[col]
				self.numFrames[objectID] += 1
				self.disappeared[objectID] = 0

				# indicate that we have examined each of the row and
				# column indexes, respectively
				usedRows.add(row)
				usedCols.add(col)

			# compute both the row and column index we have NOT yet
			# examined
			unusedRows = set(range(0, D.shape[0])).difference(usedRows)
			unusedCols = set(range(0, D.shape[1])).difference(usedCols)

			# if number of object centroids >= number of input centroids,
			# need to check and see if some of these objects have 
			# potentially disappeared
			if D.shape[0] >= D.shape[1]:
				# loop over the unused row indexes
				for row in unusedRows:
					# grab the object ID for the corresponding row
					# index and increment the disappeared counter
					objectID = objectIDs[row]
					self.disappeared[objectID] += 1

					# check to see if the number of consecutive
					# frames the object has been marked "disappeared"
					# for warrants deregistering the object
					if self.disappeared[objectID] > self.maxDisappeared:
						self.deregister(objectID)

			# otherwise, if the number of input centroids is greater
			# than the number of existing object centroids we need to
			# register each new input centroid as a trackable object
			else:
				for col in unusedCols:
					self.register(inputCentroids[col])

		# return the set of trackable objects
		return self.objects