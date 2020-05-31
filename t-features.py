import cv2
import os
import imutils
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

images='t-images'


def preprocessing(img):
    img = cv2.bilateralFilter(img,5,150,150)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thres = cv2.threshold(img,120,255,cv2.THRESH_BINARY_INV)[1]
    kernel = np.ones((5,15), np.uint8)
    dilated = cv2.dilate(thres, kernel, iterations=1)
    return dilated

def get_contours(img,file):

    cnts = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnts = imutils.grab_contours(cnts)
    output = img.copy()
    #print(len(cnts))


    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if(h>70 and w>img.shape[1]/9):

                #cv2.rectangle(output,(x,y),(x+w,y+h),(255,255,230),1)
            extracted_image = output[y:y+h,x:x+w]
            w_i=w
            h_i=h
            bar_i=features(extracted_image)


    return w_i,h_i,bar_i


def horizontalProjection(img):
    # Return a list containing the sum of the pixels in each row
    (h, w) = img.shape[:2]
    sumRows = []
    for j in range(h):
        row = img[j:j+1, 0:w] # y1:y2, x1:x2
        sumRows.append(np.sum(row))
    return sumRows


def features(img):
    #fig=plt.figure(figsize=(8,8))
    i = 1


    hp=horizontalProjection(img)
    hp=np.array(hp[1:])
    maximum=hp.max()

    pixels=0
    pixels2=0
    maxi=hp.max()
    less=hp.max()-(hp.max()/5)

    for i in range(len(hp)):
        if hp[i]==maxi:
            break
        pixels=pixels+1

    '''


    for i in range(len(hp)):

        if hp[i]>=less and hp[i]<=maxi:

            pixels2=pixels2+1'''
    return pixels



def main():
    files=os.listdir(images)
    width=[]
    height=[]
    bar_height=[]
    id_main=[]
    for file in files:
        id=file.split('.')[0]
        id_main.append(id)
        try:
            dummy_image=cv2.imread(images+'/'+file)

            img=preprocessing(dummy_image)
            w,h,bar=get_contours(img,file)
            width.append(w)
            height.append(h)
            bar_height.append(bar/h)
            print("Processing: ", file)
            print("Width", w)
            print("Height", h)
            print("Bar-height", bar)
        except Exception as e:
            print("NOT  PROCESSED", id)
            print(e)
        finally:
            df=pd.DataFrame({'id':id_main,'width':width,'height':height,'bar-height':bar_height})
            df.to_csv('Csv/t_features.csv')
        break


main()
