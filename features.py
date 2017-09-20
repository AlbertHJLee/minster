"""
Library of functions for extracting features from images and metadata
"""


import numpy as np
from PIL import Image
from io import BytesIO





"""
Image features
"""


def contrast(image):

    # "contrast" measured as the standard deviation
    # Other metric might be better
    
    return np.sqrt( np.var(image) )





def rgb2xyz(rgb):

    # Convert to XYZ color space

    x = 0.49*rgb[:,:,0] + 0.31*rgb[:,:,1] + 0.2*rgb[:,:,2]
    y = 0.177*rgb[:,:,0] + 0.812*rgb[:,:,1] + 0.011*rgb[:,:,2]
    z = 0.*rgb[:,:,0] + 0.01*rgb[:,:,1] + 0.99*rgb[:,:,2]

    return x,y,z




def colorfulness(image, option='rgb'):

    # How far the RGB components are removed from true gray

    if (option == 'rgb'):

        I = image.mean(2)
        C = np.sqrt((image[:,:,0]-I)**2 + (image[:,:,1]-I)**2 + (image[:,:,2]-I)**2)

    elif (option == 'xyz'):
        
        x,y,_ = rgb2xyz(image)
        C = np.sqrt(x**2 + y**2)

    return C




def saturation(image, options=['rgb','mean']):

    # Given some brightness, how colorful the RGB components are

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

    notcos = np.array([-.7,.2,1.,.2,-.7])
    notsin = np.array([-1.,-.7,0.,.7,1.])

    corner1 = np.array([])

    return notcos, notsin






"""
Textual features
"""


def not_in_list(x,args,y):
    list = x['caption'].split(' #')
    return not (args in list[1:])




def convertString(x):

    # Converts textual description of likes to integer
    # i.e. - '16.5k' -> 16,500
    
    string = str(x)
    if 'k' in string:
        number = float( ''.join(string.split('k')[0].split(',')) ) * 1000
    elif 'm' in string:
        number = float( ''.join(string.split('m')[0].split(',')) ) * 1000000
    else:
        number = float( ''.join(string.split(',')) )
    return number




def extractTimeData(x):

    # Get time data from timestamp
    # use indexing to get weekday or hour
    

def extractTimeData(x):
    if not (type(x) is int):
        return 7, 25
    createdtime = datetime.fromtimestamp(int(x))
    hour = createdtime.hour
    weekday = createdtime.weekday()
    return weekday, hour


def likesFromPandas(df):
    return df['likes'].apply(lambda x: float(convertString(x))).values


def ntagsFromPandas(df):
    return df[u'caption'].apply(lambda x: float( len(x.split(' #')) ) ).values - 1



