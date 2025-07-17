"""
Created on Thu Jul 10 13:01:50 2025

@author: Drugtor (mostly just via GPT promts with minor adjustments from me)
It's barely optimised, but much better than my first version :)
"""
import tkinter as tk
from tkinter import ttk, filedialog
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class CSVInputApp:
    def __init__(self, master):
        self.master = master
        self.master.title("CSV Data Wizard")
        self.df = None
        self.selected_plot_type = tk.StringVar(value="Line Chart")
        self.selected_plot_type.trace_add("write", lambda *args: self.toggle_axis_limit_controls())

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
        self.file_path_entry.bind("<Return>", lambda e: self.process_data())

        self.browse_button = tk.Button(self.input_tab, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)

        self.decimal_label = tk.Label(self.input_tab, text="Decimal Denoter:")
        self.decimal_label.grid(row=1, column=0, padx=10, pady=10)
        self.decimal_entry = tk.Entry(self.input_tab, width=5)
        self.decimal_entry.grid(row=1, column=1, padx=10, pady=10, sticky="W")
        self.decimal_entry.bind("<Return>", lambda e: self.process_data())

        self.separator_label = tk.Label(self.input_tab, text="Cell Separator:")
        self.separator_label.grid(row=2, column=0, padx=10, pady=10)
        self.separator_entry = tk.Entry(self.input_tab, width=5)
        self.separator_entry.grid(row=2, column=1, padx=10, pady=10, sticky="W")
        self.separator_entry.bind("<Return>", lambda e: self.process_data())

        self.submit_button = tk.Button(self.input_tab, text="Submit", command=self.process_data)
        self.submit_button.grid(row=3, column=1, pady=20, sticky="W")

        self.input_tab.columnconfigure(1, weight=1)
        
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

        self.toolbar_container = tk.Canvas(self.plot_tab, borderwidth=0, width=240, background="#d4d0c8")
        self.toolbar_frame = tk.Frame(self.toolbar_container, bg="#d4d0c8", relief="groove", bd=2, width=240)
        self.toolbar_container.grid(row=0, column=0, rowspan=3, sticky="NS", padx=(0, 5), pady=5)
        self.toolbar_container.create_window((0, 0), window=self.toolbar_frame, anchor="nw")
        self.toolbar_frame.bind("<Configure>", lambda e: self.toolbar_container.configure(scrollregion=self.toolbar_container.bbox("all")))

        # Toolbar-Frame als logische Referenz
        self.toolbar = self.toolbar_frame

        tk.Label(self.toolbar, text="Plot Type:").pack(anchor="w")
        plot_types = ["Line Chart", "Bar Chart", "Heatmap", "Scatter Plot", "Box Plot"]
        for plot_type in plot_types:
            rb = tk.Radiobutton(self.toolbar, text=plot_type, variable=self.selected_plot_type, value=plot_type)
            rb.pack(anchor="w")

        tk.Label(self.toolbar, text="X-Axis:").pack(anchor="w")
        self.x_axis_combo = ttk.Combobox(self.toolbar, state="readonly")
        self.x_axis_combo.pack(fill="x")

        tk.Label(self.toolbar, text="Y-Axis (multiple):").pack(anchor="w")
        self.y_axis_listbox = tk.Listbox(self.toolbar, selectmode="multiple", exportselection=0, height=5)
        self.y_axis_listbox.pack(fill="x")

        tk.Label(self.toolbar, text="Plot Title:").pack(anchor="w")
        self.title_entry = tk.Entry(self.toolbar)
        self.title_entry.pack(fill="x")
        self.title_entry.bind("<Return>", lambda e: self.plot_from_selection())

        tk.Label(self.toolbar, text="X Label:").pack(anchor="w")
        self.xlabel_entry = tk.Entry(self.toolbar)
        self.xlabel_entry.pack(fill="x")

        tk.Label(self.toolbar, text="Y Label:").pack(anchor="w")
        self.ylabel_entry = tk.Entry(self.toolbar)
        self.ylabel_entry.pack(fill="x")

        tk.Label(self.toolbar, text="X Min / Max:").pack(anchor="w")
        self.xmin_entry = tk.Entry(self.toolbar, width=8)
        self.xmin_entry.pack(fill="x")
        self.xmax_entry = tk.Entry(self.toolbar, width=8)
        self.xmax_entry.pack(fill="x")

        tk.Label(self.toolbar, text="Y Min / Max:").pack(anchor="w")
        self.ymin_entry = tk.Entry(self.toolbar, width=8)
        self.ymin_entry.pack(fill="x")
        self.ymax_entry = tk.Entry(self.toolbar, width=8)
        self.ymax_entry.pack(fill="x")

        self.auto_scale_var = tk.BooleanVar(value=True)
        self.auto_scale_check = tk.Checkbutton(self.toolbar, text="Auto Scale", variable=self.auto_scale_var, command=self.toggle_axis_limit_controls)
        self.auto_scale_check.pack(anchor="w")

        self.plot_button = tk.Button(self.toolbar, text="Plot", command=self.plot_from_selection)
        self.plot_button.pack(anchor="s", fill="x", pady=(10, 0))

        self.export_button = tk.Button(self.toolbar, text="Export as PNG", command=self.export_current_plot)
        self.export_button.pack(anchor="s", fill="x", pady=(5, 10))

        self.plot_display = tk.Frame(self.plot_tab)
        self.plot_display.grid(row=0, column=1, rowspan=3, sticky="NSEW", padx=(10, 0), pady=5)

        self.plot_tab.rowconfigure(2, weight=1)
        self.plot_tab.columnconfigure(1, weight=1)

        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(self.master, textvariable=self.status_var, font=("Helvetica", 10), bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, sticky="EW")

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        sns.set_theme(style="whitegrid")

    def browse_file(self):
        """Öffnet einen Dateidialog zur Auswahl einer CSV-Datei und trägt den Pfad in das Eingabefeld ein."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)

    def process_data(self):
        """Liest die CSV-Datei unter Beachtung des benutzerdefinierten Trennzeichens und Dezimalzeichens ein.
        Anschließend werden die Daten angezeigt und die Auswahllisten für Achsen aktualisiert."""
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
            self.toggle_axis_limit_controls()
        except Exception as e:
            self.print_to_status_bar(f"❌ Error: {e}")

    def show_data_in_table(self):
        """Zeigt die eingelesenen Daten (max. 500 Zeilen) im 'Data View'-Tab als Tabelle an."""
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
        """Befüllt die X- und Y-Achsen-Auswahllisten mit Spaltennamen aus dem DataFrame.
        Nur numerische Spalten werden als Y-Achsen vorgeschlagen."""
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

    def toggle_axis_limit_controls(self):
        """Aktiviert oder deaktiviert die Eingabefelder für Achsengrenzen und Achsenwahl,
        abhängig vom Plottyp und ob 'Auto Scale' aktiviert ist."""
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

    def plot_from_selection(self):
        """Ermittelt den gewählten Plottyp aus der Toolbar und startet die Plot-Erstellung."""
        self.plot_data(self.selected_plot_type.get())

    def plot_data(self, plot_type):
        """Erzeugt ein Diagramm basierend auf dem gewählten Typ und den aktuellen Benutzereinstellungen.
        Validiert die Eingaben und konfiguriert Titel, Achsenbeschriftung sowie Achsenlimits."""
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

    def show_plot(self, fig):
        """Zeigt das erzeugte Matplotlib-Diagramm im Plot-Bereich an."""
        canvas = FigureCanvasTkAgg(fig, master=self.plot_display)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True)
        canvas.draw()

    def clear_plot_frame(self):
        """Entfernt alle vorherigen Diagramme aus dem Plot-Anzeigebereich."""
        for widget in self.plot_display.winfo_children():
            widget.destroy()

    def export_current_plot(self):
        """Exportiert den aktuellen Plot als PNG-Datei an benutzerdefiniertem Speicherort."""
        try:
            fig = plt.gcf()
            default_name = "plot.png"
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

    def print_to_status_bar(self, message):
        """Aktualisiert die Statusleiste mit einer Nachricht."""
        self.status_var.set(message)
        self.master.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVInputApp(root)
    root.mainloop()
