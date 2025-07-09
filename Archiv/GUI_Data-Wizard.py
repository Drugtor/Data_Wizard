# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 10:56:21 2023

@author: justin
GUI for Datavis tool
"""
import tkinter as tk

root = tk.Tk()

root.geometry('800x500')
root.title('Daten Visualierung')

label_disclamer = tk.Label(root, text='This a work in progress', 
                           font=('Arial', 13))
label_disclamer.pack(pady=15)



label_filepath = tk.Label(root, text ='Put in the filepath', 
                           font=('Arial', 13))
label_filepath.pack()

filepath = tk.Text(root,height=1, font=('Arial',12))
filepath.pack(padx=10, pady=10)



label_columnsep = tk.Label(root, text ='Put in the seperator for the column', 
                           font=('Arial', 13))
label_columnsep.pack()

columnsep = tk.Entry(root)
columnsep.pack()



label_decimalsep = tk.Label(root, text ='Put in the decimal separator', 
                           font=('Arial', 13))
label_decimalsep.pack()

decimalsep = tk.Entry(root)
decimalsep.pack()

root.mainloop()
