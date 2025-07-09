# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 11:54:36 2024

@author: justin gaurich with help by chatgpt
"""
#%% GUI for input

import tkinter as tk
from tkinter import filedialog
import pandas as pd

class CSVInputApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Data Input App")
        self.df = None  # Initialize df as an instance variable

        # File Path
        self.file_path_label = tk.Label(master, text="File Path:")
        self.file_path_label.grid(row=0, column=0, padx=10, pady=10)
        self.file_path_entry = tk.Entry(master, width=40)
        self.file_path_entry.grid(row=0, column=1, padx=10, pady=10)
        self.browse_button = tk.Button(master, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)

        # Decimal Denoter
        self.decimal_label = tk.Label(master, text="Decimal Denoter:")
        self.decimal_label.grid(row=1, column=0, padx=10, pady=10)
        self.decimal_entry = tk.Entry(master, width=5)
        self.decimal_entry.grid(row=1, column=1, padx=10, pady=10)

        # Cell Separator
        self.separator_label = tk.Label(master, text="Cell Separator:")
        self.separator_label.grid(row=2, column=0, padx=10, pady=10)
        self.separator_entry = tk.Entry(master, width=5)
        self.separator_entry.grid(row=2, column=1, padx=10, pady=10)

        # Submit Button
        self.submit_button = tk.Button(master, text="Submit", command=self.process_data_and_close)
        self.submit_button.grid(row=3, column=1, pady=20)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)

    def process_data_and_close(self):
        global df  # Declare df as a global variable
        file_path = self.file_path_entry.get()
        decimal_denoter = self.decimal_entry.get()
        cell_separator = self.separator_entry.get()

        try:
            # Read CSV into pandas DataFrame
            df = pd.read_csv(file_path, sep=cell_separator, decimal=decimal_denoter)
            print('Data input successful')
        except Exception as e:
            print(f"Error: {e}")

        # Close the Tkinter window
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVInputApp(root)
    root.mainloop()
    
#%%
