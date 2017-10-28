# pikkit

<p align="center">
  <img src="http://pikkit.site/static/pikkit_banner.png" alt="pikkit banner"/>
</p>

Pikkit is a machine learning tool for predicting the popularity of Instagram posts.

This repository consists of a python package, an ipython script, and a web app. The script scrapes Instagram data and trains a linear regression model based on the data. It automatically rejects outliers and selects features based on their importance.

The web app allows users to upload images and get recommendations from the regression model running on the backend. It is hosted at www.pikkit.site


## Outline of README:
1. [Goals and Overview](#Goals)
2. [Analysis and Model](#Analysis)
3. [Latest Graphs](#Organization)


<a id='Goals'></a>
## 1. Goals and Overview

<p align="center">
<img src="http://pikkit.site/static/demo_img_best.jpg" alt="Best Picture Ever" height=100px width=100px>
<img src="http://pikkit.site/static/demo_img_contrast.jpg" alt="Best Picture Ever" height=100px width=100px>
<img src="http://pikkit.site/static/demo_img_corner.jpg" alt="Best Picture Ever" height=100px width=100px>
<img src="http://pikkit.site/static/demo_img_gray.jpg" alt="Best Picture Ever" height=100px width=100px>
</p>

<p align="center">
<img src="http://pikkit.site/static/demo_img_best.jpg" alt="demo_best" height=100px width=100px>
<img src="http://pikkit.site/static/demo_img_contrast.jpg" alt="demo_contrast" height=100px width=100px style="opacity:0.4;">
<img src="http://pikkit.site/static/demo_img_corner.jpg" alt="Best Picture Ever" height=100px width=100px style="opacity:0.4;filter:alpha(opacity=40);">
<img src="http://pikkit.site/static/demo_img_gray.jpg" alt="Best Picture Ever" height=100px width=100px style="opacity:0.4;filter:alpha(opacity=40);">
</p>

<a id='Analysis'></a>
## 2. Analysis and Model


<a id='Organization'></a>
## 3. Directory structure

    ├── LICENSE
    ├── .gitignore
    ├── README.md          <- Overview of project
    │
    ├── data               <- This folder contains .json files of metadata of posts from Instagram
    │   ├── *.json         <- jsons scraped using utils.getData() or instagram-scraper*
    │   :     :
    │   └── images         <- This folder contains images scraped from Instagram
    │       └── *.jpg      <- jpgs scraped using utils.getData() or instagram-scraper*
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
   
* https://github.com/rarcega/instagram-scraper
