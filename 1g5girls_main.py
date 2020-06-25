"""This programm is intended to take images combined with the location where it was taken.
It also set a logfile ans a csv file that compile information about images and location.
It takes photos at regular intervals calculated for respect the maximum time and file size while spanning orbit without area not photographed.
(calculating of field of the camera)
When we'll get the footage, we will treat them in an automatic way with a programm to calculate the proportion of forest."""

# importation of dictionnary 
from logzero import logger, logfile
from ephem import readtle, degree
from picamera import PiCamera
from datetime import datetime, timedelta
from time import sleep
import os
import csv

TEAM = "1G5-GIRLS"  #team name
CAPTURE_INTERVAL_DELAY = 10  #time in seconds between  2 images to limit data amount to 3GB

dir_path = os.path.dirname(os.path.realpath(__file__))


# Set a logfile name
logfile(dir_path + "/" + TEAM + ".log")




#Latest TLE data for ISS location
name = "ISS (ZARYA)"
l1 = "1 25544U 98067A   20043.35917824  .00000614  00000-0  19234-4 0  9992"
l2 = "2 25544  51.6444 251.0491 0004797 258.4711  99.3710 15.49156480212505"
iss = readtle(name, l1, l2)

# Set up camera
cam = PiCamera()
cam.resolution = (1296, 972)

def create_csv_file(data_file):
    #"Create a new CSV file and add the header row"
    with open(data_file, 'w') as f:
        writer = csv.writer(f)
        header = ("Date/time", "Image number", "Long", "Lat")
        writer.writerow(header)

def add_csv_data(data_file, data):
    #"Add a row of data to the data_file CSV"
    with open(data_file, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(data)

def get_latlon():
    """
    A function to write lat/long to EXIF data for photographs.
    Returns (lat, long)
    """
	
    iss.compute() # Get the lat/long values from ephem
    long_value = [float(i) for i in str(iss.sublong).split(":")]
    if long_value[0] < 0:
        long_value[0] = abs(long_value[0])
        cam.exif_tags['GPS.GPSLongitudeRef'] = "W"
    else:
        cam.exif_tags['GPS.GPSLongitudeRef'] = "E"
    cam.exif_tags['GPS.GPSLongitude'] = '%d/1,%d/1,%d/10' % (long_value[0], long_value[1], long_value[2]*10)
    lat_value = [float(i) for i in str(iss.sublat).split(":")]
    if lat_value[0] < 0:
        lat_value[0] = abs(lat_value[0])
        cam.exif_tags['GPS.GPSLatitudeRef'] = "S"
    else:
        cam.exif_tags['GPS.GPSLatitudeRef'] = "N"
    cam.exif_tags['GPS.GPSLatitude'] = '%d/1,%d/1,%d/10' % (lat_value[0], lat_value[1], lat_value[2]*10)
    return (iss.sublat / degree, iss.sublong / degree)

# initialise the CSV file
data_file = dir_path + "/data.csv"
create_csv_file(data_file)
# store the start time
start_time = datetime.now()
# store the current time
# (these will be almost the same at the start)
now_time = datetime.now()
# run a loop for 2 minutes
photo_counter = 1
# Recording image and location during 178 minutes
while (now_time < start_time + timedelta(minutes=178)):
    try:
        logger.info("{} iteration {}".format(datetime.now(), photo_counter))
        # get latitude and longitude
        lat, lon = get_latlon()
        # Save the data to the file
        data = (datetime.now(), photo_counter, lat, lon)
        add_csv_data(data_file, data)
        # use zfill to pad the integer value used in filename to 3 digits (e.g. 001, 002...)
        cam.capture(dir_path + "/photo_" + str(photo_counter).zfill(3) + ".jpg")
        photo_counter += 1
        sleep(CAPTURE_INTERVAL_DELAY)  # According max data amount
        # update the current time
        now_time = datetime.now()
    except Exception as e:
        logger.error('{}: {})'.format(e.__class__.__name__, e))


