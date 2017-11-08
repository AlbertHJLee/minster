# pikkit

<p align="center">
  <img src="http://pikkit.site/static/pikkit_banner.png" alt="pikkit banner"/>
</p>

Pikkit is a machine learning tool for predicting the popularity of Instagram posts.

This repository consists of a python package, an ipython script, and a web app. The script scrapes Instagram data and trains a linear regression model based on the data. It automatically rejects outliers and selects features based on their importance.

The web app allows users to upload images and get recommendations from the regression model running on the backend. It is hosted at www.pikkit.site


## Outline of README:
1. [Running the code](#Runcode)
2. [Goals and Overview](#Goals)
3. [Analysis and Model](#Analysis)
4. [Directory structure](#Organization)



<a id='Runcode'></a>
## 1. Running the code

First make sure all necessary packages have been installed:

    $ pip install requests
    $ pip install Pillow
    $ pip install beautifulsoup4
    $ pip install instagram-scraper
    
(If you don't have numpy, scipy, sklearn, Flask, etc. you'll need those too.)
    
In order to scrape specific users on Instagram:

    $ cd <directory_for_data>
    $ instagram-scraper <username> --media_metadata 

In order to scrape a hashtag, open python and run searchLoop (without the # in the string):

    $ cd <directory_of_this_repository>
    $ python
    > import utils
    > posts,images,rout = utils.searchLoop('<yourhashtag>',saveImages=False,saveJpgs=True,wait=180)
  
The keyword wait specifies how long in seconds to wait before making the next GET request from Instagram. For popular tags, like 'cat', 30 seconds is usually long enough during peak hours. For popular food related tags, 2 minutes is more reasonable.

The analysis is mainly carried out in feature_engineering.ipynb, which calls most of the important functions from features.py and utils.py. Making everything callable from the command line is my first order of business but the ipython notebook should at least make it clear what I'm doing.

Once a model is saved from the ipython script, it can be used by pikkit.site's backend. The backend runs using functions from app.py and model.py. If you use Flask, these should run as is. Hosting it on a dedicated server (e.g. on AWS) will require some set up.
    

<a id='Goals'></a>
## 2. Goals and Overview

Pikkit is a tool for predicting the popularity of an image on Instagram.
Given some set of images with dfferent aesthetic features, such as the following:

<p align="center">
<img src="http://pikkit.site/static/demo_img_best.jpg" alt="Best Picture Ever" height=150px width=150px>
<img src="http://pikkit.site/static/demo_img_contrast.jpg" alt="Best Picture Ever" height=150px width=150px>
<img src="http://pikkit.site/static/demo_img_corner.jpg" alt="Best Picture Ever" height=150px width=150px>
<img src="http://pikkit.site/static/demo_img_gray.jpg" alt="Best Picture Ever" height=150px width=150px>
</p>

Pikkit will pick the image with the best visual characteristics:

<p align="center">
<img src="http://pikkit.site/static/demo_img_best.jpg" alt="demo_best" height=150px width=150px border="2">
</p>

A linear regression model is used to make this prediction. Given that likeability does not have a linear relationship with many of the features in an image, I had to do a lot of feature engineering to arrive at a useful set of features. I used an iterative strategy of engineering some features, running a feature selection algorithm, and then engineering new features based on what kind of information had predictive power in the previous iteration.

I settled on this approach after realizing that throwing more complex models at the data set - such as a neural net - did not produce noticeably better results because simply knowing what feature is informative was the main bottleneck.

I focused on food-related instagram posts in order to scope down the requirements of my model and also to have a consistent set of image features and properties that could be modeled linearly. After multiple rounds of selecting features I converged on a final model with 46 features.


<a id='Analysis'></a>
## 3. Analysis and Model

The 46 features used in the regression model consist of image features and metadata features:
* 7 image kernels for detecting compositional features (e.g. how centered is the image)
* saturation
* contrast
* number of hashtags
* day of the week, one hot encoded
* hour of day, one hot encoded
* flag for multiple images
* number of followers
* number followed
* number of total posts by user
* mean number of likes for user

The mean number of likes were obviously the most informative, but the image features contributed to the model's predictive power, as evidenced by the fact that the model was able to recommend likeable images even when run on a single user's data.

In terms of numbers, the final model had an R^2 score of 0.75 and a Spearman correlation of 0.9. This is expected to lead to a 20% increase in the number of likes. I calculated this by comparing the average number of likes a user would get by selecting any candidate image at random to the number of likes they would get if they only select images recommended by pikkit.


<a id='Organization'></a>
## 4. Directory structure

    ├── LICENSE
    ├── .gitignore
    ├── README.md          <- Overview of project
    │
    ├── data               <- This folder contains .json files of metadata of posts from Instagram
    │   │                       (not included in repository due to size)
    │   ├── *.json         <- jsons scraped using utils.getData() or instagram-scraper**
    │   :     :
    │   └── images         <- This folder contains images scraped from Instagram
    │       └── *.jpg      <- jpgs scraped using utils.getData() or instagram-scraper**
    │             :
    │
    ├── exploration.ipynb          <- ipython notebook documenting data exploration
    ├── feature_engineering.ipynb  <- ipython notebook documenting analysis and model training
    │
    │
    ├── app.py             <- Flask app for running pikkit.site
    │
    ├── static             <- Assets for pikkit.site
    │   ├── customstyle.css        <- Modifications to default bootstrap.com styles
    │   ├── navbar-top.css         <- More modifications
    │   ├── favicon.png            <- Icon for browser tab
    │   ├── pikkit_banner.png      <- Banner for homepage
    │   ├── demo_img_*.jpg         <- Backup images for demo-ing the project from a browser
    │   :     :
    │   └── demo_images.html       <- Webpage indexing demo images above
    │
    ├── templates          <- Main pages at pikkit.site
    │   ├── index.html             <- Homepage
    │   ├── output.html            <- Results page (displays best images after running model on uploaded data)
    │   ├── slides.html            <- Embedded slides explaining project
    │   └── layout.html            <- General template for all pikkit.site pages
    │
    │
    ├── models             <- Trained models (used in webapp backend)
    │   ├── LR_model_*.sav 
    │   :     :
    │   └── LR_model_cake.sav      <- Current version (scoped down to cakes for better performance)
    │
    │
    ├── features.py        <- Suite of tools for extracting image and metadata features
    │  
    ├── model.py           <- Tools for loading and running regression model
    │
    └── utils.py           <- Tools for scraping, manipulating, and formatting data
   
\*\* https://github.com/rarcega/instagram-scraper
