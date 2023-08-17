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


#####################################################
#Metpy Units: Implement withouth breaking everything?
#####################################################


#Remove height slicing to above 100m at function level and implement at actual
#calculation level to have more general functions?


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
    
    cl_i = cloudnet.target_classification.where((cloudnet.height >= cloudbase) & (cloudnet.height <= cloudtop))
    
    #remove all non-Ice cloud pixel data!
    
    cl_i = cl_i.where(((cl_i >=4) & (cl_i <=7)))
    
    #detect if ice pixel in cloud_layer
    #check if all entries in array are nan
    all_nan = np.isnan(cl_i).all()
    
    #check if array contains any cloud pixel classed as ice
    any_int = np.issubdtype(cl_i.dtype, float)
    
    if all_nan:
        contains_ice = False
    elif any_int:
        contains_ice = True
    
    return contains_ice




def contains_ice_thresh(cloudnet):

    cloudbase = get_cloudbase(cloudnet)
    
    cloudtop = get_cloudtop(cloudnet)
    
    cl_i = cloudnet.target_classification.where(
        (cloudnet.height >= cloudbase) & (cloudnet.height <= cloudtop))
    
    
    count_ice = np.sum(cl_i.where(((cl_i >=4) & (cl_i <= 7)), drop = True))
        
    count_cloud_pixel = np.sum(cl_i.where(((cl_i >=1) & (cl_i <=7)),drop = True))
    
    
    #nan_count = np.sum(~np.isnan(cl_i))
    
    percentage_ice = (count_ice/ count_cloud_pixel)*100
    
    #Threshold of 5% (Radenz 2021)!
    
    threshold = 5
    
    if percentage_ice >= threshold:
       return(True)
    else:
        return(False)
    
    print("runtime func "+str(datetime.now() - start_time ))


def contains_ice_thresh_new(cloudnet):
    
    cloudbase = get_cloudbase(cloudnet)
    
    cloudtop = get_cloudtop(cloudnet)
    
    cl_i = cloudnet.target_classification.where(
        (cloudnet.height >= cloudbase) & (cloudnet.height <= cloudtop)).values
    
    start_time = datetime.now()
    
    count_ice = np.sum(np.where((cl_i >=4) & (cl_i <= 5)))
    
    count_cloud_pixel = np.sum(np.where((cl_i >=1) & (cl_i <=7)))
    
    percentage_ice = (count_ice/ count_cloud_pixel)*100
    
    # print(percentage_ice)
    # #set to arbitrary treshold for testing!
    
    #threshold = 5
    
    # if percentage_ice >= threshold:
    #     contains_ice  =True
    # else:
    #     contains_ice = False
        
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
    # theta.name = "theta"
    
    # profile = xr.merge([theta, sounding])    
    #profile = profile.assign_coords({"height" : profile.height})
    ##Already assigned by read_files module!
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
    #     #cloud_base_val = 
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
    except:
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
    except:
        decoupling_height.append(np.nan)


def pbl_theta_new(sounding):
    #Calculate inversion height through greatest gradient of potential temperature in troposphere
    #Cut to above 100 meter and below cloud_top_height   
    theta= theta_profile(sounding)    
    
    #Differentiate to with respect to height
    
    gradient_theta = theta.where((theta.height[0] >= 100) & (theta.height < 12000) ).differentiate(coord = "height")
    
    #Find first spike in gradient from surface upwards?    
    
    gradient_theta = gradient_theta.where(gradient_theta > 0).dropna(dim= "time")
           
    for hidx in np.arange(gradient_theta.size):
        if gradient_theta[hidx] >= 0.05:
            max_grad_height = gradient_theta[hidx].height
            break
    return max_grad_height.values.item()




