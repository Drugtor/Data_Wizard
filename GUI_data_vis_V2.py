#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 10 12:54:58 2025

@author: justin
"""

import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import os

class CSVInputApp:
    def __init__(self, master):
        self.master = master
        self.master.title("CSV Input App")
        self.df = None

        self.master.geometry("900x500")

        self.notebook = ttk.Notebook(master)
        self.notebook.grid(row=0, column=0, padx=10, pady=10, sticky="NSEW")

        # Input Tab
        self.input_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.input_tab, text="Input")

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

        # Plot Tab
        self.plot_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.plot_tab, text="Plots")

        plot_types = ["Line Chart", "Bar Chart", "Heatmap", "Scatter Plot"]
        for i, plot_type in enumerate(plot_types):
            button = tk.Button(self.plot_tab, text=plot_type, command=lambda t=plot_type: self.plot_data(t))
            button.grid(row=0, column=i, padx=10, pady=10)

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(self.master, textvariable=self.status_var, font=("Helvetica", 10), bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, sticky="WE")

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

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
            print(self.df)
        except FileNotFoundError:
            msg = "❌ Error: File not found."
            self.print_to_status_bar(msg)
            print(msg)
        except pd.errors.EmptyDataError:
            msg = "❌ Error: The file is empty."
            self.print_to_status_bar(msg)
            print(msg)
        except pd.errors.ParserError:
            msg = "❌ Error: Failed to parse the CSV file. Check separator/decimal."
            self.print_to_status_bar(msg)
            print(msg)
        except Exception as e:
            msg = f"❌ Unexpected error: {e}"
            self.print_to_status_bar(msg)
            print(msg)

    def plot_data(self, plot_type):
        if self.df is None:
            self.print_to_status_bar("❗ Please submit data first.")
            return

        if len(self.df.columns) < 2:
            self.print_to_status_bar("❗ Not enough columns to plot.")
            return

        if plot_type == "Line Chart":
            self.plot_line_chart()
        elif plot_type == "Bar Chart":
            self.plot_bar_chart()
        elif plot_type == "Heatmap":
            self.plot_heatmap()
        elif plot_type == "Scatter Plot":
            self.plot_scatter_plot()

    def limit_ticks(self, ax, axis='x', max_ticks=20):
        if axis == 'x':
            ticks = ax.get_xticks()
            if len(ticks) > max_ticks:
                indices = np.linspace(0, len(ticks) - 1, max_ticks, dtype=int)
                new_ticks = [ticks[i] for i in indices]
                ax.set_xticks(new_ticks)
            for tick in ax.get_xticklabels():
                tick.set_rotation(45)
        elif axis == 'y':
            ticks = ax.get_yticks()
            if len(ticks) > max_ticks:
                indices = np.linspace(0, len(ticks) - 1, max_ticks, dtype=int)
                new_ticks = [ticks[i] for i in indices]
                ax.set_yticks(new_ticks)

    def plot_line_chart(self):
        self.clear_plot_frame()
        fig, ax = plt.subplots()
        x_col = self.df.columns[0]
        y_cols = self.df.columns[1:]
        for y_col in y_cols:
            ax.plot(self.df[x_col], self.df[y_col], label=y_col)
        ax.set_xlabel(x_col)
        ax.set_ylabel("Values")
        ax.legend()
        self.limit_ticks(ax, 'x', max_ticks=20)
        self.show_plot(fig)

    def plot_bar_chart(self):
        self.clear_plot_frame()
        fig, ax = plt.subplots()
        x_col = self.df.columns[0]
        y_cols = self.df.columns[1:]
        bar_width = 0.8 / len(y_cols)
        x = np.arange(len(self.df))
        for i, y_col in enumerate(y_cols):
            ax.bar(x + i * bar_width, self.df[y_col], bar_width, label=y_col)
        ax.set_xticks(x + bar_width * (len(y_cols) - 1) / 2)
        ax.set_xticklabels(self.df[x_col])
        ax.set_xlabel(x_col)
        ax.set_ylabel("Values")
        ax.legend()
        self.limit_ticks(ax, 'x', max_ticks=20)
        self.show_plot(fig)

    def plot_heatmap(self):
        self.clear_plot_frame()
        fig, ax = plt.subplots()
        x_col = self.df.columns[0]
        y_cols = self.df.columns[1:]
        im = ax.imshow(self.df[y_cols].values, cmap="viridis", aspect="auto", interpolation="nearest")
        ax.set_xticks(range(len(self.df)))
        ax.set_xticklabels(self.df[x_col], rotation=45)
        ax.set_yticks(range(len(y_cols)))
        ax.set_yticklabels(y_cols)
        ax.set_xlabel(x_col)
        ax.set_ylabel("Columns")
        fig.colorbar(im, ax=ax)
        self.limit_ticks(ax, 'x', max_ticks=20)
        self.show_plot(fig)

    def plot_scatter_plot(self):
        self.clear_plot_frame()
        fig, ax = plt.subplots()
        x_col = self.df.columns[0]
        y_cols = self.df.columns[1:]
        for y_col in y_cols:
            ax.scatter(self.df[x_col], self.df[y_col], label=y_col)
        ax.set_xlabel(x_col)
        ax.set_ylabel("Values")
        ax.legend()
        self.limit_ticks(ax, 'x', max_ticks=20)
        self.show_plot(fig)

    def show_plot(self, fig):
        canvas = FigureCanvasTkAgg(fig, master=self.plot_tab)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="NSEW")
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
