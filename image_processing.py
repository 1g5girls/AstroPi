#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  8 14:58:49 2020

@author: ines

Images processing : get land surface, sea surface, cloud surface and usability of images
"""

import numpy as np
import matplotlib.pyplot as plt
import os, re

from skimage import io
from skimage.color import rgb2gray
from skimage.util import img_as_uint

output_dir = "processed images"  # Output folder for processed images

rep = "usable_image" # Output folder for usable images

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
#Calculate surfaces and deduces usability of image


def image_processing(image) :
    '''
    

    Parameters
    ----------
    image : np_array
        A grayscale image

    Returns
    -------
    liste : string
        Area of cloud cover, land and sea, usability
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


try:
    os.mkdir(output_dir)
except FileExistsError:
    print(f"The dossier {output_dir} exists. The images will be overwritten")
    
try:
    os.mkdir(rep)
except FileExistsError:
    print(f"The dossier {rep} exists. The images will be overwritten")

file_listing = os.listdir()
file_listing.sort()

extension = re.compile("(?i).*\.jpg")

big_liste = []

#images processing
for file_name in file_listing : 
     if extension.match(file_name):
        img = io.imread(file_name)
        img= mask_porthole(img)
        img = rgb2gray(img)
        big_liste.append([file_name, *image_processing(img)])
        plt.figure(dpi=150, frameon = False, figsize = (10, 10))
        plt.imshow(img, cmap="gray")
        plt.axis('off')
        plt.show()
        plt.imsave(f"{output_dir}/{file_name}", img_as_uint(img), cmap="gray")
        # if the image is usable it goes in a separate folder.
        for usability in image_processing(img):
            if usability == 'usable' :
                plt.imsave(f"{rep}/{file_name}", img_as_uint(img), cmap="gray")

# display of the results in the console
for file_name, cloud_surface, land_surface, sea_surface, usability in big_liste:
    print(f"{file_name}: ")
    print(f"\t Cloud surface = {cloud_surface:.1} km^2")
    print(f"\t Land surface = {land_surface:.1} km^2")
    print(f"\t Sea surface = {sea_surface:.1} km^2")
    print(f"\t The image is {usability}")
    


    
