"""
Utils for scraping Instagram
"""

from __future__ import print_function as print3

import requests
import json
import numpy as np
from PIL import Image
from io import BytesIO

import time
import os
import sys, select
import datetime

from bs4 import BeautifulSoup as bs

res = 300





def saveJson(struct,file):

    with open(file,'w') as outfile:
        json.dump(struct,outfile)

    return True



def openJson(file):

    with open(file,'r') as infile:
        data = json.load(infile)

    return data





def getUserMedia(user):

    """
    Get json of user page data
    """

    page = requests.get('https://www.instagram.com/'+user+'/media/')
    content = page.content
    struct = json.loads(content)

    return page, struct




def getImage(userpage, index):

    # Get image from user page

    struct = json.loads(page.content)

    imgurl = struct['items'][index]['images']['standard_resolution']['url']
    code = struct['items'][index]['code']

    image = Image.open(BytesIO(requests.get(imgurl).content))

    return image




def getImagesOld(userpage):

    struct = json.loads(page.content)

    imgurls = []
    codes = []
    images = []

    for post in struct['items']:
        imgurls += [post['images']['standard_resolution']['url']]
        codes += [post['code']]
        images += [Image.open(BytesIO(requests.get(imgurls[-1]).content))]

    return imgurls,codes,images





def getPosts(userpage):

    # Get latest n=25 posts from user page

    struct = json.loads(userpage.content)

    posts = []

    for post in struct['items']:
        id = post['id']
        code = post['code']
        imgurl = post['images']['standard_resolution']['url']
        image = Image.open(BytesIO(requests.get(imgurl).content))
        caption = post['caption']['text']
        userid = post['user']['id']
        username = post['user']['username']
        likes = post['likes']['count']
        comments = post['comments']['count']
        posts += [{'id':id, 'code':code, 'imgurl':imgurl, 'image':image,
                  'caption':caption, 'userid':userid, 'username':username,
                  'likes':likes, 'comments':comments}]

    return posts





def img2numpy(image):

    # Convert image to numpy array for analyses

    array = np.array(image.getdata()).reshape(image.size[0], image.size[1], 3)

    return array





def jsonStructFromPageContent(content):

    string = content.split('<script type="text/javascript">window._sharedData = ')
    string = string[1].split(';</script>')[0]

    struct = json.loads(string)

    return struct
    





def search_old(term):

    page = requests.get('https://www.instagram.com/explore/tags/'+term+'/')
    content = page.content

    sharedData = content.split('<script type="text/javascript">window._sharedData = ')
    substrings = sharedData[1].split('}, {')
    struct = []

    i=0
    length = len(substrings)
    print(str(length) + ' results')

    for string in substrings[1:(length-10)]:

        struct += [json.loads('{'+string+'}')]

    return struct




def search(term, saveJpgs=False):

    # Get latest n~15 posts for a given tag

    page = requests.get('https://www.instagram.com/explore/tags/'+term+'/')
    content = page.content

    sharedData = content.split('<script type="text/javascript">window._sharedData = ')
    substrings = sharedData[1].split('}, {')
    struct = []

    length = len(substrings)
    print(str(length) + ' results, keeping ' + str(length-11))
    length += -11

    i=0
    images = np.zeros([length,res,res,3])

    for string in substrings[1:(length+1)]:

        temp = json.loads('{'+string+'}')
        
        id = temp['id']
        code = temp['code'] #photography_1505164452.json
        userid = temp['owner']['id']
        imgurl = temp['display_src']
        height = temp['dimensions']['height']
        width = temp['dimensions']['width']
        caption = temp['caption']
        likes = temp['likes']['count']
        comments = temp['comments']['count']
        date = temp['date']
        
        struct += [{'id':id, 'code':code, 'userid':userid, 
                    'imgurl':imgurl, 'height':height, 'width':width, 
                    'caption':caption, 'likes':likes, 'comments':comments, 'date':date}]

        jpg = Image.open(BytesIO(requests.get(imgurl).content))
        if saveJpgs:
            timestamp = str(int(time.time()))
            jpg.save('data/images/%s_%02d_%s.jpg'%(timestamp,i,id),'JPEG')
        
        images[i] = jpg.resize([res,res])
        i += 1

    return struct, images




