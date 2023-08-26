
import datetime as dt
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from calc_new import *
from read_files import *
import xarray as xr
import pandas as pd
import os.path

#Construct dataset of calculated parameters and save as NetCDF for further processing

path = '/home/ralf/Studium/Bachelorarbeit/calc_results/'


dh =  (pd.read_csv(path + "decoupling_new_series.txt", 
                        header = None,
                        names = ["time", "decoupling_height"],
                        skiprows = 0,
                        delimiter = ";", 
                        parse_dates = [0],
                        index_col= 0)).to_xarray()

cmt = (pd.read_csv(path + "cmt/cloud_min_temp_series.txt",
                        header = None,   
                        names = ["time", "cloud_min_temp"],
                        skiprows = 0,
                        delimiter = ";", 
                        parse_dates = [0],
                        index_col= 0)).to_xarray()

ctt = (pd.read_csv(path + "ctt/cloud_top_temp_series.txt",
                        header = None,
                        names = ["time", "cloud_top_temp"],
                        skiprows = 0,
                        delimiter = ";", 
                        parse_dates = [0],
                        index_col= 0)).to_xarray()

cbh = (pd.read_csv(path + "cbh/cloud_base_height_series.txt", 
                        header = None,
                        names = ["time", "cloud_base_height"],
                        skiprows = 0,
                        delimiter = ";", 
                        parse_dates = [0],
                        index_col= 0)).to_xarray()

ice_frac = (pd.read_csv(path + "ice_frac/ice_fraction_series.txt", 
                        header = None,
                        names = ["time", "ice_fraction"],
                        skiprows = 0,
                        delimiter = ";", 
                        parse_dates = [0],
                        index_col= 0)).to_xarray()

ice_perc = (pd.read_csv(path + "ice_frac/new_ice_percentage.txt",
                        header = None,
                        names = ["time", "ice_percentage"],
                        skiprows = 0,
                        delimiter = ";", 
                        parse_dates = [0],
                        index_col= 0)).to_xarray()




dataset = xr.merge([dh, cmt, ctt, cbh,ice_frac, ice_perc])

dataset.to_netcdf(path + "time_series.nc", format = "NETCDF4")
