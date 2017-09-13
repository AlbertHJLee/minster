"""
Library of functions for extracting features from images
"""


import numpy as np
from PIL import Image
from io import BytesIO




def contrast(image):

    #hist = np.histogram(image)

    return np.sqrt( np.var(image) )





def rgb2xyz(rgb):

    x = 0.49*rgb[:,:,0] + 0.31*rgb[:,:,1] + 0.2*rgb[:,:,2]
    y = 0.177*rgb[:,:,0] + 0.812*rgb[:,:,1] + 0.011*rgb[:,:,2]
    z = 0.*rgb[:,:,0] + 0.01*rgb[:,:,1] + 0.99*rgb[:,:,2]

    return x,y,z




def saturation(image, option='rgb'):

    if (option == 'rgb'):

        I = image.mean(2)
        C = np.sqrt((image[:,:,0]-I)**2 + (image[:,:,1]-I)**2 + (image[:,:,2]-I)**2)
        sat = (C+1)/(I+1)

    elif (option == 'xyz'):
        
        x,y,_ = rgb2xyz(image)
        Cxy = np.sqrt(x**2 + y**2)
        I = image.mean(2)
        sat = Cxy/I

    return sat

    