def searchLoop(term, verbose=1, saveImages=True, saveJpgs=True, wait=120):

    """
    Keep scraping tag until keyboard interrupt
    wrapper for search()
    """

    timestamp = str(int(time.time()))

    posts = []
    images = np.zeros([0,750,750,3])
    postsfile = 'data/posts_'+term+'_'+timestamp+'.json'
    imagefile = 'data/images_'+term+'_'+timestamp+'.npy'

    interrupt = False
    
    while not interrupt:

        struct,imageArr = search(term, saveJpgs)
        posts += struct
        if saveImages:
            images = np.append(images,imageArr, axis=0)
        
        with open(postsfile,'w') as outfile:
            if verbose >= 1:
                print("Saving posts...")
            json.dump(posts,outfile)

        np.save(imagefile,images)

        #time.sleep(20)
        rout, wout, exout = select.select( [sys.stdin], [], [], wait )

        if (rout):
            interrupt = True
            print("Interrupted by", sys.stdin.readline().strip())

    print("Done (keyboard interrupt)")

    return posts,images




def imagesFromFiles(substr,nposts):

    """
    Open all images in a directory with the right range of timestamps
    given a list of posts
    """

    files = os.listdir('data/images')
    files.sort()

    counter = 0
    start = False
    images = np.zeros([nposts,res,res,3])

    for file in files:

        if int(file.split('_')[0]) >= int(substr):
            start = True

        if start:
            temp = Image.open('data/images/'+file)
            images[counter] = temp.resize([res,res])
            counter += 1

        if (counter >= nposts):
            break

    return images





def getData(file='posts_photography_1505164452.json', updated=True, rawimages=False):

    # VERY DEPENDENT ON KEEPING NAMING SCHEME

    """
    Load data
    """
    
    with open('data/'+file,'r') as infile:
        posts = json.load(infile)

    substr = file.split('posts_')[-1].split('.json')[0]
    
    try:
        infile = 'data/images_'+substr+'.npy'
        images = np.load(infile)
    except:
        rawimages = True

    if updated:
        with open('data/posts3_'+substr+'.json','r') as infile:
            posts = json.load(infile)
    
    if rawimages:
        images = imagesFromFiles(substr.split('_')[-1].split('.')[0],len(posts))

    return posts, images




def getUserInfo(username):

    page = requests.get('https://www.instagram.com/'+username)
    soup = bs(page.content, 'html.parser')
    desc = soup.find('meta', property='og:description')['content']

    substr = desc.split(' Followers, ')
    followers = substr[0]
    substr = substr[1].split(' Following, ')
    following = substr[0]
    nposts = substr[1].split(' Posts')[0]

    struct = jsonStructFromPageContent(page.content)
    likes = []
    comments = []
    counter = 0
    for node in struct[u'entry_data'][u'ProfilePage'][0][u'user'][u'media'][u'nodes']:
        likes += [ node[u'likes'][u'count'] ]
        comments += [ node[u'comments'][u'count'] ]
        counter += 1

    return {'followers':followers, 'following':following, 'nposts':nposts}




    
def userFromPost(post, verbose=1):

    """
    Given a post, retrieve the posting user's info
    """

    code = post['code']

    try:
        page = requests.get('https://www.instagram.com/p/'+code+'/')
        content = page.content

        if verbose >= 2:
            print('https://www.instagram.com/p/'+code+'/')
        
        soup = bs(content,'html.parser')
        #hashtags = soup.find_all("meta", property="instapp:hashtags")
        userid = soup.find('meta', property='instapp:owner_user_id')['content']
        title = soup.find('meta', property='og:title')
        
        desc = soup.find('meta', property='og:description')
        if '(' in desc['content']:
            username = desc['content'].split('(@')[1].split(')')[0]
        else:
            username = desc['content'].split('- @')[1].split(' on Instagram')[0]
            
        userData = getUserInfo(username)
        userData['userid'] = userid
        userData['username'] = username

    except requests.exceptions.RequestException as error:
        print('Request error')

        userData = {'followers':-1, 'following':-1, 'nposts':-1}
        userData['userid'] = ''
        userData['username'] = ''

    except:
        print('No page')

        userData = {'followers':-1, 'following':-1, 'nposts':-1}
        userData['userid'] = ''
        userData['username'] = ''

    return userData




