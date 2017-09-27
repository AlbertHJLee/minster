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

    filename = 'models/LR_model.sav'
    model,features = pickle.load(open(filename, 'rb'))
    
    return model,features



def getProbs(likes, model):
    probs = likes
    return probs




def pickbest(images):

    nimages = len(images)
    likes = np.zeros(nimages)
    npimages = np.zeros([nimages,res,res,3])

    regr_model,featureList = getModel()
    nfeatures = regr_model.coef_.shape[0]
    data = np.zeros([nimages,nfeatures])

    print nimages,nfeatures,npimages.shape,data.shape,featureList
    
    for i in range(nimages):
        image = Image.open(images[i])
        npimages[i] = utils.img2numpy(image.resize([res,res]))
        data[i,:] = features.getImageFeatures(npimages[i])[0,featureList[0:9]]  # using only the 9 image features

    print data
    likes = regr_model.predict(data)
    probs = getProbs(likes, regr_model)

    order = likes.argsort().tolist()

    if nimages >= 4:
        return [images[i] for i in order[-4:]], ['%.4f'%probs[i] for i in order[-4:]]
    else:
        return images[order[-1]], probs[order[-1]]
