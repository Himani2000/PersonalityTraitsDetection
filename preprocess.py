import pandas as pd 
import numpy as np
import os
import cv2
import imutils 


# this function does the bilateral filtering given d in runtime ,default set to 5 

def bilateralFilter(image, d=5):
	image = cv2.bilateralFilter(image,d,50,50)
	return image


#  function to do thresholding of the image 
def threshold(image, t):
	image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	image = cv2.threshold(image,t,255,cv2.THRESH_BINARY_INV)[1]
	return image

#function to  perfrom dilate operation on the image 

def dilate(image, kernalSize):
	kernel = np.ones(kernalSize, np.uint8)
	image = cv2.dilate(image, kernel, iterations=1)
	return image



''' function to calculate horizontal projection of the image pixel rows and return it '''
def horizontalProjection(img):
    # Return a list containing the sum of the pixels in each row
    (h, w) = img.shape[:2]
    sumRows = []
    for j in range(h):
        row = img[j:j+1, 0:w] # y1:y2, x1:x2
        sumRows.append(np.sum(row))
    return sumRows
	
''' function to calculate vertical projection of the image pixel columns and return it '''
def verticalProjection(img):
    # Return a list containing the sum of the pixels in each column
    (h, w) = img.shape[:2]
    sumCols = []
    for j in range(w):
        col = img[0:h, j:j+1] # y1:y2, x1:x2
        sumCols.append(np.sum(col))
    return sumCols
    
    
    
    
    
    
