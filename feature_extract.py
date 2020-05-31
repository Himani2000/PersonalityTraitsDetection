import pandas as pd
import numpy as np
import os
import cv2
import imutils
import preprocess
import math

ANCHOR_POINT = 6000
MIDZONE_THRESHOLD = 15000
MIN_HANDWRITING_HEIGHT_PIXEL = 20


def straighten(image):

	global BASELINE_ANGLE

	angle = 0.0
	angle_sum = 0.0
	countour_count = 0


	# filtered = bilateralFilter(image, 3)
	# cv2.imshow('filtered',filtered)
	# convert to grayscale and binarize the image by INVERTED binary thresholding
	thresh = preprocess.threshold(image, 120)
	kernel = np.ones((2,2))
	#cv2.imshow('thresh',thresh)
	#cv2.waitKey(0)
	mat = preprocess.horizontalProjection(thresh)
	img_w = thresh.shape[1]
	#print("width: ", img_w)
	#print(type(thresh),thresh.shape)

	for i in range(len(mat)):
	# 	print(mat[i]/255)
	 	if (mat[i]/255.0) < (img_w/70.0):                 # Mat is sum of pixels in each row. Divide by 255 to get number of black lines
	 		for j in range(thresh[i].shape[0]):
	 			thresh[i][j] = 0
	#cv2.imshow('thresh', thresh)
	#cv2.waitKey(0)
	dil = 50
	dilated = preprocess.dilate(thresh, (5, dil))
	#cv2.imshow('Dilated', dilated)
	#cv2.waitKey(0)
	while(True):
		ctrs, heirarchy = cv2.findContours(dilated.copy(), cv2.RETR_TREE ,cv2.CHAIN_APPROX_SIMPLE)[-2:]
		if len(ctrs) > 3:
			break
		dil -= 5
		dilated = preprocess.dilate(thresh, (5, dil))
	#print(len(ctrs))
	for i, ctr in enumerate(ctrs):
		x, y, w, h = cv2.boundingRect(ctr)
	#	print(x,y,w,h)
		# We can be sure the contour is not a line if height > width or height is < 20 pixels. Here 20 is arbitrary.
		if h < 5:
			continue
		# We extract the region of interest/contour to be straightened.
		roi = image[y:y+h, x:x+w]
		#rows, cols = ctr.shape[:2]
		# If the length of the line is less than half the document width, especially for the last line,
		# ignore because it may yeild inacurate baseline angle which subsequently affects proceeding features.
		if w < image.shape[1]/7 :
			roi = 255
			image[y:y+h, x:x+w] = roi
			continue

		# minAreaRect is necessary for straightening
		rect = cv2.minAreaRect(ctr)
		center = rect[0]
		angle = rect[2]
		#print "original: "+str(i)+" "+str(angle)
		# I actually gave a thought to this but hard to remember anyway!
		if angle < -45.0:
			angle += 90.0;
		#print "+90 "+str(i)+" "+str(angle)
		rot = cv2.getRotationMatrix2D(((x+w)/2,(y+h)/2), angle, 1)
		#extract = cv2.warpAffine(roi, rot, (w,h), borderMode=cv2.BORDER_TRANSPARENT)
		extract = cv2.warpAffine(roi, rot, (w,h), borderMode=cv2.BORDER_CONSTANT, borderValue=(255,255,255))
		#cv2.imshow('warpAffine:'+str(i),extract)
		# image is overwritten with the straightened contour
		image[y:y+h, x:x+w] = extract
		'''
		# Please Ignore. This is to draw visual representation of the contour rotation.
		box = cv2.boxPoints(rect)
		box = np.int0(box)
		cv2.drawContours(display,[box],0,(0,0,255),1)
		cv2.rectangle(display,(x,y),( x + w, y + h ),(0,255,0),1)
		'''
	#	print(angle)
		angle_sum += angle
		countour_count += 1
	'''
		# sum of all the angles of downward baseline
		if(angle>0.0):
			positive_angle_sum += angle
			positive_count += 1
		# sum of all the angles of upward baseline
		else:
			negative_angle_sum += angle
			negative_count += 1

	if(positive_count == 0): positive_count = 1
	if(negative_count == 0): negative_count = 1
	average_positive_angle = positive_angle_sum / positive_count
	average_negative_angle = negative_angle_sum / negative_count
	print "average_positive_angle: "+str(average_positive_angle)
	print "average_negative_angle: "+str(average_negative_angle)

	if(abs(average_positive_angle) > abs(average_negative_angle)):
		average_angle = average_positive_angle
	else:
		average_angle = average_negative_angle

	print "average_angle: "+str(average_angle)
	'''
	#cv2.imshow('countours', display)

	# mean angle of the contours (not lines) is found
	mean_angle = angle_sum/countour_count
	BASELINE_ANGLE = mean_angle
	#print("Average baseline angle: "+str(mean_angle))
	return mean_angle,image



