"""
Created on Thu Jul 10 13:01:50 2025

@author: Drugtor (mostly just via GPT promts with minor adjustments from me)
It's barely optimised, but much better than my first version :)
"""

import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import os

class CSVInputApp:
    def __init__(self, master):
        self.master = master
        self.master.title("CSV Data Wizard")
        self.df = None

        self.master.geometry("1000x600")

        self.notebook = ttk.Notebook(master)
        self.notebook.grid(row=0, column=0, padx=10, pady=10, sticky="NSEW")

        # === Input Tab ===
        self.input_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.input_tab, text="Input")

        self.file_path_label = tk.Label(self.input_tab, text="File Path:")
        self.file_path_label.grid(row=0, column=0, padx=10, pady=10)
        self.file_path_entry = tk.Entry(self.input_tab, width=40)
        self.file_path_entry.grid(row=0, column=1, padx=10, pady=10, sticky="EW")
        self.browse_button = tk.Button(self.input_tab, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)

        self.decimal_label = tk.Label(self.input_tab, text="Decimal Denoter:")
        self.decimal_label.grid(row=1, column=0, padx=10, pady=10)
        self.decimal_entry = tk.Entry(self.input_tab, width=5)
        self.decimal_entry.grid(row=1, column=1, padx=10, pady=10, sticky="W")

        self.separator_label = tk.Label(self.input_tab, text="Cell Separator:")
        self.separator_label.grid(row=2, column=0, padx=10, pady=10)
        self.separator_entry = tk.Entry(self.input_tab, width=5)
        self.separator_entry.grid(row=2, column=1, padx=10, pady=10, sticky="W")

        self.submit_button = tk.Button(self.input_tab, text="Submit", command=self.process_data)
        self.submit_button.grid(row=3, column=1, pady=20, sticky="W")

        self.input_tab.columnconfigure(1, weight=1)
        self.input_tab.rowconfigure(3, weight=1)

        # === Data View Tab ===
        self.data_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.data_tab, text="Data View")
        self.notebook.insert(1, self.data_tab)

        self.tree = ttk.Treeview(self.data_tab, show="headings")
        self.tree.grid(row=0, column=0, sticky="NSEW")

        self.vsb = ttk.Scrollbar(self.data_tab, orient="vertical", command=self.tree.yview)
        self.vsb.grid(row=0, column=1, sticky="NS")
        self.hsb = ttk.Scrollbar(self.data_tab, orient="horizontal", command=self.tree.xview)
        self.hsb.grid(row=1, column=0, sticky="EW")
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        self.data_tab.columnconfigure(0, weight=1)
        self.data_tab.rowconfigure(0, weight=1)

        # === Plot Tab ===
        self.plot_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.plot_tab, text="Plots")

        plot_types = ["Line Chart", "Bar Chart", "Heatmap", "Scatter Plot", "Box Plot"]

        spacer = tk.Frame(self.plot_tab)
        spacer.grid(row=0, column=0, sticky="EW")
        self.plot_tab.columnconfigure(0, weight=1)

        for i, plot_type in enumerate(plot_types, start=1):
            button = tk.Button(self.plot_tab, text=plot_type, command=lambda t=plot_type: self.plot_data(t))
            button.grid(row=0, column=i, padx=5, pady=10, sticky="E")

        self.x_axis_label = tk.Label(self.plot_tab, text="X-Axis:")
        self.x_axis_label.grid(row=1, column=0, padx=5, sticky="E")
        self.x_axis_combo = ttk.Combobox(self.plot_tab, state="readonly")
        self.x_axis_combo.grid(row=1, column=1, padx=5, sticky="EW")

        self.y_axis_label = tk.Label(self.plot_tab, text="Y-Axis (multiple):")
        self.y_axis_label.grid(row=1, column=2, padx=5, sticky="E")
        self.y_axis_listbox = tk.Listbox(self.plot_tab, selectmode="multiple", exportselection=0, height=5)
        self.y_axis_listbox.grid(row=1, column=3, padx=5, sticky="EW")

        self.plot_tab.rowconfigure(2, weight=1)
        self.plot_tab.columnconfigure(1, weight=1)
        self.plot_tab.columnconfigure(3, weight=1)

        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(self.master, textvariable=self.status_var, font=("Helvetica", 10), bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, sticky="EW")

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        sns.set_theme(style="darkgrid")

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
            self.show_data_in_table()
            self.populate_axis_selectors()
        except Exception as e:
            self.print_to_status_bar(f"❌ Error: {e}")

    def show_data_in_table(self):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(self.df.columns)

        for col in self.df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="w")

        for i, row in self.df.iterrows():
            if i > 500:
                break
            self.tree.insert("", "end", values=list(row))

    def populate_axis_selectors(self):
        if self.df is None:
            return

        cols = list(self.df.columns)
        num_cols = list(self.df.select_dtypes(include=np.number).columns)

        self.x_axis_combo['values'] = cols
        if cols:
            self.x_axis_combo.current(0)

        self.y_axis_listbox.delete(0, tk.END)
        for col in num_cols:
            self.y_axis_listbox.insert(tk.END, col)

    def plot_data(self, plot_type):
        if self.df is None:
            self.print_to_status_bar("❗ Please submit data first.")
            return

        self.clear_plot_frame()
        fig, ax = plt.subplots()

        try:
            x = self.x_axis_combo.get()
            selected_indices = self.y_axis_listbox.curselection()
            y_cols = [self.y_axis_listbox.get(i) for i in selected_indices]

            if plot_type != "Heatmap" and (not x or not y_cols):
                self.print_to_status_bar("❗ Please select both X and Y axes.")
                return

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
        canvas_widget.grid(row=2, column=0, columnspan=6, padx=10, pady=10, sticky="NSEW")
        canvas.draw()

    def clear_plot_frame(self):
        for widget in self.plot_tab.winfo_children():
            if isinstance(widget, (tk.Button, tk.Label, ttk.Combobox, tk.Listbox, tk.Frame)):
                continue
            widget.destroy()

    def print_to_status_bar(self, message):
        self.status_var.set(message)
        self.master.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVInputApp(root)
    root.mainloop()
