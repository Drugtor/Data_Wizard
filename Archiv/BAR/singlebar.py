# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 11:10:34 2023

@author: justin
"""

#%% Packages (dont touch)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scienceplots        #needs prior installation eg. via pip install
plt.style.use(['science'])

#%% Set data requriements (do touch)
#the r infront is only needed if you use single backslashes
path_to_file = r"C:\Users\justi\Desktop\ANB 6\TechEnzyme\Diverse Daten\Enzymaktivität_Prozess.CSV"
column_separator = ';'
decimal_separator = ','

# import Data (dont touch)
data = pd.read_csv(path_to_file, sep= column_separator, decimal= decimal_separator)

#%% Set figure req. (do touch)
#select data to plot
x_data = data.Probe
y1_data = data.EA
#y2_data = data.Gesamtprotein
#y3_data = data.VolumenAktivität
#y4_data = data.Gesamtaktivität
#y5_data = data.SpezAktivität

#plot settings
plot_title = 'Eigenes Enzym'
plot_xlim = []      #work in progress
plot_ylim = []      #work in progress

#gloabal labels
x_axis_label = 'Probenummer'
x_fonts_size = 12

y_axis_label = '[nkat/mL]'
y_font_size = 12

figure_title = 'Volumetrische EA'
title_font_size = 15

figure_size = (8,6)     #x,y good ratio -> 8,5 or 8,4
resolution = 250        #300 gives good clarity above is taxing for pc but better res
#%% Visualisation (dont touch)
x_indexes = np.arange(len(x_data))
width = 0.25


plt.figure(figsize=figure_size ,dpi=resolution)

plt.xticks(ticks=x_indexes, labels=x_data)
plt.xlabel(x_axis_label, fontsize=x_fonts_size)
plt.ylabel(y_axis_label, fontsize=y_font_size)
plt.title(figure_title, fontsize=title_font_size)

#plt.bar(x_indexes - 2*width, y1_data, width=width)

#plt.bar(x_indexes - width, y1_data, width=width)

plt.bar(x_indexes, y1_data, width=width)

#plt.bar(x_indexes + width, y2_data, width=width)

#plt.bar(x_indexes + 2*width, y5_data, width=width)