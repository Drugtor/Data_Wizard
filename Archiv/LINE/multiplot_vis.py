# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 10:34:16 2023

@author: justin gaurich
"""
#%% Packages (dont touch)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scienceplots        #needs prior installation eg. via pip install
plt.style.use(['science'])

#Set data requriements (do touch)
#the r infront is only needed if you use single backslashes
path_to_file = r"C:\Users\justi\Desktop\ANB 6\Regelungstechnik\Projekt\Gluc_optimiert.csv"
column_separator = ';'
decimal_separator = ','

# import Data (dont touch)
data = pd.read_csv(path_to_file, sep= column_separator, decimal= decimal_separator)


#%% Set figure req. (do touch)
x_data = data.Zeit              #x axis is shared by both plots
y1_data = data.F_E1_0       #y axis for plot 1
y2_data = data.G_1_m        #y axis for plot 2

line = x_data*0 + 100

#plot 1 settings
plot1_title = 'Regelung der Emzymlösung'
plot1_linestyle = '-'
plot1_linewidth = 2
plot1_markerstyle = 'o' 
plot1_markersize = 0
plot1_xlim = [0,15000]
plot1_ylim = []

#plot 2 settings
plot2_title = 'Glukosekonzentration'
plot2_linestyle = '-'
plot2_linewidth = 2
plot2_markerstyle ='o'
plot2_markersize = 0
plot2_xlim = [0,15000]
plot2_ylim = []

#global labels
x_axis_label = '[s]'
y_axis_label = '[kg/m$^3$] [m$^3$/s]'
figure_title = ''

figure_size = (8,6)     #x,y good ratio is 8,5 or 8,4
resolution = 250        #300 gives good clarity above is taxing for pc but better res
#%% subplot Visualisation (dont touch)
# Initialise the subplot function using number of rows and columns
fig, axis = plt.subplots(2, figsize=figure_size ,dpi=resolution)


# For 1st Function
axis[0].plot(x_data, y1_data,                   #data to plot
             lw=plot1_linewidth, ls=plot1_linestyle,        #linestyle
             marker=plot1_markerstyle, ms=plot1_markersize) #markerstyle
axis[0].set_xlim(plot1_xlim)                    #x limit
#axis[0].set_ylim(plot1_ylim)                    #y limit
#axis[0].set_title(plot1_title)                  #title for plot 1

# For 2nd Function
axis[1].plot(x_data, y2_data, line,                  #data to plot
             lw=plot2_linewidth, ls=plot2_linestyle,        #linestyle
             marker=plot2_markerstyle, ms=plot2_markersize) #markerstyle
#axis[1].set_xlim(plot2_xlim)                    #x limit
#axis[1].set_ylim(plot2_ylim)                    #y limit
axis[1].set_title(plot2_title)                  #title for plot 2
  

#global titles / Settings
fig.suptitle(figure_title, fontsize=15)     #global title
fig.supxlabel(x_axis_label, fontsize=12)    #global x axis
fig.supylabel(y_axis_label, fontsize=12)    #global y axis
plt.tight_layout(h_pad=3)