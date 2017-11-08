"""
Library of functions for extracting features from images and metadata
"""


import numpy as np
from PIL import Image
from io import BytesIO

from datetime import datetime, date

from scipy.misc import imresize





"""
Image features
"""


def contrast(image):

    """
    "contrast" measured as the standard deviation
    Other metric might be better

    input:  image as a numpy array
    output: contrast as a floating point
    """
    
    return np.sqrt( np.var(image) )





def rgb2xyz(rgb):

    """
    Convert RGB to XYZ color space

    input:   image as a numpy array with 3 channels (RGB)
    outputs: X, Y, and Z channels
    """

    x = 0.49*rgb[:,:,0] + 0.31*rgb[:,:,1] + 0.2*rgb[:,:,2]
    y = 0.177*rgb[:,:,0] + 0.812*rgb[:,:,1] + 0.011*rgb[:,:,2]
    z = 0.*rgb[:,:,0] + 0.01*rgb[:,:,1] + 0.99*rgb[:,:,2]

    return x,y,z




def colorfulness(image, option='rgb'):

    """
    How far the RGB components are removed from true gray
    (This is close to how we perceive how much color is present in an image)
    
    inputs:  
      image - image as numpy array with 3 color channels
      option - keyword specifying which color space to use

    output:
      colorfulness as floating point

    """

    if (option == 'rgb'):

        I = image.mean(2)
        colorfulness = np.sqrt((image[:,:,0]-I)**2 + (image[:,:,1]-I)**2 + (image[:,:,2]-I)**2)

    elif (option == 'xyz'):
        
        x,y,_ = rgb2xyz(image)
        colorfulness = np.sqrt(x**2 + y**2)

    return colorfulness




def saturation(image, options=['rgb','mean']):

    """
    Given some brightness, how colorful the RGB components are.

    In other words, if something is fairly bright, and sending a lot of photons,
    the non-white-ness of the photons should scale accordingly. I.e. the signal in
    the color should scale proportionally to the signal in the intensity (brightness)

    inputs:
      image - numpy image
      options - [ string_specifying_color_space, string_specifying_conversion_to_gray ]

    output:
      saturation

    """

    C = colorfulness(image,options[0])
 
    if (options[1] == 'luma'):
        I = 0.2126*image[:,:,0] + 0.7152*image[:,:,1] + 0.0722*image[:,:,2]
    else:
        I = image.mean(2)

    sat = (C+.01)/(I+.1)

    return sat



def compKernels(res):

    """
    Kernels for extracting compositional features in image
    i.e. is the image centered, skewed, etc.
    built from sinc interpolation and sine functions
    
    Maybe better to use cosine and sine?

    input: integer specifying resolution of image we want to generate kernels for
    outputs:
      sinc - 1D sinc function kernel
      sin - 1D sine kernel
      corner1 etc. - 2D Gaussian kernel displaced to corner of image

    """

    offset = float(int(float(res)*.5))
    x = (np.arange(res)-offset)/offset
    sinc = np.sinc(x)
    sinc = sinc-np.mean(sinc)

    sin = np.sin(x*np.pi*0.7)
    sin = sin - np.mean(sin)

    xx = np.zeros([res,res])
    for i in range(res):
        xx[i,:] = x 

    yy = np.zeros([res,res])
    for i in range(res):
        yy[:,i] = x 

    corner1 = np.exp(-((xx-0.3)**2+(yy-0.3)**2))
    mean = np.mean(corner1)
    corner1 += -mean
    corner2 = np.exp(-((xx-0.3)**2+(yy+0.3)**2)) - mean
    corner3 = np.exp(-((xx+0.3)**2+(yy-0.3)**2)) - mean
    corner4 = np.exp(-((xx+0.3)**2+(yy+0.3)**2)) - mean
    
    return sinc, sin, corner1, corner2, corner3, corner4




def compKernels5():

    """
    Hard coded kernels used for testing
    """

    notcos = np.array([-.7,.2,1.,.2,-.7])
    notsin = np.array([-1.,-.7,0.,.7,1.])

    corner1 = np.array([])

    return notcos, notsin




