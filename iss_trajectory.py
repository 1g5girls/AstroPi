# -*- coding: utf-8 -*-
"""
Created on Thu May 21 11:04:34 2020

@author: ines

generate kml file from csv data file to display ISS trajectory
using simple kml 

"""

import simplekml


TEAM = "1G5-GIRLS"  #team name
DATA_FILE = "1g5girls_data.csv"
ISS_HEIGHT = 412e3


def read_csv_file(data_file):
    """
    Read csv data file
    Return data list 
    decimal coordinates Long Lat as float
    """
    with open(data_file, 'r') as f:
        # create a list that contains each string of characters separated by commas 
        data_lines_str = [line.split(',') for line in f.readlines()]
        # create a list by removing the CSV headers and transforming the character strings into floaters
        data_lines = [(date, number, float(long.strip()), float(lat.strip())) for date, number, long, lat in data_lines_str[1:]]
        return data_lines
 
positions = read_csv_file(DATA_FILE)

monkml = simplekml.Kml()

# waypoints computing
for date, number, long, lat in positions:
    # Create a point with the name and 1g5girls_number of the lat photo, long
    pnt = monkml.newpoint(name=f"1g5girls_{number}", coords=[(lat, long)])
    # Create an information next to the point with the number and date of the shot
    pnt.snippet.content = f"ISS position {number} at {date}"
    pnt.snippet.maxlines = 1

# linestring computing

start_date = positions[1][0]
# Create a list of tuples with the lat, long, altitude 
line_coords = [(lat, long, ISS_HEIGHT) for date, number, long, lat in positions]
# # create a kml line with the list of points connected by line segments
lin = monkml.newlinestring(name="Traj_iss_1g5girls", description=f"ISS trajectory from {start_date} ", coords=line_coords)
# Set the altitude reference in google earth
lin.altitudemode = simplekml.AltitudeMode.absolute  

# Generate kml file
monkml.save("1g5girls.kml")