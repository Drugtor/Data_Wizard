"""
Created on Thu Jul 10 13:01:50 2025

@author: Drugtor (mostly just via GPT promts with minor adjustments from me)
It's barely optimised, but much better than my first version :)
"""

""" Packages used for this application """
import tkinter as tk
from tkinter import ttk, filedialog
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import date


""" Initial def. of the app window type and the tabs inside"""
class CSVInputApp:
    def __init__(self, master):
        self.master = master
        self.master.title("CSV Data Wizard")
        self.df = None
        self.selected_plot_type = tk.StringVar(value="Line Chart")
        self.selected_plot_type.trace_add("write", lambda *args: self.toggle_axis_limit_controls())

        self.master.geometry("1000x600")
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)

        """ The tabs with their different functions """
        self.notebook = ttk.Notebook(master)
        self.notebook.grid(row=0, column=0, padx=10, pady=10, sticky="NSEW")
        
        self.create_input_tab()
        self.create_data_tab()
        self.create_plot_tab()
        
        """ Creating the statusbar on the bottom of the window """
        self.status_var = tk.StringVar()
        tk.Label(self.master, textvariable=self.status_var, font=("Helvetica", 10), bd=1, relief=tk.SUNKEN, anchor=tk.W).grid(row=1, column=0, sticky="EW")
        sns.set_theme(style="darkgrid") #style of the plots in seaborn


    """ The input tab for selecting the CSV file  """
    def create_input_tab(self):
        self.input_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.input_tab, text="Input")

        """ The file path input line, with an option to browse with a button next to it """
        tk.Label(self.input_tab, text="File Path:").grid(row=0, column=0, padx=10, pady=10)
        self.file_path_entry = tk.Entry(self.input_tab, width=40)
        self.file_path_entry.grid(row=0, column=1, padx=10, pady=10, sticky="EW")
        self.file_path_entry.bind("<Return>", lambda e: self.process_data())

        tk.Button(self.input_tab, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=10, pady=10)

        """ Due to different denotion types in CSV/TXT two more entry tabs for decimal and cell separator.
        If left empty a default will be used . for decimal and , for cell
        Additionally to support other file encodings an entry tab for 'Encoding type' the defualt beeing UTF-8"""
        tk.Label(self.input_tab, text="Decimal Denoter:").grid(row=1, column=0, padx=10, pady=10)
        self.decimal_entry = tk.Entry(self.input_tab, width=5)
        self.decimal_entry.grid(row=1, column=1, padx=10, pady=10, sticky="W")
        self.decimal_entry.bind("<Return>", lambda e: self.process_data())

        tk.Label(self.input_tab, text="Cell Separator:").grid(row=2, column=0, padx=10, pady=10)
        self.separator_entry = tk.Entry(self.input_tab, width=5)
        self.separator_entry.grid(row=2, column=1, padx=10, pady=10, sticky="W")
        self.separator_entry.bind("<Return>", lambda e: self.process_data())

        tk.Label(self.input_tab, text="Encoding:").grid(row=3, column=0, padx=10, pady=10)
        self.encoding_entry = tk.Entry(self.input_tab, width=15)
        self.encoding_entry.grid(row=3, column=1, padx=10, pady=10, sticky="W")
        self.encoding_entry.insert(0, "utf-8")

        tk.Button(self.input_tab, text="Submit", command=self.process_data).grid(row=4, column=1, pady=20, sticky="W")
        self.input_tab.columnconfigure(1, weight=1)


    """ A simple data review Tab so one can see what pandas made of their CSV """
    def create_data_tab(self):
        self.data_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.data_tab, text="Data View")
        
        self.tree = ttk.Treeview(self.data_tab, show="headings")
        self.tree.grid(row=0, column=0, sticky="NSEW")
        
        vsb = ttk.Scrollbar(self.data_tab, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="NS")
        hsb = ttk.Scrollbar(self.data_tab, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, sticky="EW")
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.data_tab.columnconfigure(0, weight=1)
        self.data_tab.rowconfigure(0, weight=1)


    """ The plotting tab with a toolbar on the left and a plotting canvas on the right """
    def create_plot_tab(self):
        self.plot_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.plot_tab, text="Plots")
        self.plot_tab.rowconfigure(0, weight=1)
        self.plot_tab.columnconfigure(2, weight=1)
        
        """ The toolbar with its scrollbar in column 0 and 1 """
        self.toolbar_container = tk.Canvas(self.plot_tab, borderwidth=0, width=260, background="#d4d0c8", highlightthickness=0)
        self.toolbar_scroll = tk.Scrollbar(self.plot_tab, orient="vertical", command=self.toolbar_container.yview)
        self.toolbar_container.configure(yscrollcommand=self.toolbar_scroll.set)
        self.toolbar_container.grid(row=0, column=1, sticky="NSW", padx=(0, 0), pady=0)
        self.toolbar_scroll.grid(row=0, column=0, sticky="NS")
        
        """ Design of the Toolbar in the style of Windows XP """
        self.toolbar_frame = tk.Frame(self.toolbar_container, bg="#d4d0c8", relief="groove", bd=2)
        self.toolbar_container.create_window((0, 0), window=self.toolbar_frame, anchor="nw")
        self.toolbar_frame.bind("<Configure>", lambda e: self.toolbar_container.configure(scrollregion=self.toolbar_container.bbox("all")))

        self.create_toolbar_sections()
        
        """ The plotting canvas in column 2 """
        self.plot_display = tk.Frame(self.plot_tab)
        self.plot_display.grid(row=0, column=2, sticky="NSEW", padx=(5, 0), pady=5)

    """ Subsections of the toolbar """
    def create_toolbar_sections(self):
        """ Plottypes can be chosen here """
        plot_type_frame = tk.LabelFrame(self.toolbar_frame, text="Plot Type")
        plot_type_frame.pack(fill="x", pady=5)
        for pt in ["Line Chart", "Bar Chart", "Heatmap", "Scatter Plot", "Box Plot"]:
            tk.Radiobutton(plot_type_frame, text=pt, variable=self.selected_plot_type, value=pt).pack(anchor="w")

        """ Options for the axis (limits) which can either be automatic or manual  """
        axes_frame = tk.LabelFrame(self.toolbar_frame, text="Axes")
        axes_frame.pack(fill="x", pady=5)
        
        tk.Label(axes_frame, text="X-Axis:").pack(anchor="w")
        self.x_axis_combo = ttk.Combobox(axes_frame, state="readonly")
        self.x_axis_combo.pack(fill="x")
        
        tk.Label(axes_frame, text="Y-Axis (multiple):").pack(anchor="w")
        self.y_axis_listbox = tk.Listbox(axes_frame, selectmode="multiple", exportselection=0, height=5)
        self.y_axis_listbox.pack(fill="x")
        self.auto_scale_var = tk.BooleanVar(value=True)
        
        tk.Checkbutton(axes_frame, text="Auto Scale", variable=self.auto_scale_var, command=self.toggle_axis_limit_controls).pack(anchor="w")
        limits_frame = tk.Frame(axes_frame)
        limits_frame.pack(fill="x", pady=(5, 0))
        
        tk.Label(limits_frame, text="X Limits:").grid(row=0, column=0, sticky="w")
        self.xmin_entry = tk.Entry(limits_frame, width=8)
        self.xmin_entry.grid(row=0, column=1, padx=2)
        self.xmax_entry = tk.Entry(limits_frame, width=8)
        self.xmax_entry.grid(row=0, column=2, padx=2)
        
        tk.Label(limits_frame, text="Y Limits:").grid(row=1, column=0, sticky="w")
        self.ymin_entry = tk.Entry(limits_frame, width=8)
        self.ymin_entry.grid(row=1, column=1, padx=2)
        self.ymax_entry = tk.Entry(limits_frame, width=8)
        self.ymax_entry.grid(row=1, column=2, padx=2)

        """ Label for axis and title  """
        labels_frame = tk.LabelFrame(self.toolbar_frame, text="Labels")
        labels_frame.pack(fill="x", pady=5)
        
        tk.Label(labels_frame, text="Plot Title:").pack(anchor="w")
        self.title_entry = tk.Entry(labels_frame)
        self.title_entry.pack(fill="x")
        
        tk.Label(labels_frame, text="X Label:").pack(anchor="w")
        self.xlabel_entry = tk.Entry(labels_frame)
        self.xlabel_entry.pack(fill="x")
        
        tk.Label(labels_frame, text="Y Label:").pack(anchor="w")
        self.ylabel_entry = tk.Entry(labels_frame)
        self.ylabel_entry.pack(fill="x")
        
        """ plot and export buttons """
        actions_frame = tk.LabelFrame(self.toolbar_frame, text="Actions")
        actions_frame.pack(fill="x", pady=5)
        tk.Button(actions_frame, text="Plot", command=self.plot_from_selection).pack(side="left", expand=True, fill="x", padx=2, pady=2)
        tk.Button(actions_frame, text="Export as PNG", command=self.export_current_plot).pack(side="left", expand=True, fill="x", padx=2, pady=2)


    """Opens a dialog window for choosing a file and copying the path in the text box"""
    def browse_file(self):
       file_path = filedialog.askopenfilename(
           filetypes=[
               ("CSV Files", "*.csv"),
               ("Text Files", "*.txt"),
               ("Excel Files", "*.xlsx;*.xls"),
               ("Alle Dateien", "*.*")
           ]
       )
       if file_path:
           self.file_path_entry.delete(0, tk.END)
           self.file_path_entry.insert(0, file_path)


    """ Reads the CSV file with the userdefined (or default) denoters and shows it in the data tab.
    Additionally it also displays the axis options for plotting"""
    def process_data(self):
       file_path = self.file_path_entry.get()
       if not file_path:
           self.print_to_status_bar("❗ Bitte wähle zuerst eine Datei aus.")
           return

       decimal_denoter = self.decimal_entry.get() or '.'
       cell_separator = self.separator_entry.get() or ','
       encoding_type = self.encoding_entry.get() or "utf-8"

       try:
           ext = os.path.splitext(file_path)[1].lower()
           if ext in [".csv", ".txt"]:
               try:
                   self.df = pd.read_csv(file_path, sep=cell_separator, decimal=decimal_denoter, encoding=encoding_type)
               except UnicodeDecodeError:
                   self.print_to_status_bar(f"⚠️ Encoding-Fehler mit {encoding_type}, versuche 'latin1'")
                   self.df = pd.read_csv(file_path, sep=cell_separator, decimal=decimal_denoter, encoding='latin1')
           elif ext in [".xlsx", ".xls"]:
               self.df = pd.read_excel(file_path)
           else:
               raise ValueError(f"Nicht unterstützter Dateityp: {ext}")

           file_name = os.path.basename(file_path)
           self.print_to_status_bar(f"✅ Geladen: {file_name}")
           self.show_data_in_table()
           self.populate_axis_selectors()
           self.toggle_axis_limit_controls()
       except Exception as e:
           self.print_to_status_bar(f"❌ Fehler: {e}")
    
    
    """ Shows the first 500 lines of data in a table """
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
        
    
    """ Fills the the axis selction with the column names from the data only numeric for Y axis """
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


    """ Dynamic activation of the Axis limits depending on Plottype and 'Autoscale' activity """
    def toggle_axis_limit_controls(self):
        state = "disabled" if self.auto_scale_var.get() or self.selected_plot_type.get() == "Heatmap" else "normal"
        for widget in [
            self.xmin_entry, self.xmax_entry,
            self.ymin_entry, self.ymax_entry
        ]:
            widget.configure(state=state)

        # Disable axis selectors if Heatmap is selected
        axis_state = "disabled" if self.selected_plot_type.get() == "Heatmap" else "readonly"
        listbox_state = "disabled" if self.selected_plot_type.get() == "Heatmap" else "normal"
        self.x_axis_combo.configure(state=axis_state)
        self.y_axis_listbox.configure(state=listbox_state)


    """ Checks the Plottype and starts plotting """
    def plot_from_selection(self):
        self.plot_data(self.selected_plot_type.get())


    """ Plots the Diagramm based on the chosen settings. The settings are also validated for correct syntax. """
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

            if plot_type != "Heatmap":
              if not x and not y_cols:
                  self.print_to_status_bar("❗ Please select X and Y axes.")
                  return
              elif not x:
                  self.print_to_status_bar("❗ Please select an X axis.")
                  return
              elif not y_cols:
                  self.print_to_status_bar("❗ Please select at least one Y axis.")
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

            ax.set_title(self.title_entry.get())
            ax.set_xlabel(self.xlabel_entry.get())
            ax.set_ylabel(self.ylabel_entry.get())

            # Optional axis limits
            try:
                if not self.auto_scale_var.get():
                    xmin = float(self.xmin_entry.get()) if self.xmin_entry.get() else None
                    xmax = float(self.xmax_entry.get()) if self.xmax_entry.get() else None
                    ymin = float(self.ymin_entry.get()) if self.ymin_entry.get() else None
                    ymax = float(self.ymax_entry.get()) if self.ymax_entry.get() else None

                    if xmin is not None and xmax is not None and xmin >= xmax:
                        raise ValueError("X min must be less than X max")
                    if ymin is not None and ymax is not None and ymin >= ymax:
                        raise ValueError("Y min must be less than Y max")

                    if xmin is not None or xmax is not None:
                        ax.set_xlim(xmin, xmax)
                    if ymin is not None or ymax is not None:
                        ax.set_ylim(ymin, ymax)
            except ValueError:
                self.print_to_status_bar("⚠️ Ungültige Achsengrenzen oder Min >= Max. Ignoriert.")
                self.print_to_status_bar("⚠️ Ungültiger Zahlenwert für Achsenlimits. Ignoriert.")

            self.show_plot(fig)
        except Exception as e:
            self.print_to_status_bar(f"❌ Plotting error: {e}")


    """ Shows the diagramm on the canvas of the Plot-tab """
    def show_plot(self, fig):
        canvas = FigureCanvasTkAgg(fig, master=self.plot_display)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True)
        canvas.draw()


    """ Clears previous diagramms from the canvas """
    def clear_plot_frame(self):
        for widget in self.plot_display.winfo_children():
            widget.destroy()

    """ Exports the current plot as a png in a user defined directory """
    def export_current_plot(self):
        try:
            file_title = self.title_entry.get()
            today = str(date.today())
            fig = plt.gcf()
            default_name = f"{today}-{file_title}.png"
            file_path = filedialog.asksaveasfilename(
                initialfile=default_name,
                defaultextension=".png",
                filetypes=[("PNG files", "*.png")],
                title="Save Plot As..."
            )
            if file_path:
                fig.savefig(file_path, dpi=300, format="png")
                self.print_to_status_bar(f"✅ Plot gespeichert: {os.path.basename(file_path)}")
        except Exception as e:
            self.print_to_status_bar(f"❌ Fehler beim Speichern: {e}")


    """ Looks for new mesages for the status bar """
    def print_to_status_bar(self, message):
        self.status_var.set(message)
        self.master.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVInputApp(root)
    root.mainloop()