def getImageFeatures(image):

    """
    Extract image features from image

    input:  numpy image
    output: numpy array of extracted features
    """
    
    dims = 5
    
    sat = np.mean(colorfulness(image))
    intensity = np.mean(image,2)
    imgcontrast = contrast(image)
    #comp = imresize(intensity,[dims,dims]).reshape([dims**2])

    kernelCos,kernelSin,kernelCor1,kernelCor2,kernelCor3,kernelCor4 = compKernels(dims)

    temp = imresize(intensity,[dims,dims])
    kCos = np.mean(temp*kernelCos)
    kSin = np.mean(temp*kernelSin)
    kCor1 = np.mean(temp*kernelCor1)
    kCor2 = np.mean(temp*kernelCor2)
    kCor3 = np.mean(temp*kernelCor3)
    kCor4 = np.mean(temp*kernelCor4)

    #minsat = np.min(sat)
    #maxsat = np.max(sat)
    #mincon = np.min(imgcontrast)
    #maxcon = np.max(imgcontrast)

    #normSinA = np.abs(kSin)/np.max(np.abs(kSin))

    #normsat = (sat - minsat)/(maxsat-minsat)
    #normcontrast = (imgcontrast - mincon)/(maxcon-mincon)
    #normCos = (kCos - np.mean(kCos))/(np.max(kCos) - np.min(kCos))
    #normSin = (kSin - np.mean(kSin))/(np.max(kSin) - np.min(kSin))

    nfeatures = 1+2+4+1+1
    data = np.zeros([1,nfeatures])
    data[:,0] = kCos
    data[:,1] = kSin
    data[:,2] = np.abs(kSin)
    data[:,3] = kCor1 #kCor1/np.max(kCor1)
    data[:,4] = kCor2 #kCor2/np.max(kCor2)
    data[:,5] = kCor3 #kCor3/np.max(kCor3)
    data[:,6] = kCor4 #kCor4/np.max(kCor4)
    data[:,7] = sat
    data[:,8] = imgcontrast

    return data






"""
Textual features
"""


def not_in_list(x,args,y):

    """
    Check whether a string is in a list of hashtags
    """
    
    list = x['caption'].split(' #')
    return not (args in list[1:])




def convertString(x):

    """
    Converts textual description of number of likes to integer
    i.e. - '16.5k' -> 16,500
    """
    
    string = str(x)
    if 'k' in string:
        number = float( ''.join(string.split('k')[0].split(',')) ) * 1000
    elif 'm' in string:
        number = float( ''.join(string.split('m')[0].split(',')) ) * 1000000
    else:
        number = float( ''.join(string.split(',')) )
    return number




def extractTimeData(x):

    """
    Get time data from timestamp
    use indexing to get weekday or hour

    input:
      timestamp of either unicode or integer format

    outputs:
      Monday to Sunday -> 0 to 6  (7 if no timestamp)
      00:00 to 23:00 -> 0 to 23  (25 if no timestamp)

    """

    if (type(x) is unicode):
        createdtime = datetime.fromtimestamp(int(x))
        hour = createdtime.hour
        weekday = createdtime.weekday()
        #date(2017,9,16).weekday()
        return weekday, hour
    elif type(x) is int:
        createdtime = datetime.fromtimestamp(x)
        hour = createdtime.hour
        weekday = createdtime.weekday()
        #date(2017,9,16).weekday()
        return weekday, hour
    else:
        return 7, 25


    
def getnposts(x):

    """
    Get total number of posts
    """
    
    if type(x) is list:
        npostunicode = x[0]
        return convertString(npostunicode)
    elif type(x) is unicode:
        return convertString(x)
    else:
        return -1


    
def likesFromPandas(df):
    """
    From a dictified json of a list of Instagram posts, extract no. of likes
    """
    return df['likes'].apply(lambda x: float(convertString(x))).values


def ntagsFromPandas(df):
    """
    From a dictified json of a list of Instagram posts, extract no. of hashtags
    """
    return df[u'caption'].apply(lambda x: float( len(x.split(' #')) ) ).values - 1




def meanLikesFromStruct(struct):

    """
    Average number of likes and comments in most recent page of posts on a user's account
    (typically last ~16 posts)

    input:   dictified json of user page
    outputs: mean no. likes, mean no. comments
    """
    
    likes = []
    comments = []
    for node in struct[u'entry_data'][u'ProfilePage'][0][u'user'][u'media'][u'nodes']:
        likes += [node[u'likes'][u'count']]
        comments += [node[u'comments'][u'count']]
    nplikes = np.array(likes)
    return np.mean(nplikes), np.mean(np.array(comments))
