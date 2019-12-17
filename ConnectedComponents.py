#from __future__ import absolute_import, division, print_function, unicode_literals
import cv2 as cv
import numpy as np
from PIL import Image
import math

# Read the image you want connected components of
src = cv.imread('../../FCV/EIP/io/eip_original-t1.png')
# Threshold it so it becomes binary
ret, thresh = cv.threshold(src,0,255,cv.THRESH_BINARY)
# You need to choose 4 or 8 for connectivity type
connectivity = 4
# Perform the operation
output = cv.connectedComponentsWithStats(thresh, connectivity, cv.CV_32S)
# Get the results
# The first cell is the number of labels
num_labels = output[0]
# The second cell is the label matrix
labels = output[1]
# The third cell is the stat matrix
stats = output[2]
# The fourth cell is the centroid matrix
centroids = output[3]

#Labels is a matrix the size of the input image where each element has a value equal to its label.

#Stats is a matrix of the stats that the function calculates. It has a length equal to the number of labels and a width equal to t
he number of stats. It can be used with the OpenCV documentation for it:

#Statistics output for each label, including the background label, see below for available statistics. Statistics are accessed via
 stats[label, COLUMN] where available columns are defined below.

#cv2.CC_STAT_LEFT The leftmost (x) coordinate which is the inclusive start of the bounding box in the horizontal direction.
#cv2.CC_STAT_TOP The topmost (y) coordinate which is the inclusive start of the bounding box in the vertical direction.
#cv2.CC_STAT_WIDTH The horizontal size of the bounding box
#cv2.CC_STAT_HEIGHT The vertical size of the bounding box
#cv2.CC_STAT_AREA The total area (in pixels) of the connected component
#Centroids is a matrix with the x and y locations of each centroid. The row in this matrix corresponds to the label number.
