#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  3 17:28:31 2023

@author: ralf
"""

import numpy as np
import xarray as xr
import pandas as pd
import datetime as dt
from datetime import datetime, timedelta
import math
from metpy.calc import *
from metpy.calc import mixing_ratio_from_relative_humidity
from metpy.calc import virtual_potential_temperature
from metpy.calc import gradient_richardson_number
from metpy.units import units



#Define functions

def cloudnet_slicer(cloudnet):
    start_time= cloudnet.time[0].values
    end_time = cloudnet.time[cloudnet.time.size-1].values
    
    cloud_layer = get_cloud_layer(cloudnet)
        
    cloudnet_chunk = []
    for chunk_start in pd.date_range(start_time, end_time, freq='30T'):
        chunk_end = chunk_start + pd.Timedelta(minutes=30)
        chunk = cloudnet.sel(time=slice(chunk_start, chunk_end))
        cloudnet_chunk.append(chunk)
    
    return cloudnet_chunk


def contains_ice(cloudnet):
    
    cloudbase = get_cloudbase(cloudnet)
    
    cloudtop = get_cloudtop(cloudnet)
    
    cl_i = cloudnet.target_classification.where(
        (cloudnet.height >= cloudbase) & (cloudnet.height <= cloudtop)).values
    
    start_time = datetime.now()
    
    count_ice = np.sum(np.where((cl_i >=4) & (cl_i <= 5)))
    
    count_cloud_pixel = np.sum(np.where((cl_i >=1) & (cl_i <=7)))
    
    percentage_ice = (count_ice/ count_cloud_pixel)*100
    
    return round(percentage_ice,3)

def get_ice_percentage(cloudnet):
    cloudbase = get_cloudbase(cloudnet)
    cloudtop = get_cloudtop(cloudnet)
    
    cl_i = cloudnet.target_classification.where(
        (cloudnet.height >= cloudbase) & (cloudnet.height <= cloudtop)).values
    
    ice_indices = (cl_i >= 4) & (cl_i <= 5)
    cloud_pixel_indices = (cl_i >= 1) & (cl_i <= 7)
    
    count_ice = np.sum(ice_indices)
    count_cloud_pixel = np.sum(cloud_pixel_indices)
    
    if count_cloud_pixel == 0:
        return 0.0 
    
    percentage_ice = (count_ice / count_cloud_pixel) * 100
    
    return round(percentage_ice,3)


def theta_profile(sounding):
      
    theta = (sounding.temperature + 273.15) * \
            (sounding.pressure[0] / sounding.pressure) ** (2/7)
    return theta


def get_cloud_layer(cloudnet):
        
    #Define cloud layer as only liquid/ice classified cloudnet bits
    cloud_layer = cloudnet.target_classification.where((cloudnet.target_classification >= 1)\
                                        &(cloudnet.target_classification <= 8))

                 
    return cloud_layer



def get_cloudbase(cloudnet):  
    
    try:
        cloudbase = cloudnet.cloud_base_height_amsl
        
        #use rolling median to remove outliers!
        
        cloudbase = cloudbase.rolling(time = 30, center = True).median().dropna(dim ="time")
                  
        cloud_base_val = cloudbase.min()
        
        return cloud_base_val
    
    #too few detections: set cloud_base_val to ErrorValue and pass ignore statement to cloudtop function (?)
   
    except:ValueError
        pass

  

def get_cloudtop(cloudnet):
    cloudtop = []
    
    try:
        layer = get_cloud_layer(cloudnet)
         
        cloudbase = get_cloudbase(cloudnet)
        
        for idx in np.arange(len(layer.time)):
            
            t_slice = (layer[idx])                                           
            #Height Index of lowest non NaN Cloudpixel!
            h_idx = t_slice.height.where(t_slice.height >= cloudbase.values).argmin()
            
            while np.isnan(t_slice[h_idx]) != True:
                                
                h_idx += 1
                    
            cloudtop.append(t_slice[h_idx].height.values)
        
        #return max or median of cloudtop for interval?
        #Hannes uses max so for comparability!
        
        cloudtop_val = np.array(cloudtop).max()
        
        return cloudtop_val
    except: ValueError
        pass



def cloud_min_temp(cloudnet, sounding):
    cloudbase = get_cloudbase(cloudnet)
    
    cloudtop = get_cloudtop(cloudnet)
    
    temp_in_layer = sounding.temperature.where((sounding.height > cloudbase) &\
                                               (sounding.height <=cloudtop)).dropna(dim = "time")
    
    cloud_min_temp = temp_in_layer.values.min()
    
    return cloud_min_temp




def decoupling_new(sounding, cloudnet):
    try:    
        cloud_base= get_cloudbase(cloudnet)
        
        decoupling_height = []
               
        theta = theta_profile(sounding)
        
        theta = theta.where((theta.height > theta.height[0] + 100)).dropna(dim = "time")
        
        theta = theta.where((theta.height < cloud_base)).dropna(dim ="time")
            
        height_sounding = theta.height.values
        theta_sounding = theta.values
        theta_threshold = 0.5 
                
        for hidx in range(height_sounding.shape[0]):
        
            theta_cumsum = np.cumsum(theta_sounding[hidx::-1])
        
            theta_cummean = theta_cumsum / np.arange(1,hidx+2)
        
            theta_diff = theta_cummean-theta_sounding[hidx::-1]
            
            
            if (round(np.nanmax(theta_diff),3) >= theta_threshold):
                
                decoupling_height.append(height_sounding[hidx])            
                break   
                    
            # elif(round(np.nanmax(theta_diff),3) <= theta_threshold):
            #           decoupling_height.append(-9999)
                        
        
        if not decoupling_height:
            decoupling_height.append(-9999)
        return np.array(decoupling_height)
    except: ValueError
        decoupling_height.append(np.nan)

