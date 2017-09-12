"""
Utils for scraping Instagram
"""

import requests
import json
import numpy as np
from PIL import Image
from io import BytesIO

import time
import sys, select
import datetime

from bs4 import BeautifulSoup as bs



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

    array = numpy.array(image.getdata()).reshape(image.size[0], image.size[1], 3)

    return array




def search_old(term):

    page = requests.get('https://www.instagram.com/explore/tags/'+term+'/')
    content = page.content

    sharedData = content.split('<script type="text/javascript">window._sharedData = ')
    substrings = sharedData[1].split('}, {')
    struct = []

    i=0
    length = len(substrings)
    print str(length) + ' results'

    for string in substrings[1:(length-10)]:

        #print i
        #i += 1
        struct += [json.loads('{'+string+'}')]

    return struct




def search(term):

    # Get latest n~15 posts for a given tag

    page = requests.get('https://www.instagram.com/explore/tags/'+term+'/')
    content = page.content

    sharedData = content.split('<script type="text/javascript">window._sharedData = ')
    substrings = sharedData[1].split('}, {')
    struct = []

    length = len(substrings)
    print str(length) + ' results'

    i=0
    images = np.zeros([length,750,750,3])

    for string in substrings[1:(length-10)]:

        temp = json.loads('{'+string+'}')
        
        id = temp['id']
        code = temp['code']
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

        images[i] = Image.open(BytesIO(requests.get(imgurl).content)).resize([750,750])
        i += 1

    return struct, images




def searchLoop(term, verbose=1):

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

        struct,imageArr = search(term)
        posts += struct
        images = np.append(images,imageArr, axis=0)
        
        with open(postsfile,'w') as outfile:
            if verbose >= 1:
                print "Saving posts..."
                json.dump(posts,outfile)

        np.save(imagefile,images)

        #time.sleep(20)
        rout, wout, exout = select.select( [sys.stdin], [], [], 120 )

        if (rout):
            interrupt = True
            print "Interrupted by", sys.stdin.readline().strip()

    print "Done (keyboard interrupt)"

    return posts,images




def getData(file='posts_photography_1505164452.json'):

    # VERY DEPENDENT ON KEEPING NAMING SCHEME
    
    with open('data/'+file,'r') as infile:
        posts = json.load(infile)

    substr = file.split('posts_')[-1].split('.json')[0]
    infile = 'data/images_'+substr+'.npy'
    images = np.load(infile)

    return posts, images




def getUserInfo(username):

    page = requests.get('https://www.instagram.com/'+user)
    soup = bs(page.content, 'html.parser')
    desc = soup.find('meta', property='og:description')['content']

    substr = desc.split(' Followers, ')
    followers = substr[0]
    substr = substr.split(' Following, ')
    following = substr[0]
    nposts = substr.split(' Posts')

    return {'followers':followers, 'following':following, 'nposts':nposts}




    
def userFromPost(post):

    code = post['code']

    try:
        page = requests.get('https://www.instagram.com/p/'+code+'/')
    except :
        print 'Request error'
    content = page.content

    #sharedData = content.split('<script type="text/javascript">window._sharedData = ')
    #jsonString = sharedData[1].split(';</script>')[0]
    #struct = json.loads(jsonString)

    soup = bs(content,'html.parser')
    hashtags = soup.find_all("meta", property="instapp:hashtags")
    userid = soup.find('meta', property='instapp:owner_user_id')['content']
    title = soup.find('meta', property='og:title')
    desc = soup.find('meta', property='og:description')
    username = desc['content'].split('(@')[1].split(')')[0]

    userData = getUserInfo(username)
    userData['userid'] = userid
    userData['username'] = username

    return userData




def usersFromPosts(posts):

    users = []
    print ''
    
    for post in posts:

        userData = userFromPost(post)
        users += [userData]

        print '\b.',

    return users


