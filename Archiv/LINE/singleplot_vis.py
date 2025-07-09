# -*- coding: utf-8 -*-
"""
Created on Wed May 31 14:08:40 2023

@author: justin
Raw construct for Datavisualisation, a GUI and adaptaion for different
file Types is in the works
"""
#%% Packages (dont touch)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scienceplots        #needs prior installation eg. via pip install
plt.style.use(['science'])

# Set data requriements (do touch)
# the r infront is only needed if you use single backslashes
path_to_file = r"C:\Users\justi\Desktop\ANB 6\Regelungstechnik\Projekt\Gluc_sprungantwort.csv"
column_separator = ';'
decimal_separator = ','

# import Data (dont touch)
data = pd.read_csv(path_to_file, sep= column_separator, decimal= decimal_separator)

#%% Set figure req. (do touch)
#select data to plot
x_data = data.Zeit
y_data = data.G_1_m
y2_data = data.F_E1_0

#plot settings
plot_linestyle = '--'
plot_linewidth = 2
plot_markerstyle = 'o' 
plot_markersize = 5
plot_xlim = [0, 180]    #work in progress
plot_ylim = [0,0.001]   #work in progress

#gloabal labels
x_axis_label = 'Time [s]'
x_fonts_size = 12

y_axis_label = 'Konzentration'
y_font_size = 12

figure_title = 'Michaelis-Menten des Kommerziellen Enzyms'
title_font_size = 15

figure_size = (16,9)     #x,y good ratio -> 8,5 or 8,4
resolution = 250        #300 gives good clarity above is taxing for pc but better res

# Visualisation (dont touch)
plt.figure(figsize=figure_size ,dpi=resolution)

plt.xlabel(x_axis_label, fontsize=x_fonts_size)
plt.ylabel(y_axis_label, fontsize=y_font_size)
plt.title(figure_title, fontsize=title_font_size)


plt.plot(x_data, y_data,                                    #data to plot
             lw= plot_linewidth, ls= plot_linestyle,        #linestyle
             marker= plot_markerstyle, ms= plot_markersize) #markerstyle