#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  8 14:58:49 2020

@author: ines

process an image and compile the resulting data into a csv file with data from another csv file
"""

import numpy as np
import os

from skimage import io
from skimage.color import rgb2gray

import csv

SCALE = 0.222  #photo scale calculated from the camera sensor characteristics in km/px

def mask_porthole(image):
    '''
    Creating a mask to remove the porthole from an image

    Parameters
    ----------
    img : tabular image

    Returns
    -------
    masked image

    '''

    l_x, l_y = image.shape[0], image.shape[1] # height, width of the image in pixels
    X, Y = np.ogrid[:l_x, :l_y]
    outer_disk_mask = (X - l_x / 2)**2 + (Y - l_y / 2)**2 > (l_x / 1.89)**2
    #inner_disk_mask =  (l_x / 1.89)**2 > (X - l_x / 2)**2 + (Y - l_y / 2)**2
    image[outer_disk_mask] = (0,0,0)
    return image

#----------------------------------------------------------------------
#Calculate the brightness of the image 


def luminosite(image) :
    '''
    

    Parameters
    ----------
    image : np_array
        A grayscale image

    Returns
    -------
	 Surface de mer = 0e+00 km^2
1g5girls_photo_006.jpg: 
    liste : string
        Area of cloud cover, land and sea.
    '''
    
    number_pixel_black = 0
    number_pixel_cloud = 0
    number_pixel_land = 0
    number_pixel_sea = 0
 
    # calculation of the number of pixels of each surface    
    for line in image:
        for pixel in line:
            if pixel < 0.09 :
                number_pixel_black += 1
            elif pixel < 0.4:
                number_pixel_sea += 1
            elif pixel < 0.5 :
                number_pixel_land += 1
            else : 
                number_pixel_cloud += 1
    
    # Convert the number of pixels of each surface to km²
    clou_sur = number_pixel_cloud * SCALE**2
    land_sur = number_pixel_land * SCALE**2
    sea_sur = number_pixel_sea * SCALE**2
    
    # add all the surfaces
    total = clou_sur + land_sur + sea_sur
  
    # we determine if the photo is taken at night
    if total < 1000 :
        clou_sur = '?'
        land_sur = '?'
        sea_sur = '?'
        usability = 'taken at night'
    # otherwise we can calculate the rate of land and determine the usability
    else :
        land_rate = land_sur/total
        
        if land_rate < 0.2 :
            usability = 'inoperable'
        else :
            usability = 'usable'

    return clou_sur, land_sur, sea_sur, usability

    
#----------------------------------------------------------------------
#Create a csv file containing the date, the number of the photo,
#Location, area and operability 

DATA_FILE = "1g5girls_data.csv"
DATA_FILE_DONE = '1g5girls_data_computed.csv'

dir_path = os.path.dirname(os.path.realpath(__file__))


def read_csv_file(data_file):
    """
    Read csv data file
    Return data list 
    decimals coordinates Long Lat as float
    """
    with open(data_file, 'r') as f:
        data_lines_str = [line.split(',') for line in f.readlines()]
        data_lines = [(date, number, float(long.strip()), float(lat.strip())) for date, number, long, lat in data_lines_str[1:]]
        return data_lines
    
def create_csv_file(data_file):
    #"Create a new CSV file and add the header row"
    with open(data_file, 'w') as f:
        writer = csv.writer(f)
        header = ("Date/time", "Image number", "Long", "Lat", "Cloud_surface", 
                  "Land_Surface", "Sea_surface", "Usability")
        writer.writerow(header)
        
def add_csv_data(data_file, data):
    #"Add a row of data to the data_file CSV"
    with open(data_file, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(data)
        
create_csv_file(DATA_FILE_DONE)

data_lines = read_csv_file(DATA_FILE)
data_lines_done = []
    
#images processing
for date, number, long, lat in data_lines:
    file_name = f"1g5girls_photo_{str(number).zfill(3)}.jpg"
    img = io.imread(file_name)
    img= mask_porthole(img)
    img = rgb2gray(img)
    data = (date, number, long, lat, *luminosite(img))
    add_csv_data(DATA_FILE_DONE, data)
        