def usersFromPosts(posts, verbose=1):

    users = []
    i = 0
    
    for post in posts:

        userData = userFromPost(post, verbose)
        users += [userData]

        if (i % 100) == 0:
            print(':::')
        elif (i % 10) == 0:
            print(':')
        else:
            print('.',end='')
            
        i += 1

    return users





def updatePost(post, verbose=1):

    code = post['code']
    newpost = post.copy()

    # Features that should have been included in original parser
    newpost['fb_app_id'] = 0
    newpost['medium'] = 0
    newpost['mediumtype'] = 0
    newpost['ismultiple'] = 0


    try:
        page = requests.get('https://www.instagram.com/p/'+code+'/')
        content = page.content

        if verbose >= 2:
            print('https://www.instagram.com/p/'+code+'/')
        
        soup = bs(content,'html.parser')
        hashtags = soup.find_all("meta", property="instapp:hashtags")
        desc = soup.find('meta', property='og:description')
        
        if '(' in desc['content']:
            username = desc['content'].split('(@')[1].split(')')[0]
        else:
            username = desc['content'].split('- @')[1].split(' on Instagram')[0]

        substr = desc['content'].split(' Likes, ')
        likes = substr[0]
        comments = substr[1].split(' Comments')[0]

        newpost['timestamp'] = time.time()
        if type(hashtags) is list:
            newpost['hashtags'] = hashtags
        newpost['likes'] = likes
        newpost['comments'] = comments

        # Features that should have been included in original parser
        
        newpost['fb_app_id'] = soup.find('meta', property='fb:app_id')['content']
        #newpost['medium'] = soup.find('meta', name='medium')['content']
        newpost['mediumtype'] = soup.find('meta', property='og:type')['content']
        if len(content.split('sidecar')) > 2:
            newpost['ismultiple'] = 2
        elif len(content.split('sidecar')) == 2:
            newpost['ismultiple'] = 1
        else:
            newpost['ismultiple'] = 0

        if verbose >=2:
            print(newpost['fb_app_id'], newpost['medium'], newpost['mediumtype'], newpost['ismultiple'])
        

    except requests.exceptions.RequestException as error:
        print('Request error')
        newpost['timestamp'] = 0.

    except:
        if verbose >= 3:
            print('No page')
        elif verbose >= 2:
            print('NP',end='')
        elif verbose >= 1:
            print('N',end='')
        newpost['timestamp'] = 0.

    return newpost




def updateData(posts, verbose=1):

    newposts = []
    i = 0
    
    for post in posts:

        newpost = updatePost(post, verbose)
        newposts += [newpost]

        if (i % 100) == 0:
            print(':::')
        elif (i % 10) == 0:
            print(':')
        else:
            print('.',end='')
            
        i += 1

    print('')

    return newposts





def dataFromScraper(account, getImages=True):

    """
    Get data from instagram-scraper output
    Match format of utils output
    """

    dir = os.path.join('/home','albert','Data','scraper',account)
    struct = openJson(os.path.join(dir,account+'.json'))

    data = []
    nposts = len(struct)

    if getImages:
        images = np.zeros([nposts,res,res,3])
        counter = 0
    else:
        images = []
        
    for post in struct:

        #userid
        username = post[u'user'][u'username']
        #followers
        #following
        #nposts
        id = post[u'id']
        code = post[u'code']
        userid = post[u'user'][u'id']
        image = post[u'images'][u'standard_resolution']
        imgurl = image[u'url']
        height = image[u'height']
        width = image[u'width']
        captiondata = post[u'caption']
        if (captiondata is None):
            caption = ''
            createdtime = ''
        else:
            caption = captiondata[u'text']
            createdtime = captiondata[u'created_time']
        likes = post[u'likes'][u'count']
        comments = post[u'comments'][u'count']
        date = createdtime

        temp = {'id':id, 'code':code, 'userid':userid, 
                'imgurl':imgurl, 'height':height, 'width':width, 
                'caption':caption, 'likes':likes, 'comments':comments, 'date':date,
                'createdtime':createdtime}

        data += [temp]

        if getImages:
            filename = os.path.join(dir,str(imgurl).split('/')[-1])
            if os.path.isfile(filename):
                temp = Image.open(filename)
                images[counter] = temp.resize([res,res])
            else:
                images[counter] = 0.
            counter += 1
        
    return data, images
