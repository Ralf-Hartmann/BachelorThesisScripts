#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  9 18:49:53 2023

@author: ralf
"""

import datetime as dt
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from calc_new import *
from read_files import *
import xarray as xr
import os.path



start_time = datetime.now()

# Choose starting and end date, define interval of soun



def out_decoupling(start_date, end_date):
    

    decoupling_height = []
    
    
    while (start_date <= end_date):
  
        #try opening file!
        try:
                          
                cloudnet = in_cloudnet(start_date)
                sounding = in_sounding(start_date)
                
                
                sounding = sounding.where(sounding.height.where((sounding.height > sounding.height[0]+100)))
                sounding = sounding.where(sounding.height.where(sounding.height <12000))
                
                ###############
                #Do Something #
                ###############
                
                chunk = cloudnet_slicer(cloudnet)
                                
                for layer in chunk:

                    decoupling_height.append([decoupling_new(sounding, layer).item(),layer["time"][0].dt.strftime("%Y%m%d%H%M").values ])
                    print(layer["time"][0].dt.strftime("%Y-%m-%d-%H-%M").values)
        except: ValueError
                    pass
        
                

        start_date += timedelta(hours=6)
    
    
    
    # Flatten list
    coupling_list_arr = np.array([decoupling_height])
    
    
    #reshape to 2 columns -> I hope this doesnt crash
    #array.size + 1 to have even integer
    coupling_list_flat= coupling_list_arr.reshape((int((coupling_list_arr.size+1)/2), 2))
    
    
    save_path = "/home/ralf/Studium/Bachelorarbeit/calc_results"   
    
    file_name = "decoupling_height_new"+ "_" + str(dt.datetime.strftime(start_date - timedelta(hours = 1), "%Y"))
    
    complete_name = os.path.join(save_path, file_name)
    
    
        
    with open(os.path.join(save_path, complete_name) + ".txt", "w") as output:
          for i in np.arange(coupling_list_flat.shape[0]):
                  output.write(str(coupling_list_flat[i, 1]))
                  output.write(";")
                  output.write(str(coupling_list_flat[i, 0]))
                  output.write("\n")
    
        
        
    #Check runtime
    print("runtime" + " " +str(datetime.now() - start_time ))


def out_cloud_min_temp(start_date, end_date):
    c_m_t = []
    
    while (start_date <= end_date):
        
        
        #try opening file!
        try:
                      
                cloudnet = in_cloudnet(start_date)
                sounding = in_sounding(start_date)
                
                
                sounding = sounding.where(sounding.height.where((sounding.height > sounding.height[0]+100)))
                sounding = sounding.where(sounding.height.where(sounding.height <12000))
                
                ###############
                #Do Something #
                ###############
                            
                chunk = cloudnet_slicer(cloudnet)
    
                for layer in chunk:
                    c_m_t.append([cloud_min_temp(layer, sounding),layer["time"][0].dt.strftime("%Y%m%d%H%M").values ])
                    print(layer["time"][0].dt.strftime("%Y-%m-%d-%H-%M").values)
    
        
        
    
        except:
            pass
        
        start_date += timedelta(hours=6)    
    
    # Flatten list
    c_m_t_arr = np.array([c_m_t])
    
    
    #reshape to 2 columns -> I hope this doesnt crash
    #array.size + 1 to have even integer
    c_m_t_flat= c_m_t_arr.reshape((int((c_m_t_arr.size+1)/2), 2))
    
    save_path = "/home/ralf/Studium/Bachelorarbeit/calc_results"   
    
    file_name = "cloud_min_temp_t"+ "_" + str(dt.datetime.strftime(start_date - timedelta(hours = 1), "%Y"))
    
    complete_name = os.path.join(save_path, file_name)
        
    with open(os.path.join(save_path, complete_name) + ".txt", "w") as output:
          for i in np.arange(c_m_t_flat.shape[0]):
                  output.write(str(c_m_t_flat[i, 1]))
                  output.write(";")
                  output.write(str(c_m_t_flat[i, 0]))
                  output.write("\n")
    
        
        
    #Check runtime
    print("runtime" + " " +str(datetime.now() - start_time ))    
    


def out_ice(start_date, end_date):
    
    ice_flag = []
    
    
    while start_date <= end_date:
        
        try:
            cloudnet = in_cloudnet(start_date)
            sounding = in_sounding(start_date)
            
            chunk = cloudnet_slicer(cloudnet)
                            
            for layer in chunk:
                    try:
                        ice_flag.append([contains_ice(layer)]),
                                    
                                         layer["time"][0].dt.strftime("%Y%m%d%H%M").values ])
                        print(layer["time"][0].dt.strftime("%Y-%m-%d-%H-%M").values)
                    except:
                        pass
        except: 
               pass    
        
        
        start_date += timedelta(hours = 6)
        
        
    # Flatten list
    ice_flag_arr = np.array([ice_flag])


    #reshape to 2 columns -> I hope this doesnt crash
    #array.size + 1 to have even integer
    ice_flag_flat= ice_flag_arr.reshape((int((ice_flag_arr.size+1)/2), 2))
    
    
    
    save_path = "/home/ralf/Studium/Bachelorarbeit/calc_results"   
    
    file_name = "ice_fraction"+ "_" + str(dt.datetime.strftime(start_date - timedelta(hours = 1), "%Y"))
    
    complete_name = os.path.join(save_path, file_name)
        
    with open(os.path.join(save_path, complete_name) + ".txt", "w") as output:
          for i in np.arange(ice_flag_flat.shape[0]):
                  output.write(str(ice_flag_flat[i, 1]))
                  output.write(";")
                  output.write(str(ice_flag_flat[i, 0]))
                  output.write("\n")

        
        
    #Check runtime
    print("runtime" + " " +str(datetime.now() - start_time ))

def out_cloud_base_height(start_date, end_date):

    cloud_base_height = []
    
    while (start_date <= end_date):
            
        #try opening file!
        try:
                      
                cloudnet = in_cloudnet(start_date)
                sounding = in_sounding(start_date)
                
                
                sounding = sounding.where(sounding.height.where((sounding.height > sounding.height[0]+100)))
                sounding = sounding.where(sounding.height.where(sounding.height <12000))
                
                
                chunk = cloudnet_slicer(cloudnet)
                
                for layer in chunk:
                        try:
                            cloud_base_height.append([get_cloudbase(layer).values,layer["time"][0].dt.strftime("%Y%m%d%H%M").values ])
                            print(layer["time"][0].dt.strftime("%Y-%m-%d-%H-%M").values)
                        except:
                            pass
        
        except:
            pass
        start_date += timedelta(hours = 6)              
        
    # Flatten list
    cloud_base_arr = np.array([cloud_base_height])

    #reshape to 2 columns -> I hope this doesnt crash
    #array.size + 1 to have even integer
    cloud_base_flat= cloud_base_arr.reshape((int((cloud_base_arr.size+1)/2), 2))
       
    save_path = "/home/ralf/Studium/Bachelorarbeit/calc_results"   
    
    file_name = "cloud_base_height"+ "_" + str(dt.datetime.strftime(start_date - timedelta(hours = 1), "%Y"))
    
    complete_name = os.path.join(save_path, file_name)
        
    with open(os.path.join(save_path, complete_name) + ".txt", "w") as output:
          for i in np.arange(cloud_base_flat.shape[0]):
                  output.write(str(cloud_base_flat[i, 1]))
                  output.write(";")
                  output.write(str(cloud_base_flat[i, 0]))
                  output.write("\n")

        
        
    #Check runtime
    print("runtime" + " " +str(datetime.now() - start_time ))


def out_cloud_top_height(start_date, end_date):
        
    cloudnet = in_cloudnet(start_date)
    sounding = in_sounding(start_date)
    
    
    cloud_top_height = []
    
    
    while (start_date <= end_date):
            
        #try opening file!
        try:
                      
                cloudnet = in_cloudnet(start_date)
                sounding = in_sounding(start_date)
                
                
                sounding = sounding.where(sounding.height.where((sounding.height > sounding.height[0]+100)))
                sounding = sounding.where(sounding.height.where(sounding.height <12000))
                
                
                chunk = cloudnet_slicer(cloudnet)
                
                for layer in chunk:
                        try:
                            cloud_top_height.append([get_cloudtop(layer),layer["time"][0].dt.strftime("%Y%m%d%H%M").values ])
                            print(layer["time"][0].dt.strftime("%Y-%m-%d-%H-%M").values)
                        except:
                            pass
        
        except:
            pass
        start_date += timedelta(hours = 6)              
        
    # Flatten list
    cloud_base_arr = np.array([cloud_top_height])

    #reshape to 2 columns -> I hope this doesnt crash
    #array.size + 1 to have even integer
    cloud_base_flat= cloud_base_arr.reshape((int((cloud_base_arr.size+1)/2), 2))
       
    save_path = "/home/ralf/Studium/Bachelorarbeit/calc_results"   
    
    file_name = "cloud_top_height"+ "_" + str(dt.datetime.strftime(start_date - timedelta(hours = 1), "%Y"))
    
    complete_name = os.path.join(save_path, file_name)
        
    with open(os.path.join(save_path, complete_name) + ".txt", "w") as output:
          for i in np.arange(cloud_base_flat.shape[0]):
                  output.write(str(cloud_base_flat[i, 1]))
                  output.write(";")
                  output.write(str(cloud_base_flat[i, 0]))
                  output.write("\n")

        
        
    #Check runtime
    print("runtime" + " " +str(datetime.now() - start_time ))                




def process_ice(start_date, end_date):
    
    start_time = datetime.now()
    
    ice_flag = []

    while start_date <= end_date:
        try:
            cloudnet = in_cloudnet(start_date)
            sounding = in_sounding(start_date)

            chunk = cloudnet_slicer(cloudnet)

            for layer in chunk:
                try:
                    ice_percentage = get_ice_percentage(layer)
                    time_str = layer["time"][0].dt.strftime("%Y%m%d%H%M").values
                    ice_flag.append([ice_percentage, time_str])
                    print(layer["time"][0].dt.strftime("%Y-%m-%d-%H-%M").values)
                except:
                    pass
        except:
            pass

        start_date += timedelta(hours=6)

    ice_flag_arr = np.array(ice_flag)

    save_path = "/home/ralf/Studium/Bachelorarbeit/calc_results"
    file_name = "ice_percentage" + "_" + str(dt.datetime.strftime(start_date - timedelta(hours=1), "%Y"))
    complete_name = os.path.join(save_path, file_name)

    with open(os.path.join(save_path, complete_name) + ".txt", "w") as output:
        for i in range(ice_flag_arr.shape[0]):
            output.write(str(ice_flag_arr[i, 1]))
            output.write(";")
            output.write(str(ice_flag_arr[i, 0]))
            output.write("\n")

    print("runtime" + " " + str(datetime.now() - start_time))








                
start_date = datetime(2022, 1, 1, 00)
end_date = datetime(2022, 12, 31,18)




#call functions here !

#out_decoupling(start_date, end_date)

#out_cloud_min_temp(start_date, end_date)

#out_cloud_base_height(start_date, end_date)

#out_cloud_top_height(start_date, end_date)

#out_ice_flag_thresh(start_date, end_date)

#out_pbl_height(start_date, end_date)

#process_ice(start_date, end_date)
