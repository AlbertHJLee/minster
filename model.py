"""
Functions for running input images through model
"""

import requests
import json
import numpy as np
from PIL import Image
from io import BytesIO

#from .. import features
#from .. import utils

import ..insta import features
import ..insta import utils

res=300




def likesFromModel(image):

    contrast = features.contrast(image)

    satH,_ = np.histogram(features.colorfulness(image), bins=nbins)
    satH = satH/np.sqrt(np.sum(satH**2))
    sat = np.mean(features.colorfulness(image))
    intensity = np.mean(image,2)
    conH,_ = np.histogram(intensity, bins=nbins)
    conH = conH/np.sqrt(np.sum(conH**2))
    contrast = features.contrast(image)
    comp = imresize(intensity,[dims,dims]).reshape([dims**2])

    likes = contrast
    
    return likes




def pickbest(images):

    nimages = len(images)
    likes = np.zeros(nimages)
    npimages = np.zeros([nimages,res,res,3])
    
    for i in range(nimages):
        image = Image.open(images[i])
        npimages[i] = utils.img2numpy(image.resize([res,res]))
        likes[i] = likesFromModel(npimages[i])

    bestimage = images[ np.where(likes == likes.max())[0][0] ]
    
    return bestimage
