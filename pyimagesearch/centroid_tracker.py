'''
Creates a simple tracker class using a centroid tracking algorithm 
(taken and modified from pyimagesearch.com)
'''

# import the necessary packages
from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np

class CentroidTracker():
	def __init__(self, width, height, maxDisappeared=10):
		# initialize the next unique object ID along with two ordered
		# dictionaries used to keep track of mapping a given object
		# ID to its centroid and number of consecutive frames it has
		# been marked as "disappeared", respectively
		self.nextObjectID = 0
		self.objects = OrderedDict()
		self.disappeared = OrderedDict()
		self.numFrames = OrderedDict()

		# store the number of maximum consecutive frames a given
		# object is allowed to be marked as "disappeared" until we
		# need to deregister the object from tracking
		self.maxDisappeared = maxDisappeared

		# stores the width and height dimensions of the frames
		self.width = width
		self.height = height

		# keeps track of when fish enters and leaves
		self.track = {"enter": '', "exit": ''}

		# counts the number of "left" stream and "right" stream fish:
		self.counts = {"left": 0, "right": 0, "NA": 0}

		# # counts the number of frames the track has
		# self.numFrames = 0

	def getCounts(self):
		return self.counts

	# This function checks if there are any remaining fish not deregistered.
	def getRemainingFish(self):
		leftoverCounts = {"right": 0, "left": 0, "NA": 0}
		for key, value in self.objects:
			# If valid fish track
			if self.numFrames[key] > 5:
				if self.objects[key][0] < self.width / 2:
					self.track['exit'] = 'L'
				else:
					self.track['exit'] = 'R'

				if self.track['enter'] == 'L' and self.track['exit'] == 'R':
					leftoverCounts['right'] += 1
				elif self.track['enter'] == 'R' and self.track['exit'] == 'L':
					leftoverCounts['left'] += 1
				else:
					if self.numFrames[key] > 25:
						leftoverCounts['NA'] += 1

			del self.object[key]
			del self.disappeared[key]
			del self.numFrames[key]

		return leftoverCounts


	def register(self, centroid):
		# when registering an object we use the next available object
		# ID to store the centroid
		# print("START:")
		# print(centroid)
		# print("id:", self.nextObjectID)
		if centroid[0] < self.width / 2:
			self.track['enter'] = 'L'
		else:
			self.track['enter'] = 'R'

		self.objects[self.nextObjectID] = centroid
		self.disappeared[self.nextObjectID] = 0
		self.numFrames[self.nextObjectID] = 1
		self.nextObjectID += 1

	def deregister(self, objectID):
		# to deregister an object ID we delete the object ID from
		# both of our respective dictionaries
		# print("END:")
		# print(self.objects[objectID])
		# print(self.numFrames[objectID])
		
		# Setting some minimum number of frames required to be counted as a track
		if self.numFrames[objectID] > 5:
			if self.objects[objectID][0] < self.width / 2:
				self.track['exit'] = 'L'
			else:
				self.track['exit'] = 'R'
			if self.track['enter'] == 'L' and self.track['exit'] == 'R':
				self.counts['right'] += 1
			elif self.track['enter'] == 'R' and self.track['exit'] == 'L':
				self.counts['left'] += 1
			else:
				if self.numFrames[objectID] > 25:
					self.counts['NA'] += 1
			print(objectID)
			print(self.track)
			print(self.counts)
			print()

		else:
			print()

		del self.objects[objectID]
		del self.disappeared[objectID]
		del self.numFrames[objectID]

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
		inputCentroids = np.zeros((len(rects), 2), dtype="int")

		# loop over the bounding box rectangles
		for (i, (startX, startY, deltaX, deltaY)) in enumerate(rects):
			# use the bounding box coordinates to derive the centroid
			cX = int(startX + deltaX / 2.0)
			cY = int(startY + deltaY / 2.0)
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

				# if the distance between the object centroid and its
				# new centroid is greater than 200 pixels, the new
				# bbox is probably not of the same track. Ignore it.
				if D[row][col] > 200:
					continue
				
				# otherwise, grab the object ID for the current row,
				# set its new centroid, increase the number of tracks,
				# and reset the disappeared counter.
				objectID = objectIDs[row]
				self.objects[objectID] = inputCentroids[col]
				self.numFrames[objectID] += 1
				# print("centroid:")
				# print(self.objects[objectID])
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