def penpressure(image):
	pen_pressure=0.0
	image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	# inverting the image pixel by pixel individually. This costs the maximum time and processing in the entire process!
	h, w = image.shape[:]
	inverted = image
	for x in range(h):
		for y in range(w):
			inverted[x][y] = 255 - image[x][y]


	# bilateral filtering
	filtered = preprocess.bilateralFilter(inverted, 3)

	# binary thresholding. Here we use 'threshold to zero' which is crucial for what we want.
	# If src(x,y) is lower than threshold=100, the new pixel value will be set to 0, else it will be left untouched!
	ret, thresh = cv2.threshold(filtered, 100, 255, cv2.THRESH_TOZERO)


	# add up all the non-zero pixel values in the image and divide by the number of them to find the average pixel value in the whole image
	total_intensity = 0
	pixel_count = 0
	for x in range(h):
		for y in range(w):
			if(thresh[x][y] > 0):
				total_intensity += thresh[x][y]
				pixel_count += 1

	average_intensity = float(total_intensity) / pixel_count
	pen_pressure= average_intensity
	return pen_pressure



def letterSize(image):
	filtered = preprocess.bilateralFilter(image, 5)

	thresh = preprocess.threshold(filtered, 160)

	# extract a python list containing values of the horizontal projection of the image into 'hp'
	hpList = preprocess.horizontalProjection(thresh)

	indexCount=0
	setLineTop=True
	lines=[]
	lineTop = 0
	lineBottom = 0
	spaceTop = 0
	spaceBottom = 0
	setSpaceTop = True
	includeNextSpace = True
	space_zero = [] # stores the amount of space between lines


	# we are scanning the whole horizontal projection now
	for i, sum in enumerate(hpList):
		# sum being 0 means blank space
		if(sum==0):
			if(setSpaceTop):
				spaceTop = indexCount
				setSpaceTop = False # spaceTop will be set once for each start of a space between lines
			indexCount += 1
			spaceBottom = indexCount
			if(i<len(hpList)-1): # this condition is necessary to avoid array index out of bound error
				if(hpList[i+1]==0): # if the next horizontal projectin is 0, keep on counting, it's still in blank space
					continue
			# we are using this condition if the previous contour is very thin and possibly not a line
			if(includeNextSpace):
				space_zero.append(spaceBottom-spaceTop)
			else:
				if (len(space_zero)==0):
					previous = 0
				else:
					previous = space_zero.pop()
				space_zero.append(previous + spaceBottom-lineTop)
			setSpaceTop = True # next time we encounter 0, it's begining of another space so we set new spaceTop

		# sum greater than 0 means contour
		if(sum>0):
			if(setLineTop):
				lineTop = indexCount
				setLineTop = False # lineTop will be set once for each start of a new line/contour
			indexCount += 1
			lineBottom = indexCount
			if(i<len(hpList)-1): # this condition is necessary to avoid array index out of bound error
				if(hpList[i+1]>0): # if the next horizontal projectin is > 0, keep on counting, it's still in contour
					continue

				# if the line/contour is too thin <10 pixels (arbitrary) in height, we ignore it.
				# Also, we add the space following this and this contour itself to the previous space to form a bigger space: spaceBottom-lineTop.
				if(lineBottom-lineTop<20):
					includeNextSpace = False
					setLineTop = True # next time we encounter value > 0, it's begining of another line/contour so we set new lineTop
					continue
			includeNextSpace = True # the line/contour is accepted, new space following it will be accepted

			# append the top and bottom horizontal indices of the line/contour in 'lines'
			lines.append([lineTop, lineBottom])
			setLineTop = True # next time we encounter value > 0, it's begining of another line/contour so we set new lineTop






	fineLines = [] # a 2D list storing the horizontal start index and end index of each individual line
	for i, line in enumerate(lines):

		anchor = line[0] # 'anchor' will locate the horizontal indices where horizontal projection is > ANCHOR_POINT for uphill or < ANCHOR_POINT for downhill(ANCHOR_POINT is arbitrary yet suitable!)
		anchorPoints = [] # python list where the indices obtained by 'anchor' will be stored
		upHill = True # it implies that we expect to find the start of an individual line (vertically), climbing up the histogram
		downHill = False # it implies that we expect to find the end of an individual line (vertically), climbing down the histogram
		segment = hpList[int(line[0]):int(line[1])] # we put the region of interest of the horizontal projection of each contour here

		for j, sum in enumerate(segment):
			if(upHill):
				if(sum<ANCHOR_POINT):
					anchor += 1
					continue
				anchorPoints.append(anchor)
				upHill = False
				downHill = True
			if(downHill):
				if(sum>ANCHOR_POINT):
					anchor += 1
					continue
				anchorPoints.append(anchor)
				downHill = False
				upHill = True

		#print anchorPoints

		# we can ignore the contour here


		'''
		# the contour turns out to be an individual line
		if(len(anchorPoints)<=3):
			fineLines.append(line)
			continue
		'''
		# len(anchorPoints) > 3 meaning contour composed of multiple lines
		lineTop = line[0]
		for x in range(1, len(anchorPoints)-1, 2):
			# 'lineMid' is the horizontal index where the segmentation will be done
			lineMid = (anchorPoints[x]+anchorPoints[x+1])/2
			lineBottom = lineMid
			# line having height of pixels <20 is considered defects, so we just ignore it
			# this is a weakness of the algorithm to extract lines (anchor value is ANCHOR_POINT, see for different values!)
			if(lineBottom-lineTop < 20):
				continue
			fineLines.append([lineTop, lineBottom])
			lineTop = lineBottom
		if(line[1]-lineTop < 20):
			continue
		fineLines.append([lineTop, line[1]])


	space_nonzero_row_count = 0
	midzone_row_count = 0
	lines_having_midzone_count = 0
	flag = False

	for i, line in enumerate(fineLines):
		segment = hpList[int(line[0]):int(line[1])]
		for j, sum in enumerate(segment):
			if(sum<MIDZONE_THRESHOLD):
				space_nonzero_row_count += 1
			else:
				midzone_row_count += 1
				flag = True

		# This line has contributed at least one count of pixel row of midzone
		if(flag):
			lines_having_midzone_count += 1
			flag = False

	# error prevention ^-^
	if(lines_having_midzone_count == 0): lines_having_midzone_count = 1





	total_space_row_count = space_nonzero_row_count + np.sum(space_zero[1:-1])
	average_line_spacing = float(total_space_row_count) / lines_having_midzone_count
	average_letter_size = float(midzone_row_count) / lines_having_midzone_count
	# letter size is actually height of the letter and we are not considering width
	LETTER_SIZE = average_letter_size
	# error prevention ^-^
	if(average_letter_size == 0): average_letter_size = 1
	# We can't just take the average_line_spacing as a feature directly. We must take the average_line_spacing relative to average_letter_size.
	# Let's take the ratio of average_line_spacing to average_letter_size as the LINE SPACING, which is perspective to average_letter_size.
	relative_line_spacing = average_line_spacing / average_letter_size

	return average_letter_size,relative_line_spacing,fineLines

