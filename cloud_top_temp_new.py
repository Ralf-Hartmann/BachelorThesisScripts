#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 14:41:33 2023

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
start_date = datetime(2019, 2, 26, 6)
end_date = datetime(2019,12,31,18)


cloudnet = in_cloudnet(start_date)
sounding = in_sounding(start_date)


ct = []
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
                try:
                                        
                    
                    
                    cloudbase = get_cloudbase(layer)

                    cloudtop = get_cloudtop(layer)

                    cloud_top_temp = sounding.temperature.where(sounding.height <= cloudtop).dropna(dim = "time")[-1]
                    
                    ct.append([cloud_top_temp.values, layer["time"][0].dt.strftime("%Y%m%d%H%M").values ])
                    
                    print(layer["time"][0].dt.strftime("%Y-%m-%d-%H-%M").values)
                    print(cloud_top_temp.values)
                                    
    
                except:
                        pass
                
                
                
                
    except: IOError
    pass
    
    start_date += timedelta(hours=6)


# Flatten list
ct_list_arr = np.array([ct])


#reshape to 2 columns -> I hope this doesnt crash
#array.size + 1 to have even integer
ct_list_flat= ct_list_arr.reshape((int((ct_list_arr.size+1)/2), 2))

    
with open("cloud_top_temp"+ "_" + str(dt.datetime.strftime(start_date - timedelta(days = 1), "%Y")) + ".txt", "w") as output:
      for i in np.arange(ct_list_flat.shape[0]):
              output.write(str(ct_list_flat[i, 1]))
              output.write(";")
              output.write(str(ct_list_flat[i, 0]))
              output.write("\n")

    
    
#Check runtime
print("runtime" + " " +str(datetime.now() - start_time ))