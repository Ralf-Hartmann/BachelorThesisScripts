#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 17:38:57 2023

@author: ralf
"""

import datetime as dt
import xarray as xr
import numpy as np
from datetime import datetime, timedelta


#Opening closing this many .nc files is kinda slow
#Try new methode of slicing a combined.nc file

def in_sounding(start_date):
    
    path_sounding = '/home/ralf/Studium/Bachelorarbeit/Radiosondendaten/' + \
                     dt.datetime.strftime(start_date, '%Y') + '_nc/' 
    file_sonde = path_sounding + dt.datetime.strftime(start_date, '%Y%m%d%H')\
                         + '-lindenberg.nc'
    sounding =  xr.open_dataset(file_sonde)
    
    #assign height as coordinate for easier handling
    sounding  = sounding.assign_coords({"height" : sounding.height})
    
    
    return sounding


def in_cloudnet(start_date):
    path_classification = '/home/ralf/Studium/Bachelorarbeit/Target_Classifications/'
    file_cloudnet = path_classification + dt.datetime.strftime(start_date, '%Y%m%d') \
          + '_lindenberg_classification.nc'
    
      #Merge current cloudnet dataset with previous day and next days  dataset +- 3hours !
    if dt.datetime.strftime(start_date, '%H') == "00":
           file_cloudnet_plus = path_classification + \
               dt.datetime.strftime(start_date - timedelta(hours=3), '%Y%m%d')\
               + '_lindenberg_classification.nc'
           d_cloudnet = (xr.open_dataset(file_cloudnet))
           d_cloudnet_previous = xr.open_dataset(file_cloudnet_plus)
           d_cloudnet = xr.merge([d_cloudnet_previous, d_cloudnet])\
               .sel(time=slice(start_date - timedelta(hours =3), start_date + timedelta(hours = 3)))
    else:
           d_cloudnet = xr.open_dataset(file_cloudnet)\
               .sel(time=slice(start_date - timedelta(hours =3), start_date + timedelta(hours = 3)))
    
    
    
    return d_cloudnet         
      