def extractWords(image, lines,average_letter_size):



	# apply bilateral filter
	filtered = preprocess.bilateralFilter(image, 5)

	# convert to grayscale and binarize the image by INVERTED binary thresholding
	thresh = preprocess.threshold(filtered, 180)

	width = thresh.shape[1]
	space_zero = [] # stores the amount of space between words
	words = [] # a 2D list storing the coordinates of each word: y1, y2, x1, x2

	# Isolated words or components will be extacted from each line by looking at occurance of 0's in its vertical projection.
	for i, line in enumerate(lines):
		extract = thresh[int(line[0]):int(line[1]), 0:width] # y1:y2, x1:x2
		vp = preprocess.verticalProjection(extract)
		#print i
		#print vp

		wordStart = 0
		wordEnd = 0
		spaceStart = 0
		spaceEnd = 0
		indexCount = 0
		setWordStart = True
		setSpaceStart = True
		includeNextSpace = True
		spaces = []

		# we are scanning the vertical projection
		for j, sum in enumerate(vp):
			# sum being 0 means blank space
			if(sum==0):
				if(setSpaceStart):
					spaceStart = indexCount
					setSpaceStart = False # spaceStart will be set once for each start of a space between lines
				indexCount += 1
				spaceEnd = indexCount
				if(j<len(vp)-1): # this condition is necessary to avoid array index out of bound error
					if(vp[j+1]==0): # if the next vertical projectin is 0, keep on counting, it's still in blank space
						continue

				# we ignore spaces which is smaller than half the average letter size
				if((spaceEnd-spaceStart) > int(average_letter_size/2)):
					spaces.append(spaceEnd-spaceStart)

				setSpaceStart = True # next time we encounter 0, it's begining of another space so we set new spaceStart

			# sum greater than 0 means word/component
			if(sum>0):
				if(setWordStart):
					wordStart = indexCount
					setWordStart = False # wordStart will be set once for each start of a new word/component
				indexCount += 1
				wordEnd = indexCount
				if(j<len(vp)-1): # this condition is necessary to avoid array index out of bound error
					if(vp[j+1]>0): # if the next horizontal projectin is > 0, keep on counting, it's still in non-space zone
						continue

				# append the coordinates of each word/component: y1, y2, x1, x2 in 'words'
				# we ignore the ones which has height smaller than half the average letter size
				# this will remove full stops and commas as an individual component
				count = 0
				for k in range(int(line[1])-int(line[0])):
					row = thresh[int(line[0]+k):int(line[0]+k+1), wordStart:wordEnd] # y1:y2, x1:x2
					if(np.sum(row)):
						count += 1
				if(count > int(average_letter_size/2)):
					words.append([line[0], line[1], wordStart, wordEnd])

				setWordStart = True # next time we encounter value > 0, it's begining of another word/component so we set new wordStart

		space_zero.extend(spaces[1:-1])

	#print space_zero
	space_columns = np.sum(space_zero)
	space_count = len(space_zero)
	if(space_count == 0):
		space_count = 1

	average_word_spacing = float(space_columns) / space_count
	relative_word_spacing = average_word_spacing / average_letter_size


	return average_word_spacing,words
