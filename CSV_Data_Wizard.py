"""
Created on Thu Jul 10 13:01:50 2025

@author: justin
"""
#Importing the used Modules
import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import os

# Start of the working code
# Creating the class of the app itself
class CSVInputApp:
    def __init__(self, master):
        self.master = master
        self.master.title("CSV Data Wizard")
        self.df = None

        self.master.geometry("1000x600")

        self.notebook = ttk.Notebook(master)
        self.notebook.grid(row=0, column=0, padx=10, pady=10, sticky="NSEW")
# The tab for input of the data in csv format
        self.input_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.input_tab, text="Input")
# 
        self.file_path_label = tk.Label(self.input_tab, text="File Path:")
        self.file_path_label.grid(row=0, column=0, padx=10, pady=10)
        self.file_path_entry = tk.Entry(self.input_tab, width=40)
        self.file_path_entry.grid(row=0, column=1, padx=10, pady=10)
        self.browse_button = tk.Button(self.input_tab, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)

        self.decimal_label = tk.Label(self.input_tab, text="Decimal Denoter:")
        self.decimal_label.grid(row=1, column=0, padx=10, pady=10)
        self.decimal_entry = tk.Entry(self.input_tab, width=5)
        self.decimal_entry.grid(row=1, column=1, padx=10, pady=10)

        self.separator_label = tk.Label(self.input_tab, text="Cell Separator:")
        self.separator_label.grid(row=2, column=0, padx=10, pady=10)
        self.separator_entry = tk.Entry(self.input_tab, width=5)
        self.separator_entry.grid(row=2, column=1, padx=10, pady=10)

        self.submit_button = tk.Button(self.input_tab, text="Submit", command=self.process_data)
        self.submit_button.grid(row=3, column=1, pady=20)

        self.plot_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.plot_tab, text="Plots")

        plot_types = ["Line Chart", "Bar Chart", "Heatmap", "Scatter Plot", "Box Plot"]
        for i, plot_type in enumerate(plot_types):
            button = tk.Button(self.plot_tab, text=plot_type, command=lambda t=plot_type: self.plot_data(t))
            button.grid(row=0, column=i, padx=5, pady=10)

        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(self.master, textvariable=self.status_var, font=("Helvetica", 10), bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, sticky="WE")

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        sns.set_theme(style="whitegrid")

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)

    def process_data(self):
        file_path = self.file_path_entry.get()
        if not file_path:
            self.print_to_status_bar("❗ Please select a CSV file first.")
            return

        decimal_denoter = self.decimal_entry.get() or '.'
        cell_separator = self.separator_entry.get() or ','

        try:
            self.df = pd.read_csv(file_path, sep=cell_separator, decimal=decimal_denoter)
            file_name = os.path.basename(file_path)
            self.print_to_status_bar(f"✅ Loaded: {file_name}")
        except Exception as e:
            self.print_to_status_bar(f"❌ Error: {e}")

    def plot_data(self, plot_type):
        if self.df is None:
            self.print_to_status_bar("❗ Please submit data first.")
            return

        self.clear_plot_frame()
        fig, ax = plt.subplots()

        try:
            x = self.df.columns[0]
            y_cols = self.df.columns[1:]

            if plot_type == "Line Chart":
                for y in y_cols:
                    sns.lineplot(data=self.df, x=x, y=y, ax=ax, label=y)
            elif plot_type == "Bar Chart":
                for y in y_cols:
                    sns.barplot(x=self.df[x], y=self.df[y], ax=ax, ci=None, label=y)
            elif plot_type == "Scatter Plot":
                for y in y_cols:
                    sns.scatterplot(data=self.df, x=x, y=y, ax=ax, label=y)
            elif plot_type == "Box Plot":
                melted = self.df.melt(id_vars=x, var_name="Variable", value_name="Value")
                sns.boxplot(data=melted, x="Variable", y="Value", ax=ax)
            elif plot_type == "Heatmap":
                sns.heatmap(self.df.corr(numeric_only=True), cmap="viridis", ax=ax, annot=True)

            ax.set_title(plot_type)
            self.show_plot(fig)
        except Exception as e:
            self.print_to_status_bar(f"❌ Plotting error: {e}")

    def show_plot(self, fig):
        canvas = FigureCanvasTkAgg(fig, master=self.plot_tab)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=1, column=0, columnspan=5, padx=10, pady=10, sticky="NSEW")
        canvas.draw()

    def clear_plot_frame(self):
        for widget in self.plot_tab.winfo_children():
            if isinstance(widget, tk.Button):
                continue
            widget.destroy()

    def print_to_status_bar(self, message):
        self.status_var.set(message)
        self.master.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVInputApp(root)
    root.mainloop()
