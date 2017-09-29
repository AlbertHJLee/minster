"""
Functions for running input images through model
"""

import requests
import json
import numpy as np
from PIL import Image
from io import BytesIO

from scipy.misc import imresize

import features
import utils
import pickle

from sklearn import linear_model, datasets
from sklearn.metrics import mean_squared_error as MSE, r2_score as R2S

res=300





def likesFromSat(image):

    nbins = 20
    dims = 5
    
    contrast = features.contrast(image)

    satH,_ = np.histogram(features.colorfulness(image), bins=nbins)
    satH = satH/np.sqrt(np.sum(satH**2))
    sat = np.mean(features.colorfulness(image))
    intensity = np.mean(image,2)
    conH,_ = np.histogram(intensity, bins=nbins)
    conH = conH/np.sqrt(np.sum(conH**2))
    contrast = features.contrast(image)
    comp = imresize(intensity,[dims,dims]).reshape([dims**2])

    likes = sat #contrast
    
    return likes




def pickbest_from_sat(images):

    nimages = len(images)
    likes = np.zeros(nimages)
    npimages = np.zeros([nimages,res,res,3])
    
    for i in range(nimages):
        image = Image.open(images[i])
        npimages[i] = utils.img2numpy(image.resize([res,res]))
        likes[i] = likesFromModel(npimages[i])

    #bestimage = images[ np.where(likes == likes.max())[0][0] ]

    order = likes.argsort().tolist()

    if nimages >= 4:
        return [images[i] for i in order[-4:]]
    else:
        return images[order[-1]]



def pickbest2(images):

    nimages = len(images)
    likes = np.zeros(nimages)
    npimages = np.zeros([nimages,res,res,3])
    
    for i in range(nimages):
        image = Image.open(images[i])
        npimages[i] = utils.img2numpy(image.resize([res,res]))
        likes[i] = likesFromModel(npimages[i])

    bestimage = images[ np.where(likes == likes.max())[0][0] ]
    
    return bestimage





def getModel():

    #filename = 'models/LR_model.sav'
    filename = 'models/LR_model_cake.sav'
    return pickle.load(open(filename, 'rb'))



def normalizeData(data,minvals,maxvals,centervals):
    nfeatures = data.shape[1]
    dataOut = data
    print nfeatures,minvals.shape,data.shape,dataOut.shape,maxvals.shape,centervals.shape
    for i in range(nfeatures):
        dataOut[:,i] = (data[:,i] - centervals[i]) / (maxvals[i] - minvals[i])
    return dataOut



def revertData(data,minvals,maxvals,centervals):
    nfeatures = minvals.shape[0]
    reverted = data
    for i in range(nfeatures):
        reverted[:,i] = data[:,i] * (maxvals[i] - minvals[i]) + centervals[i]
    return reverted



def revert_y(y,min_y,max_y,center_y):
    return y*(max_y-min_y) + center_y



def getProbs(likes, model):
    probs = likes
    return probs




def pickbest(images):

    nimages = len(images)
    likes = np.zeros(nimages)
    npimages = np.zeros([nimages,res,res,3])

    #regr_model,featureList = getModel()
    regr_model,featureList, min_y,max_y,center_y, minvals,maxvals,centervals = getModel()
    nfeatures = minvals.shape[0]  #regr_model.coef_.shape[0]
    nImgFeatures = 9
    data = np.zeros([nimages,nImgFeatures])

    #print nimages,nfeatures,npimages.shape,data.shape,featureList
    
    for i in range(nimages):
        image = Image.open(images[i])
        npimages[i] = utils.img2numpy(image.resize([res,res]))
        data[i,:] = features.getImageFeatures(npimages[i])[0,:]  #featureList[0:9]]  # using only the 9 image features

    print data.shape,minvals.shape,maxvals.shape,centervals.shape
    data = normalizeData(data,minvals,maxvals,centervals)

    likes = regr_model.predict(data[:,featureList[0:9]])
    likes_orig = revert_y(likes,min_y,max_y,center_y)
    probs = getProbs(likes_orig, regr_model)

    order = likes.argsort().tolist()
    #print order,likes,probs, images,images

    if nimages >= 4:
        return [images[i] for i in order[-4:]], ['%.4f'%probs[i] for i in order[-4:]]
    else:
        return images[order[-1]], probs[order[-1]]
