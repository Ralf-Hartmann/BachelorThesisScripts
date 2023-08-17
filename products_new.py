#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  2 16:54:24 2023

@author: ralf
"""

import datetime as dt
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from calc_new import *
from read_files import *
from matplotlib.dates import HourLocator, DateFormatter, MinuteLocator
from tabulate import tabulate
import xarray as xr
import os.path
import seaborn as sns
import matplotlib.colors as mcolors


sns.set_theme()
sns.set_style("darkgrid")
plt.rcParams.update({'font.size': 12})
plt.rcParams.update({"axes.labelweight": "bold"})
plt.rcParams.update({"figure.autolayout" : True})

#read in files as product file!
#do not calculate for graphics!

path = '/home/ralf/Studium/Bachelorarbeit/calc_results/'

ds = xr.open_dataset(path + "time_series_data_new.nc")



#choose only times all values are present!
ds = ds.dropna(dim = "time")

def plot_compare(date):
    class_labels = {
     #   0: 'Clear sky',
        1: 'Cloud droplets',
        2: 'Drizzle or rain',
        3: 'Drizzle/rain & \n cloud droplets',
        4: 'Ice',
        5: 'Ice & \n supercooled \n droplets',
        6: 'Melting ice',
        7: 'Melting ice & \n cloud droplets',
        8: 'Aerosol',
        # 9: 'Insects',
        # 10: 'Aerosol &\n insects',
    }
    
    _COLORS = {
    #"white": "#ffffff",
    "lightblue": "#6CFFEC",
    "blue": "#209FF3", 
    "purple": "#BF9AFF",
    "lightsteel": "#a0b0bb",
    "darkpurple": "#464AB9",
    "orange": "#ffa500",
    "yellowgreen": "#C7FA3A",
    # "lightbrown": "#CEBC89",
    # "shockred": "#E64A23",
    # "pink": "#B43757",
    # "mask": "#C8C8C8",
    }

    # Create a custom colormap using the provided colors
    colormap = mcolors.ListedColormap([_COLORS[label] for label in _COLORS])

    cmap = plt.cm.get_cmap(colormap , len(class_labels))

    
    fig, ax = plt.subplots(figsize=(10, 4), ncols=2, sharey= True)
    
    date = date 
    
    cloudnet = in_cloudnet(date)
    cloud_layer = get_cloud_layer(cloudnet)
    
    
    
    class_values = list(class_labels.keys())
    
    plot = cloud_layer.plot(y="height", ax=ax[0], levels=class_values, cmap=cmap, add_colorbar = False)
    
    # Update the color bar with centered ticks and labels from class_labels
    cbar = plt.colorbar(plot, ax=ax[1], ticks=[val + 0.5 for val in class_values])
    cbar.ax.set_yticklabels([class_labels.get(val, '') for val in class_values])
    
    
    cloudnet.cloud_base_height_amsl.plot(ax = ax[0], c = "r", label = "Cloud Base Height (Cloudnet)")
    cloudnet.cloud_top_height_amsl.plot(ax = ax[0], c = "r", linestyle = "dashed", label = "Cloud Top Height (Cloudnet)")
    
    ax[0].legend()
    
    # Set up the x-axis tick locators and formatter
    
    hour_interval = HourLocator(interval=1)  # Show ticks for each half-hour
    formatter = DateFormatter("%H:%M")  # Format as hours and minutes
    
    ax[0].xaxis.set_major_locator(hour_interval)
    ax[0].xaxis.set_major_formatter(formatter)
    ax[0].grid(visible = True)
    ax[0].set_ylabel("Height amsl [km]")
    #ax[0].set_yticklabels(np.arange(0, 14, 2))
    ax[0].grid(True, linestyle='--', linewidth=0.5, color='black')  
    
    #Chunk Data
    
    chunk = cloudnet_slicer(cloudnet)
    step = 1/len(chunk)
     
    cloud_layer.plot(y="height", ax=ax[1], levels=class_values, cmap=cmap, add_colorbar = False)
    
    for i in np.arange(len(chunk)):
        try:        
              ax[1].axhline(get_cloudbase(chunk[i]), xmin = step*i, xmax = step*(i+1), c = "r")
              ax[1].axhline(get_cloudtop(chunk[i]), xmin = step*i, xmax = step*(i+1), c = "r", linestyle = "dashed")
        except:
            pass                              
    
    ax[1].xaxis.set_major_locator(half_hour_interval)
    ax[1].xaxis.set_major_formatter(formatter)
    ax[1].set_ylabel(None)
    ax[1].grid(visible = True)
    ax[1].grid(True, linestyle='--', linewidth=0.5, color='black')  # Add black grid lines 
    
    
    ax[1].axhline(-1, c="r", label="Cloud Base Height (Method)")
    ax[1].axhline(-1, c="r", linestyle="dashed", label="Cloud Top Height (Method)")
    ax[1].legend()

    
    #ax[0].set_xticks(rotation = 45)
    #ax[1].set_xticks(rotation= 45)  
    plt.tight_layout() 
    
   
    date_str = date.strftime("%Y-%m-%d")
    fig.text(0.02, 0.02, "Date: " + date_str, fontsize=12, fontweight = "bold", ha='left', va='top')
    plt.savefig("/home/ralf/Studium/Bachelorarbeit/figures_new_schemes/"  
                + "compare" +datetime.strftime(date, "%Y_%m_%d") 
                + ".png", dpi = 500 )
    plt.show()







def plot_coupling(ds):
    fig, axs = plt.subplots(figsize = (8,4), ncols = 2)
    
    dcoup = ds.where(ds.decoupling_height != -9999).dropna(dim = "time")
    coup  = ds.where(ds.decoupling_height == -9999).dropna(dim = "time")
    
    #weights!
    
    weights_decoup = (np.ones_like(dcoup.cloud_min_temp) / len(dcoup.cloud_min_temp))
    weights_coup = (np.ones_like(coup.cloud_min_temp) / len(coup.cloud_min_temp)) 
    
    weights_decoup_h = (np.ones_like(dcoup.cloud_base_height) / len(dcoup.cloud_base_height))
    weights_coup_h = (np.ones_like(coup.cloud_base_height) / len(coup.cloud_base_height)) 
    
    
    bins = np.arange(-70, 20,2)
    
    #bins = np.linspace(20, -70, 70)
    
    axs[0].hist(dcoup.cloud_min_temp, label = "decoupled clouds",bins = bins,weights = weights_decoup, alpha = 0.65)
    axs[0].hist(coup.cloud_min_temp,label = "coupled clouds",bins = bins, weights = weights_coup, alpha = 0.65)
    
    axs[0].set_title("a)" , loc = "left")
    axs[0].set_ylabel("Relative Frequency")
    axs[0].set_xlabel("Cloud Minimum Temperature [°C]")
    axs[0].grid(visible = True)
    axs[0].grid(True, linestyle='--', linewidth=0.5, color='black')
    axs[0].legend()
    bins_h = np.arange(0, 8000, 200)
    
    #bins = np.linspace(20, -70, 70)
    
    axs[1].hist(dcoup.cloud_base_height,label = "decoupled clouds",bins = bins_h, weights = weights_decoup_h, alpha = 0.65)
    axs[1].hist(coup.cloud_base_height,label = "coupled clouds", bins = bins_h,weights = weights_coup_h, alpha = 0.65)
    axs[1].grid(visible = True)
    axs[1].grid(True, linestyle='--', linewidth=0.5, color='black')
    axs[1].set_title("b)" , loc = "left")
    axs[1].set_ylabel("Relative Frequency")
    axs[1].set_xlabel("Cloud Base Height [m]")
    axs[1].legend()
    
    plt.savefig("/home/ralf/Studium/Bachelorarbeit/figures_new_schemes/cmt_cbh.png", 
                dpi = 500)
    plt.tight_layout()




def tables():
    table = [["Valid Intervals", ds.time.size, "-"],
            ["Observed Cloud Layers",ds.cloud_min_temp.dropna(dim ="time").size,
              100],
                     
             ["Decoupled Layers", dcoup.cloud_min_temp.size, 
              round(dcoup.cloud_min_temp.size/ ds.cloud_min_temp.dropna(dim ="time").size*100,2)],
             
             
             ["Coupled Layers", coup.cloud_min_temp.size,
              round(coup.cloud_min_temp.size/ ds.cloud_min_temp.dropna(dim ="time").size *100,2)]
             ]
    
    headers= ["01.01.2020 - 05.01.2023",  "Cases", "Percentage"]
    
    
    
    
    print(tabulate(table, headers, tablefmt = "latex"))
    
    
    
    
    
    table_temp = [["Total Layers", "100" + (str(ds.cloud_min_temp.size)), round(dcoup.cloud_min_temp.size / ds.cloud_min_temp.size*100,2) , 
                                            round(coup.cloud_min_temp.size/ ds.cloud_min_temp.size*100,2)],
                  
                  ["T $<$ -40° ",
                  round((ds.time.where(ds.cloud_min_temp < -40).dropna(dim = "time").size / ds.cloud_min_temp.size *100),2),                  
                  round((dcoup.time.where(ds.cloud_min_temp < -40).dropna(dim = "time").size / ds.cloud_min_temp.size *100),2),              
                  round((coup.time.where(ds.cloud_min_temp < -40).dropna(dim = "time").size / ds.cloud_min_temp.size*100),2)],
                  
                  ["-40° $<=$ T < -20°",
                   round((ds.time.where((ds.cloud_min_temp >= -40)& (ds.cloud_min_temp < -20)).dropna(dim = "time").size/ ds.cloud_min_temp.size *100),2),

                   round((dcoup.time.where((ds.cloud_min_temp >= -40)& (ds.cloud_min_temp < -20)).dropna(dim = "time").size/ ds.cloud_min_temp.size *100),2),
                   round((coup.time.where((ds.cloud_min_temp >= -40)& (ds.cloud_min_temp < -20)).dropna(dim = "time").size/ ds.cloud_min_temp.size *100),2)],              
                  
                  ["-20° $<=$ T < -10°",
                     round((ds.time.where((ds.cloud_min_temp >= -20)& (ds.cloud_min_temp < -10)).dropna(dim = "time").size/ ds.cloud_min_temp.size *100),2),

                     round((dcoup.time.where((ds.cloud_min_temp >= -20)& (ds.cloud_min_temp < -10)).dropna(dim = "time").size/ ds.cloud_min_temp.size *100),2),
                     round((coup.time.where((ds.cloud_min_temp >= -20)& (ds.cloud_min_temp < -10)).dropna(dim = "time").size/ ds.cloud_min_temp.size *100),2)],              
    
                  ["-10° $<=$ T < 0°",
                   round((ds.time.where((ds.cloud_min_temp >= -10)& (ds.cloud_min_temp < 0)).dropna(dim = "time").size/ ds.cloud_min_temp.size *100),2),

                   round((dcoup.time.where((ds.cloud_min_temp >= -10)& (ds.cloud_min_temp < 0)).dropna(dim = "time").size/ ds.cloud_min_temp.size *100),2),
                   round((coup.time.where((ds.cloud_min_temp >= -10)& (ds.cloud_min_temp < 0)).dropna(dim = "time").size/ ds.cloud_min_temp.size *100),2)],              
    
                  ["T $>=$ 0° ", 
                    round((ds.time.where(ds.cloud_min_temp >= 0).dropna(dim = "time").size / ds.cloud_min_temp.size *100),2),              

                    round((dcoup.time.where(ds.cloud_min_temp >= 0).dropna(dim = "time").size / ds.cloud_min_temp.size *100),2),              
                    round((coup.time.where(ds.cloud_min_temp >= 0).dropna(dim = "time").size / ds.cloud_min_temp.size*100),2)],
                                                
                  
                  
                  ]
    headers_temp = ["Temperature Regime", "All Layers [%]", "Decoupled Layers [%] ", "Percentage Coupled Layers [%]"]
    
    print(tabulate(table_temp, headers_temp, tablefmt = "latex_raw"))

    table_ice = [["Total Layers", "Ice containing layers", "Non-Ice containing layers"],
                 [ds.ice_fraction.size, ds.ice_fraction.where(ds.ice_fraction > 5, drop = True).size, ds.ice_fraction.where(ds.ice_fraction <5, drop = True).size]

                     ]
    print(tabulate(table_ice, tablefmt = "latex"))



def plot_cmt_ctt():
    fig, ax = plt.subplots(figsize = (6,4))
    
    bins = np.arange(-70, 20, 2)
    
    ax.hist(ds.cloud_top_temp, bins = bins, density = True, label = "cloud top temp", alpha  =.65)
    ax.hist(ds.cloud_min_temp, bins = bins, density = True, label = "cloud min temp", alpha = .65)
    ax.grid(visible = True)
    ax.grid(True, linestyle='--', linewidth=0.5, color='black')
    
    #ax.scatter(ds.cloud_top_temp, ds.cloud_min_temp)
    
    ax.set_xlabel("Temperature [°C]")
    ax.set_ylabel("Relative Frequency")
    
    plt.savefig("cmt_ctt.png", dpi = 1000)
    plt.tight_layout()
    plt.legend()


def plot_cbh_cmt():
    
    dcoup = ds.where(ds.decoupling_height != -9999).dropna(dim = "time")
    coup  = ds.where(ds.decoupling_height == -9999).dropna(dim = "time")

    
    fig, ax = plt.subplots(figsize = (4,6))
    
    bins = np.arange(-70, 20, 2)
    
    
    ax.hist(ds.cloud_top_temp, bins = bins, density = True, label = "cloud top temp", alpha  =.65)
    ax.hist(ds.cloud_min_temp, bins = bins, density = True, label = "cloud min temp", alpha = .65)
    ax.grid(visible = True)
    ax.grid(True, linestyle='--', linewidth=0.5, color='black')

    
    ax.set_xlabel("Temperature [°C]")
    ax.set_ylabel("Relative Frequency")
    
    plt.savefig("figures_new_schemes/cmh_cbh.png", dpi = 1000)

    plt.legend()
    

def ice_coud_decoup():
    
    
    
    dcoup = ds.where(ds.decoupling_height != -9999, drop = True)
    coup  = ds.where(ds.decoupling_height == -9999, drop = True)

    ice_temp_d = dcoup.cloud_top_temp.where(dcoup.ice_fraction > 5, drop  = True)
    ice_temp_c = coup.cloud_top_temp.where(coup.ice_fraction > 5, drop  = True)
    
    l_temp_d = dcoup.cloud_top_temp.where(dcoup.ice_fraction <= 5, drop  = True)
    l_temp_c = coup.cloud_top_temp.where(coup.ice_fraction <= 5, drop  = True)
    
    
    fig, (ax1, ax2) = plt.subplots(figsize = (10,4), ncols = 2)
    
    bins = np.arange(-70, 20, 2)
    
    ax1.hist(ice_temp_d, bins = bins, density = True, label = "Decoupled Clouds", alpha  =.65)
    ax1.hist(ice_temp_c, bins = bins, density = True, label = "Coupled Clouds", alpha = .65)
    ax1.grid(visible = True)
    ax1.grid(True, linestyle='--', linewidth=0.5, color='black')
    
    #ax.scatter(ds.cloud_top_temp, ds.cloud_min_temp)
    
    ax1.set_xlabel("Cloud Minimum Temperature [°C]")
    ax1.set_ylabel("Relative Frequency")
    ax1.set_title("a) Ice-containing Clouds", ha = "center")
    ax1.legend()
    
    ax2.hist(l_temp_d, bins = bins, density = True, label = "Decoupled Clouds", alpha  =.65)
    ax2.hist(l_temp_c, bins = bins, density = True, label = "Coupled Clouds", alpha = .65)
    ax2.grid(visible = True)
    ax2.grid(True, linestyle='--', linewidth=0.5, color='black')
    ax2.set_xlabel("Cloud Minimum Temperature [°C]")
    ax2.set_title("b) Liquid Clouds", ha = "center")

    ax2.legend()
    plt.tight_layout()

def cth_ice():
    
    dcoup = ds.where(ds.decoupling_height != -9999, drop = True)
    coup  = ds.where(ds.decoupling_height == -9999, drop = True)

    # ice_temp_d = dcoup.cloud_top_temp.where(dcoup.ice_fraction > 5, drop  = True)
    # ice_temp_c = coup.cloud_top_temp.where(coup.ice_fraction > 5, drop  = True)
    
    # l_temp_d = dcoup.cloud_top_temp.where(dcoup.ice_fraction <= 5, drop  = True)
    # l_temp_c = coup.cloud_top_temp.where(coup.ice_fraction <= 5, drop  = True)
    
    cbh_dc = dcoup.cloud_base_height.where(dcoup.ice_fraction > 5, drop = True)
    cbh_c = coup.cloud_base_height.where(coup.ice_fraction > 5, drop = True)
    
    cbh_dc_li = dcoup.cloud_base_height.where(dcoup.ice_fraction <= 5, drop = True)
    cbh_c_li = coup.cloud_base_height.where(coup.ice_fraction <= 5, drop = True)
    
    fig, (ax1, ax2) = plt.subplots(figsize = (10,4), ncols = 2)
    
    bins = np.arange(0, 10000, 200)
    
    ax1.hist(cbh_dc, bins = bins, density = True, label = "Decoupled Clouds", alpha  =.65)
    ax1.hist(cbh_c, bins = bins, density = True, label = "Coupled Clouds", alpha = .65)
    ax1.grid(visible = True)
    ax1.grid(True, linestyle='--', linewidth=0.5, color='black')
    
    #ax.scatter(ds.cloud_top_temp, ds.cloud_min_temp)
    
    ax1.set_xlabel("Cloud Base Height [m]")
    ax1.set_ylabel("Relative Frequency")
    ax1.set_title("a) Ice-containing Clouds", ha = "center")
    ax1.legend()
    
    ax2.hist(cbh_dc_li, bins = bins, density = True, label = "Decoupled Clouds", alpha  =.65)
    ax2.hist(cbh_c_li, bins = bins, density = True, label = "Coupled Clouds", alpha = .65)
    ax2.grid(visible = True)
    ax2.grid(True, linestyle='--', linewidth=0.5, color='black')
    ax2.set_xlabel("Cloud Base Height [m]")
    ax2.set_title("b) Liquid Clouds", ha = "center")

    # ax2.legend()
    plt.tight_layout()




def plot_ice_fraction(ds):
    
    
    #ds = ds.where(ds.cloud_min_temp <= 0, drop = True)
    
    ds = ds.where((ds.cloud_min_temp > -22) & (ds.cloud_min_temp < 2)).dropna(dim = "time")
    
    dcoup = ds.where(ds.decoupling_height != -9999).dropna(dim = "time")
    coup  = ds.where(ds.decoupling_height == -9999).dropna(dim = "time")
    

    bins = np.arange(-21,2,2)

    bin_labels = np.arange(-20, 1, 2)
    
    ds_grouped = ds.groupby_bins(ds.cloud_min_temp, bins = bins, labels = bin_labels)
    
    dcoup_grouped = dcoup.groupby_bins(dcoup.cloud_min_temp, bins = bins, labels = bin_labels)
    
    coup_grouped = coup.groupby_bins(coup.cloud_min_temp, bins = bins, labels = bin_labels)
    
    all_counts = ds_grouped.count(dim = "time")
    
    dcoup_counts = dcoup_grouped.count(dim='time')
    
    coup_counts = coup_grouped.count(dim = "time")
    
    def calc_percentage(group):
        total_clouds = group.ice_fraction.size
        #threshold of 5 %
        ice_clouds = (group.ice_fraction.where(group.ice_fraction > 5).sum())
        percentage = (ice_clouds / total_clouds)
        return percentage
    


    def error_bar(group):
        n = ds.cloud_min_temp.size
        
        f = group/100
               
        return np.sqrt((f - f**2)/n)
    
    
    
    
    fig, ax = plt.subplots(figsize = (14, 6))
    
    percentages = ds_grouped.apply(calc_percentage)
    perc_decoup = dcoup_grouped.apply(calc_percentage)
    perc_coup = coup_grouped.apply(calc_percentage)
    
    
    print(perc_decoup)
    print(perc_coup)
    
    
    sigma = error_bar(percentages)
    sigma_d = error_bar(perc_decoup)
    sigma_c = error_bar(perc_coup)
    
    ax.errorbar(percentages.cloud_min_temp_bins, percentages, yerr=sigma*1000, label = "All Clouds", c= 'C0', capsize=3, capthick=3)
    
    ax.errorbar(perc_decoup.cloud_min_temp_bins, perc_decoup, yerr = sigma_d*1000, label = "Decoupled Clouds", c = "C1", capsize=3, capthick=3)
    
    ax.errorbar(perc_coup.cloud_min_temp_bins, perc_coup, yerr = sigma*1000,label = "Coupled Clouds",c = "C2", capsize=3, capthick=3)
    

    ax.text(-26,  ax.get_ylim()[1]+12, "N All Clouds", c = "C0")
    ax.text(-26,  ax.get_ylim()[1]+6, "N Decoupled Cases", c= "C1")
    ax.text(-26,  ax.get_ylim()[1]+0,"N Coupled Cases", c= "C2")
    ax.text(4, ax.get_ylim()[1]+12, " = "+ str(int(dcoup_counts.ice_fraction.sum().values + coup_counts.ice_fraction.sum().values)) , c = "C0")
    ax.text(4, ax.get_ylim()[1]+0, " = " +str(int(coup_counts.ice_fraction.sum().values)), c = "C2")
    ax.text(4, ax.get_ylim()[1]+6, " = " +str(int(dcoup_counts.ice_fraction.sum().values)), c = "C1")
    ax.grid(True, linestyle='--', linewidth=0.5, color='black')
    
    
    # Add text annotations for counts above the upper x-axis
    for x, count in zip(dcoup_counts.cloud_min_temp_bins.values, dcoup_counts.ice_fraction.values):
        count_str = str(int(count.item())) if not np.isnan(count) else '0'
        ax.text(x.item(), ax.get_ylim()[1]+6, count_str, ha='center', va='bottom', c = "C1")
    
    for x, count in zip(coup_counts.cloud_min_temp_bins.values, coup_counts.ice_fraction.values):
        count_str = str(int(count.item())) if not np.isnan(count) else '0'
        ax.text(x.item(), ax.get_ylim()[1], count_str, ha='center', va='bottom', c = "C2")
    
    for x, count in zip(all_counts.cloud_min_temp_bins.values, all_counts.ice_fraction.values):
       count_str = str(int(count.item())) if not np.isnan(count) else '0'
       ax.text(x.item(), ax.get_ylim()[1]+12, count_str, ha='center', va='bottom', c = "C0")
    

    plt.ylabel("Fraction of Ice-Containing Clouds [%]")
    plt.xlabel("Cloud Minimum Temperature [°C]")
    plt.xticks(np.arange(-20, 2, 2))
    plt.xlim(-21, 1)
    plt.ylim(0,105)
    plt.legend(loc = "lower left")
    plt.show()
    plt.close()


def plot_ice_fraction_height(ds):
    
    
    #ds = ds.where(ds.cloud_min_temp <= 0, drop = True)
    
    ds = ds.where((ds.cloud_base_height >= 0) & (ds.cloud_base_height <= 8000)).dropna(dim = "time")
    
    dcoup = ds.where(ds.decoupling_height != -9999, drop = True)
    coup  = ds.where(ds.decoupling_height == -9999, drop = True)
    

    bins = np.arange(0,4400,200)

    bin_labels = np.arange(0, 4200, 200)
    
    ds_grouped = ds.groupby_bins(ds.cloud_base_height, bins = bins, labels = bin_labels)
    
    dcoup_grouped = dcoup.groupby_bins(dcoup.cloud_base_height, bins = bins, labels = bin_labels)
    
    coup_grouped = coup.groupby_bins(coup.cloud_base_height, bins = bins, labels = bin_labels)
    
    all_counts = ds_grouped.count(dim = "time")
    
    dcoup_counts = dcoup_grouped.count(dim='time')
    
    coup_counts = coup_grouped.count(dim = "time")
    
    def calc_percentage(group):
        total_clouds = group.ice_fraction.size
        #threshold of 5 %
        ice_clouds = (group.ice_fraction.where(group.ice_fraction > 5).sum())
        percentage = (ice_clouds / total_clouds)
        return percentage

    def error_bar(group):
        n = ds.cloud_base_height.size
        
        f = group/100
               
        return np.sqrt((f - f**2)/n)
       
    
    fig, ax = plt.subplots(figsize = (12, 6))
    
    
    percentages = ds_grouped.apply(calc_percentage)
    perc_decoup = dcoup_grouped.apply(calc_percentage)
    perc_coup = coup_grouped.apply(calc_percentage)
    
    
    
    
    
    sigma = error_bar(percentages)
    sigma_d = error_bar(perc_decoup)
    sigma_c = error_bar(perc_coup)
    
    print(sigma_d[11:])
    print(sigma_c[11:])
    
    ax.errorbar(percentages.cloud_base_height_bins, percentages, yerr=sigma, label = "All Clouds", c= 'C0', capsize=3, capthick=3)
    
    ax.errorbar(perc_decoup.cloud_base_height_bins, perc_decoup, yerr = sigma_d*1000, label = "Decoupled Clouds", c = "C1", capsize=3, capthick=3)
    
    ax.errorbar(perc_coup.cloud_base_height_bins, perc_coup, yerr = sigma*1000,label = "Coupled Clouds",c = "C2", capsize=3, capthick=3)
    
    
    ax.text(-1000,  ax.get_ylim()[1]+10, "N All Clouds", c = "C0")
    ax.text(-1000,  ax.get_ylim()[1]+5, "N Decoupled Cases", c= "C1")
    ax.text(-1000,  ax.get_ylim()[1]+0,"N Coupled Cases", c= "C2")
    ax.text(4200, ax.get_ylim()[1]+10, " = "+ str(int(dcoup_counts.ice_fraction.sum().values + coup_counts.ice_fraction.sum().values)) , c = "C0")
    ax.text(4200, ax.get_ylim()[1]+0, " = " +str(int(coup_counts.ice_fraction.sum().values)), c = "C2")
    ax.text(4200, ax.get_ylim()[1]+5, " = " +str(int(dcoup_counts.ice_fraction.sum().values)), c = "C1")
    ax.grid(True, linestyle='--', linewidth=0.5, color='black')
    
    
    # Add text annotations for counts above the upper x-axis
    for x, count in zip(dcoup_counts.cloud_base_height_bins.values, dcoup_counts.ice_fraction.values):
        count_str = str(int(count.item())) if not np.isnan(count) else '0'
        ax.text(x.item(), ax.get_ylim()[1] + 5, count_str, ha='center', va='bottom', c="C1", fontsize=11)
        
    for x, count in zip(coup_counts.cloud_base_height_bins.values, coup_counts.ice_fraction.values):
        count_str = str(int(count.item())) if not np.isnan(count) else '0'
        ax.text(x.item(), ax.get_ylim()[1], count_str, ha='center', va='bottom', c="C2", fontsize=11)
        
    for x, count in zip(all_counts.cloud_base_height_bins.values, all_counts.ice_fraction.values):
        count_str = str(int(count.item())) if not np.isnan(count) else '0'
        ax.text(x.item(), ax.get_ylim()[1] + 10, count_str, ha='center', va='bottom', c="C0", fontsize=11)
    
    # ...

    
    # Set x-axis tick labels to be integer values
    
    plt.ylabel("Fraction of Ice-Containing Clouds [%]")
    plt.xlabel("Cloud Base Height [m]")
    plt.xlim(0, 4000)
    #plt.ylim(0,105)
    plt.legend(loc = "lower right´")
    plt.tight_layout()
    plt.show()
    plt.close()

#plot_ice_fraction_height(ds)




def case_study(date, height, dc, Tmin, Tmax):
    
    sns.set_style("darkgrid")

    
    class_labels = {
     #   0: 'Clear sky',
        1: 'Cloud droplets',
        2: 'Drizzle or rain',
        3: 'Drizzle/rain & \n cloud droplets',
        4: 'Ice',
        5: 'Ice & \n supercooled \n droplets',
        6: 'Melting ice',
        7: 'Melting ice & \n cloud droplets',
        8: 'Aerosol',
        # 9: 'Insects',
        # 10: 'Aerosol &\n insects',
    }
    
    _COLORS = {
        #"white": "#ffffff",
        "lightblue": "#6CFFEC",
        "blue": "#209FF3", 
        "purple": "#BF9AFF",
        "lightsteel": "#a0b0bb",
        "darkpurple": "#464AB9",
        "orange": "#ffa500",
        "yellowgreen": "#C7FA3A",
        # "lightbrown": "#CEBC89",
        # "shockred": "#E64A23",
        # "pink": "#B43757",
        # "mask": "#C8C8C8",
        }

    # Create a custom colormap using the provided colors
    colormap = mcolors.ListedColormap([_COLORS[label] for label in _COLORS])

    cmap = plt.cm.get_cmap(colormap , len(class_labels))

    
    date = date
    
    interval =  slice(date - timedelta(hours = 3), date + timedelta(hours = 3) )
    
    select = ds.sel(time = interval)
    
    
    cmt_mean = select.cloud_min_temp.mean()
    
    cloud_layer = get_cloud_layer(in_cloudnet(date))
    
    sounding  = in_sounding(date)
    
    cloudnet = in_cloudnet(date)
    
    
    
    #plot cloudlayer
    
    chunk = cloudnet_slicer(cloudnet)
        
    #cloud_layer = get_cloud_layer(cloudnet)
     
    theta = theta_profile(sounding)
    
    temp = sounding.temperature +273.15
    
    fig, axs = plt.subplots(figsize = (10, 5), ncols = 2, sharey= True)
     
    plt.rcParams.update({"font.size":12})
    
    
    # Get the discrete class values from class_labels
    class_values = list(class_labels.keys())
    
    # Plot the cloud_layer using class_values for the levels
    plot = cloud_layer.plot(y="height", ax=axs[0], levels=class_values,
                            cmap=cmap, add_colorbar = False)
    
    
    # Update the color bar with centered ticks and labels from class_labels
    cbar = plt.colorbar(plot, ax=axs[0], ticks=[val + 0.5 for val in class_values])
    cbar.ax.set_yticklabels([class_labels.get(val, '') for val in class_values])
 
    step = 1/len(chunk)
    

    
    half_hour_interval = HourLocator(interval=1)  # Show ticks for each half-hour
    formatter = DateFormatter("%H:%M")  # Format as hours and minutes
    
    # Apply the tick locators and formatter to the x-axis
    axs[0].xaxis.set_major_locator(half_hour_interval)
    axs[0].xaxis.set_major_formatter(formatter)
    axs[0].set_ylabel("Height amsl [km]")
    
    
    axs[0].grid(visible = True)
    axs[0].grid(True, linestyle='--', linewidth=0.5, color='black')  # Add black grid lines 
    
    for i in np.arange(len(chunk)):
         
         try: 
             
             axs[0].axhline(select.cloud_base_height[i], xmin = step*i,
                            xmax = step*(i+1), linewidth = 2, c = "r")
     
             axs[0].axhline(get_cloudtop(chunk[i]), xmin = step*i, 
                            xmax = step*(i+1),
                            c = "r", linewidth = 2,linestyle = "dashed")
                                 
             decoupling_height = select.decoupling_height[i]
             
             
             if decoupling_height != -9999:
                axs[0].axhline(decoupling_height, xmin=step * i,
                               xmax=step * (i + 1), 
                               c="black", linewidth = 2,linestyle = "dotted" )
    
         except:
             pass
    
            
    
    h_lim = height
    

    axs[0].set_ylim(0, h_lim)
    #axs[0].set_yticklabels(np.arange(0, ((height/1000)+2), 2))


    
    temp = sounding.temperature.where(sounding.height < h_lim, drop = True) +273.15
    
    theta.where(theta.height < h_lim,drop = True).plot(y = "height",
                                                       ax = axs[1], 
                                                       label = r"$\Theta$")
    
    temp.plot(y = "height" ,ax = axs[1], label = r"$T$")
    
    
    axs[1].yaxis.set_tick_params(labelbottom = True)
    axs[1].set_xlim(Tmin, Tmax)
    
    axs[1].set_xlabel(r"Temperature [K]")
    axs[1].set_ylabel(None)
    
    
    if dc ==  True:
        axs[0].legend(["Cloud Base Height", "Cloud Top Height"
            ,"Decoupling Height"], loc = "upper right")
        axs[1].axhline(select.decoupling_height.where(select.decoupling_height != -9999, 
                                                 drop = True).mean(), c = "black", 
                  linestyle = "dotted", label = "Decoupling Height")
    if dc == False:
        axs[0].legend(["Cloud Base Height", "Cloud Top Height"
             ], loc = "upper right")
    
    
    axs[1].legend(loc = "upper right")

    axs[1].grid(True, linestyle='--', linewidth=0.5, color='black')  
    
    date_str = date.strftime("%Y-%m-%d")
    date_hr = date.strftime("%H")
    axs[0].set_title("Date: " +  date_str, fontsize=12 , fontweight = "bold", loc = "left")
    axs[1].set_title("Radiosonde Launch Time: " + date_hr + "UTC", fontweight = "bold", loc = "left")
    fig.subplots_adjust(wspace = 0.5)
    plt.xticks(rotation = 0 )
    plt.tight_layout()
    plt.savefig("/home/ralf/Studium/Bachelorarbeit/figures_new_schemes/"  
                + "case_study" + "_" + datetime.strftime(date, "%Y_%m_%d") + "_" + str(height) 
                + ".png", dpi = 500 )
    plt.show()



def kde_dist(ds):
     
    # dcoup = ds.where(ds.decoupling_height != -9999).dropna(dim = "time")
    # coup  = ds.where(ds.decoupling_height == -9999).dropna(dim = "time")
    
    dcoup = ds.where(ds.decoupling_height != -9999, drop = True)
    coup  = ds.where(ds.decoupling_height == -9999, drop = True)
    
    #bins = np.arange(-70, 20, 2)
    
    fig, ax  = plt.subplots(figsize = (12, 6), ncols = 2, sharey =True, sharex= True)
    
    
    def normalize(arr):
        return (arr - arr.min()) / (arr.max() - arr.min())

    
    dcoup["cloud_base_height"] = normalize(dcoup["cloud_base_height"])
    coup["cloud_base_height"] = normalize(coup["cloud_base_height"])
    
    dcoup["cloud_min_temp"] = normalize(dcoup["cloud_min_temp"]) 
    coup["cloud_min_temp"] = normalize(coup["cloud_min_temp"])

    
    weights_decoup = (np.ones_like(dcoup.cloud_min_temp) / len(dcoup.cloud_min_temp)) 
    weights_coup = (np.ones_like(coup.cloud_min_temp) / len(coup.cloud_min_temp)) 
    
        
    levels = normalize(np.arange(-70, 20, 2))*100
    
    sns.kdeplot(data = coup,x = "cloud_min_temp", 
                y = "cloud_base_height" , 
                cmap = "Oranges",
                fill =True,
                
                #levels = levels,
                weights = weights_coup,
                common_norm = True,
                cbar_kws={"label" : "relative frequency [%]"} ,
                cbar = True,           
                ax = ax[1],
                bw =0.2
                #label = "Coupled Clouds")
    )
    ax[0].set_xlabel("Cloud minimum Temperature [°C]")
    ax[0].set_ylabel("Cloud Base Height [m]")
    
    sns.kdeplot(data = dcoup ,x = "cloud_min_temp", 
                y = "cloud_base_height" , 
                cmap = "Blues",
                fill =True,
                
                #levels = levels,
                weights = weights_decoup,
                common_norm = True,
                cbar = True, 
                cbar_kws={"label" : "relative frequency [%]"} ,
                ax = ax[0],
                bw =0.2
                #label = "Decoupled Cloud")
    )
    ax[0].set_xlabel("Cloud Minimum Temperature [°C]")
    ax[0].set_ylabel("Cloud Base Height [m]")
    ax[0].set_title("Decoupled Clouds", fontweight = "bold")
    ax[0].set_yticklabels(np.arange(0, 12000, 2000))
    ax[0].set_xticklabels(np.arange(-100, 40, 20))
    ax[0].grid(visible = True)
    ax[0].grid(True, linestyle='--', linewidth=0.5, color='black')  #
    ax[0].set_ylim(0)
    
    ax[1].set_xlabel("Cloud Minimum Temperature [°C]")
    ax[1].set_ylabel("Cloud Base Height [m]")
    ax[1].grid(visible = True)
    ax[1].grid(True, linestyle='--', linewidth=0.5, color='black')  #
    ax[1].set_title("Coupled Clouds", fontweight = "bold")
    ax[1].set_xticklabels(np.arange(-100, 40, 20))
    ax[1].set_ylim(0,1)

    plt.tight_layout()
    
    
    fig.subplots_adjust(wspace = 1)

    
    plt.show()
    plt.close()
    
    
    
def kde_ice(ds):
    # dcoup = ds.where(ds.decoupling_height != -9999).dropna(dim="time")
    # coup = ds.where(ds.decoupling_height == -9999).dropna(dim="time")
    
    dcoup = ds.where(ds.decoupling_height != -9999, drop=True)
    coup = ds.where(ds.decoupling_height == -9999, drop=True)
    
    # bins = np.arange(-70, 20, 2)
    
    fig, ax = plt.subplots(figsize=(12, 6), ncols=2, sharey=True, sharex=True)
    
    
    def normalize(arr):
        return (arr - arr.min()) / (arr.max() - arr.min())
    
    dcoup["cloud_base_height"] = normalize(dcoup["cloud_base_height"])
    coup["cloud_base_height"] = normalize(coup["cloud_base_height"])
    
    dcoup["ice_fraction"] = normalize(dcoup["ice_fraction"])
    coup["ice_fraction"] = normalize(coup["ice_fraction"])
    
    
    
    # weights_decoup = (np.ones_like(dcoup.ice_fraction) / len(dcoup.ice_fraction))
    # weights_coup = (np.ones_like(coup.ice_fraction) / len(coup.ice_fraction))
    
    # levels = normalize(np.arange(0, 100, 2)) * 100
    
    sns.kdeplot(data=coup, x="ice_fraction",
                y="cloud_base_height",
                cmap="Oranges",
                fill=True,
    
                # levels = levels,
               # weights=weights_coup,
                common_norm=True,
                cbar_kws={"label": "relative frequency [%]"},
                cbar=True,
                ax=ax[1],
                bw=0.2
                # label = "Coupled Clouds")
                )
    ax[0].set_xlabel("Ice Fraction")
    ax[0].set_ylabel("Cloud Base Height [m]")
    
    sns.kdeplot(data=dcoup, x="ice_fraction",
                y="cloud_base_height",
                cmap="Blues",
                fill=True,
    
                # levels = levels,
               # weights=weights_decoup,
                common_norm=True,
                cbar=True,
                cbar_kws={"label": "relative frequency [%]"},
                ax=ax[0],
                bw=0.2
                # label = "Decoupled Cloud")
                )
    
    
    
    ax[0].set_xlabel("Ice Fraction")
    ax[0].set_ylabel("Cloud Base Height amsl [m]")
    ax[0].set_title("Decoupled Clouds", fontweight="bold")
    ax[0].set_xticklabels(np.arange(0, 100,10))
    ax[0].set_yticklabels(np.arange(0, 12000, 2000))
    ax[0].grid(visible=True)
    ax[0].grid(True, linestyle='--', linewidth=0.5, color='black')
    #ax[0].set_xlim(0, 1)
    ax[0].set_ylim(0)
    
    ax[1].set_xlabel("Ice Fraction")
    ax[1].set_ylabel("Cloud Base Height amsl [m]")
    ax[1].grid(visible=True)
    ax[1].grid(True, linestyle='--', linewidth=0.5, color='black')
    ax[1].set_title("Coupled Clouds", fontweight="bold")
    ax[1].set_xticklabels(np.arange(0, 100,10))
    #ax[1].set_xlim(0, 1)

    ax[1].set_ylim(0, 1)
    
    plt.tight_layout()
    
    fig.subplots_adjust(wspace=1)
    
    plt.show()
    plt.close()


    



def seasons():
    
    month  = ds.time.dt.month.data

    season = np.full(month.shape, "    ")


        
    season[np.isin(month, [11, 12, 1])] = "NDJ"
    season[np.isin(month, [2, 3, 4])] = "FMA"
    season[np.isin(month, [5, 6, 7])] = "MJJ"
    season[np.isin(month, [8, 9,10])] = "ASO"
    season = ds.time.copy(data=season)
    
    ds_grouped= ds.groupby(season)
    
    spring = ds_grouped["FMA"]
    summer = ds_grouped["MJJ"]
    fall = ds_grouped["ASO"]
    winter = ds_grouped["NDJ"]
    
    #plot_ice_fraction(ds)
    
    kde_ice(winter)
    
    # plot_ice_fraction(spring)
    # plot_ice_fraction(summer)
    # plot_ice_fraction(fall)
    # plot_ice_fraction(winter)
    
    # plot_ice_fraction_height(spring)
    # plot_ice_fraction_height(summer)
    # plot_ice_fraction_height(fall)
    # plot_ice_fraction_height(winter)
    
    # plot_coupling(spring)
    # plot_coupling(summer)
    # plot_coupling(fall)
    # plot_coupling(winter)
    
    
    # kde_dist(spring)
    # kde_dist(summer)
    # kde_dist(fall)
    # kde_dist(winter)



"""Call Functions Below"""


#tables()

#plot_cmt_ctt()

#plot_cbh_cmt()

#plot_coupling(ds)

#plot_compare(datetime(2022, 1, 9, 18))   

#kde_dist(ds)

plot_compare(datetime(2022,1,9, 18))

#date, height, decoupled?, tmin, tmax

case_study(datetime(2022,1,9, 18), 6000, False, 240, 320)
case_study(datetime(2022,1,26, 12), 4000, False, 260, 300)
case_study(datetime(2022,12,5, 12), 6000, True, 240, 320)



    
#plot_ice_fraction(ds)


    


