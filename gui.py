# gui.py - Full QtPy GUI for Data Wizard with logging
import os
import sys
import seaborn as sns
import matplotlib
matplotlib.use('Agg')

# Prefer PySide6 via QtPy if not set
if 'QT_API' not in os.environ:
    os.environ['QT_API'] = 'pyside6'

from qtpy import QtCore
from qtpy.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QGroupBox, QRadioButton,
    QComboBox, QListWidget, QListWidgetItem, QAbstractItemView, QCheckBox,
    QFormLayout, QGridLayout, QTableView, QStatusBar, QHeaderView, QSplitter
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import date

from core import DataWizardCore, logger


class PandasModel(QtCore.QAbstractTableModel):
    """Simple DataFrame model for QTableView."""
    def __init__(self, df=pd.DataFrame(), parent=None):
        super().__init__(parent)
        self._df = df

    def setDataFrame(self, df):
        self.beginResetModel()
        self._df = df
        self.endResetModel()

    def rowCount(self, parent=QtCore.QModelIndex()):
        return 0 if self._df is None else len(self._df.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 0 if self._df is None else len(self._df.columns)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or self._df is None:
            return None
        if role == QtCore.Qt.DisplayRole:
            val = self._df.iat[index.row(), index.column()]
            if pd.isna(val):
                return ""
            return str(val)
        return None

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole or self._df is None:
            return None
        if orientation == QtCore.Qt.Horizontal:
            try:
                return str(self._df.columns[section])
            except Exception:
                return None
        else:
            try:
                return str(self._df.index[section])
            except Exception:
                return None


class DataWizardGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Data Wizard (QtPy · PySide6)")
        self.resize(1120, 720)
        sns.set_theme(style='darkgrid')

        # Core logic
        self.core = DataWizardCore()
        self.current_canvas = None

        # UI skeleton
        central = QWidget(self)
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Build tabs
        self._build_input_tab()
        self._build_data_tab()
        self._build_plot_tab()

    # ------------------- Input Tab -------------------
    def _build_input_tab(self):
        tab = QWidget()
        self.tabs.addTab(tab, 'Input')
        layout = QGridLayout(tab)
        row = 0

        # File path
        layout.addWidget(QLabel('File Path:'), row, 0)
        self.file_path_edit = QLineEdit()
        layout.addWidget(self.file_path_edit, row, 1)
        browse_btn = QPushButton('Browse')
        browse_btn.clicked.connect(self.browse_file)
        layout.addWidget(browse_btn, row, 2)
        row += 1

        # Decimal / Separator / Encoding
        layout.addWidget(QLabel('Decimal:'), row, 0)
        self.decimal_edit = QLineEdit()
        self.decimal_edit.setFixedWidth(80)
        layout.addWidget(self.decimal_edit, row, 1)
        row += 1

        layout.addWidget(QLabel('Separator:'), row, 0)
        self.separator_edit = QLineEdit()
        self.separator_edit.setFixedWidth(80)
        layout.addWidget(self.separator_edit, row, 1)
        row += 1

        layout.addWidget(QLabel('Encoding:'), row, 0)
        self.encoding_edit = QLineEdit('utf-8')
        self.encoding_edit.setFixedWidth(160)
        layout.addWidget(self.encoding_edit, row, 1)
        row += 1

        # Time settings
        self.use_date_index_chk = QCheckBox('Use date as index')
        layout.addWidget(self.use_date_index_chk, row, 0, 1, 2)
        row += 1

        layout.addWidget(QLabel('Date Format:'), row, 0)
        self.date_format_edit = QLineEdit('%Y-%m-%d %H:%M:%S')
        layout.addWidget(self.date_format_edit, row, 1)
        row += 1

        layout.addWidget(QLabel('Time Column:'), row, 0)
        self.time_column_edit = QLineEdit()
        layout.addWidget(self.time_column_edit, row, 1)
        row += 1

        # Resample method (default median)
        layout.addWidget(QLabel('Resample method:'), row, 0)
        self.resample_method_combo = QComboBox()
        self.resample_method_combo.addItems(['mean', 'median', 'sum', 'ffill', 'bfill'])
        self.resample_method_combo.setCurrentText('median')
        layout.addWidget(self.resample_method_combo, row, 1)
        row += 1

        # Enable resample + interval
        self.enable_resample_chk = QCheckBox('Enable time resampling')
        self.enable_resample_chk.setChecked(False)
        layout.addWidget(self.enable_resample_chk, row, 0, 1, 2)
        row += 1

        layout.addWidget(QLabel('Resample interval (min):'), row, 0)
        self.resample_interval_combo = QComboBox()
        self.resample_interval_combo.addItems(['1', '5', '15', '30', '60'])
        self.resample_interval_combo.setCurrentText('1')
        layout.addWidget(self.resample_interval_combo, row, 1)
        row += 1

        # Auto-enable resampling when date index is used
        self.use_date_index_chk.stateChanged.connect(self._auto_enable_resample)

        # Submit
        submit_btn = QPushButton('Submit')
        submit_btn.clicked.connect(self.process_data)
        layout.addWidget(submit_btn, row, 1)

        layout.setColumnStretch(1, 1)

    def _auto_enable_resample(self):
        if self.use_date_index_chk.isChecked():
            self.enable_resample_chk.setChecked(True)

    # ------------------- Data View Tab -------------------
    def _build_data_tab(self):
        tab = QWidget()
        self.tabs.addTab(tab, 'Data View')
        layout = QVBoxLayout(tab)

        self.table_view = QTableView()
        self.table_model = PandasModel(pd.DataFrame())
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table_view)

    # ------------------- Plot Tab -------------------
    def _build_plot_tab(self):
        tab = QWidget()
        self.tabs.addTab(tab, 'Plots')
        outer = QHBoxLayout(tab)

        splitter = QSplitter()
        outer.addWidget(splitter)

        # Left control panel
        left_panel = QWidget()
        ll = QVBoxLayout(left_panel)

        # Plot type
        grp_plot = QGroupBox('Plot Type')
        v = QVBoxLayout(grp_plot)
        self.plot_type_buttons = {}
        for name in ['Line Chart', 'Bar Chart', 'Heatmap', 'Scatter Plot', 'Box Plot']:
            rb = QRadioButton(name)
            v.addWidget(rb)
            self.plot_type_buttons[name] = rb
        self.plot_type_buttons['Line Chart'].setChecked(True)
        ll.addWidget(grp_plot)

        # Axes group
        grp_axes = QGroupBox('Axes')
        gl = QGridLayout(grp_axes)
        gl.addWidget(QLabel('X-Axis:'), 0, 0)
        self.x_axis_combo = QComboBox()
        gl.addWidget(self.x_axis_combo, 0, 1)

        gl.addWidget(QLabel('Y-Axis (multiple):'), 1, 0)
        self.y_axis_list = QListWidget()
        self.y_axis_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        gl.addWidget(self.y_axis_list, 1, 1)

        self.auto_scale_chk = QCheckBox('Auto Scale')
        self.auto_scale_chk.setChecked(True)
        self.auto_scale_chk.toggled.connect(self.toggle_axis_limit_controls)
        gl.addWidget(self.auto_scale_chk, 2, 0, 1, 2)

        # Limits
        gl.addWidget(QLabel('X Limits:'), 3, 0)
        hx = QHBoxLayout()
        self.xmin_edit = QLineEdit(); self.xmin_edit.setFixedWidth(80)
        self.xmax_edit = QLineEdit(); self.xmax_edit.setFixedWidth(80)
        hx.addWidget(self.xmin_edit); hx.addWidget(self.xmax_edit)
        gl.addLayout(hx, 3, 1)

        gl.addWidget(QLabel('Y Limits:'), 4, 0)
        hy = QHBoxLayout()
        self.ymin_edit = QLineEdit(); self.ymin_edit.setFixedWidth(80)
        self.ymax_edit = QLineEdit(); self.ymax_edit.setFixedWidth(80)
        hy.addWidget(self.ymin_edit); hy.addWidget(self.ymax_edit)
        gl.addLayout(hy, 4, 1)

        ll.addWidget(grp_axes)

        # Labels
        grp_labels = QGroupBox('Labels')
        fl = QFormLayout(grp_labels)
        self.title_edit = QLineEdit()
        self.xlabel_edit = QLineEdit()
        self.ylabel_edit = QLineEdit()
        fl.addRow('Plot Title:', self.title_edit)
        fl.addRow('X Label:', self.xlabel_edit)
        fl.addRow('Y Label:', self.ylabel_edit)
        ll.addWidget(grp_labels)

        # Actions
        grp_actions = QGroupBox('Actions')
        h = QHBoxLayout(grp_actions)
        plot_btn = QPushButton('Plot')
        plot_btn.clicked.connect(self.plot_from_selection)
        export_png_btn = QPushButton('Export PNG')
        export_png_btn.clicked.connect(self.export_current_plot)
        export_csv_btn = QPushButton('Export CSV')
        export_csv_btn.clicked.connect(self.export_plot_data_as_csv)
        h.addWidget(plot_btn); h.addWidget(export_png_btn); h.addWidget(export_csv_btn)
        ll.addWidget(grp_actions)

        ll.addStretch(1)
        splitter.addWidget(left_panel)

        # Right: plot canvas holder
        self.plot_holder = QWidget()
        self.plot_holder_layout = QVBoxLayout(self.plot_holder)
        splitter.addWidget(self.plot_holder)
        splitter.setStretchFactor(1, 1)

        # Wiring toggles
        for btn in self.plot_type_buttons.values():
            btn.toggled.connect(self.toggle_axis_limit_controls)
        self.toggle_axis_limit_controls()

    # ------------------- Events & Actions -------------------
    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Open Data File', '',
            'CSV Files (*.csv);;Text Files (*.txt);;Excel Files (*.xlsx *.xls);;All Files (*)'
        )
        if path:
            self.file_path_edit.setText(path)

    def process_data(self):
        fp = self.file_path_edit.text().strip()
        if not fp:
            self.print_status('No file selected.')
            logger.warning('GUI: process_data invoked without a file path')
            return

        dec = self.decimal_edit.text().strip() or '.'
        sep = self.separator_edit.text().strip() or ','
        enc = self.encoding_edit.text().strip() or 'utf-8'
        use_idx = self.use_date_index_chk.isChecked()
        fmt = self.date_format_edit.text().strip()
        tcol = self.time_column_edit.text().strip()

        try:
            logger.info('GUI: process_data start')
            self.core.load_file(
                file_path=fp,
                decimal=dec,
                separator=sep,
                encoding=enc,
                use_date_index=use_idx,
                date_format=(fmt or None),
                time_col=(tcol or None),
            )

            if use_idx and tcol and self.enable_resample_chk.isChecked():
                method = self.resample_method_combo.currentText()
                freq_text = self.resample_interval_combo.currentText().strip()
                resample_freq = f"{freq_text}min"
                logger.info(f"GUI: resampling requested method={method} freq={resample_freq}")
                self.core.normalize_to_minutes(method=method, freq=resample_freq)

            self.print_status('Loaded')
            logger.info('GUI: data loaded successfully')
            self.refresh_table()
            self.populate_axis_selectors()
            self.toggle_axis_limit_controls()
        except Exception as e:
            logger.exception('GUI: error in process_data')
            self.print_status(f'Error: {e}')

    def refresh_table(self):
        self.table_model.setDataFrame(self.core.preview(500))

    def populate_axis_selectors(self):
        cols, num_cols, has_index = self.core.axis_options()
        self.x_axis_combo.clear(); self.y_axis_list.clear()
        if has_index:
            self.x_axis_combo.addItem('<index>')
        for c in cols:
            self.x_axis_combo.addItem(c)
        if self.x_axis_combo.count() > 0:
            self.x_axis_combo.setCurrentIndex(0)
        for c in num_cols:
            self.y_axis_list.addItem(QListWidgetItem(c))

    def toggle_axis_limit_controls(self):
        pt = self.get_selected_plot_type()
        is_heatmap = (pt == 'Heatmap')
        auto = self.auto_scale_chk.isChecked()
        # Axis selectors disabled for heatmap
        self.x_axis_combo.setEnabled(not is_heatmap)
        self.y_axis_list.setEnabled(not is_heatmap)
        # Limits disabled if auto or heatmap
        enable_limits = (not auto) and (not is_heatmap)
        for w in [self.xmin_edit, self.xmax_edit, self.ymin_edit, self.ymax_edit]:
            w.setEnabled(enable_limits)

    def get_selected_plot_type(self) -> str:
        for name, btn in self.plot_type_buttons.items():
            if btn.isChecked():
                return name
        return 'Line Chart'

    def clear_plot_holder(self):
        if self.current_canvas is not None:
            self.plot_holder_layout.removeWidget(self.current_canvas)
            self.current_canvas.setParent(None)
            self.current_canvas.deleteLater()
            self.current_canvas = None

    def plot_from_selection(self):
        try:
            pt = self.get_selected_plot_type()
            logger.info(f'GUI: plotting requested type={pt}')
            self.plot_data(pt)
        except Exception:
            logger.exception('GUI: plot_from_selection failed')
            self.print_status('Plot error. See datawizard.log for details.')

    def plot_data(self, plot_type: str):
        if self.core.df is None:
            self.print_status('Submit data first.')
            logger.warning('GUI: plot_data called without data')
            return

        self.clear_plot_holder()
        fig, ax = plt.subplots()

        try:
            x_choice = self.x_axis_combo.currentText() if self.x_axis_combo.count() else None
            y_items = self.y_axis_list.selectedItems()
            y_cols = [it.text() for it in y_items]
            logger.info(f'GUI: plot_data x={x_choice} y={y_cols} type={plot_type}')

            if plot_type != 'Heatmap':
                if not x_choice:
                    self.print_status('No X selected.')
                    logger.warning('GUI: no X selected for plotting')
                    return
                if not y_cols:
                    self.print_status('No Y selected.')
                    logger.warning('GUI: no Y selected for plotting')
                    return

            # Prepare X
            if x_choice == '<index>':
                x_data = self.core.df.index
                x_label = self.core.df.index.name or 'Index'
            else:
                x_data = self.core.df[x_choice]
                x_label = x_choice

            # Plot types
            if plot_type == 'Line Chart':
                for y in y_cols:
                    sns.lineplot(x=x_data, y=self.core.df[y], ax=ax, label=y)
            elif plot_type == 'Bar Chart':
                for y in y_cols:
                    sns.barplot(x=x_data, y=self.core.df[y], ax=ax, ci=None, label=y)
            elif plot_type == 'Scatter Plot':
                for y in y_cols:
                    sns.scatterplot(x=x_data, y=self.core.df[y], ax=ax, label=y)
            elif plot_type == 'Box Plot':
                melted = self.core.melt_for_boxplot(x_choice)
                sns.boxplot(data=melted, x='Variable', y='Value', ax=ax)
            elif plot_type == 'Heatmap':
                sns.heatmap(self.core.corr_matrix(), cmap='viridis', ax=ax, annot=True)

            # Labels
            ax.set_title(self.title_edit.text())
            ax.set_xlabel(self.xlabel_edit.text() or (x_label if plot_type != 'Heatmap' else ''))
            ax.set_ylabel(self.ylabel_edit.text())

            # Limits
            try:
                if (not self.auto_scale_chk.isChecked()) and plot_type != 'Heatmap':
                    xmin = float(self.xmin_edit.text()) if self.xmin_edit.text() else None
                    xmax = float(self.xmax_edit.text()) if self.xmax_edit.text() else None
                    ymin = float(self.ymin_edit.text()) if self.ymin_edit.text() else None
                    ymax = float(self.ymax_edit.text()) if self.ymax_edit.text() else None
                    if xmin is not None or xmax is not None:
                        ax.set_xlim(xmin, xmax)
                    if ymin is not None or ymax is not None:
                        ax.set_ylim(ymin, ymax)
            except Exception:
                logger.warning('GUI: invalid axis limits entered')
                self.print_status('Warning: invalid axis limits.')

            canvas = FigureCanvas(fig)
            self.current_canvas = canvas
            self.plot_holder_layout.addWidget(canvas)
            canvas.draw()
            logger.info('GUI: plot drawn successfully')

        except Exception:
            logger.exception('GUI: plotting error')
            self.print_status('Plotting error. See datawizard.log')

    def export_current_plot(self):
        if self.current_canvas is None:
            logger.warning('GUI: PNG export requested without active canvas')
            self.print_status('No plot.')
            return
        title = self.title_edit.text().strip()
        today = str(date.today())
        defname = f'{today}-{title or "plot"}.png'
        path, _ = QFileDialog.getSaveFileName(self, 'Save PNG', defname, 'PNG files (*.png)')
        if not path:
            return
        try:
            self.current_canvas.figure.savefig(path, dpi=300, format='png')
            self.print_status(f'Saved: {os.path.basename(path)}')
            logger.info(f'GUI: PNG saved to {path}')
        except Exception:
            logger.exception('GUI: error saving PNG')
            self.print_status('Save error. See datawizard.log')

    def export_plot_data_as_csv(self):
        if self.core.df is None:
            logger.warning('GUI: CSV export requested without data')
            self.print_status('No data.')
            return
        pt = self.get_selected_plot_type()
        x_choice = self.x_axis_combo.currentText() if self.x_axis_combo.count() else None
        y_cols = [it.text() for it in self.y_axis_list.selectedItems()]
        x_label = self.xlabel_edit.text().strip()
        logger.info(f"GUI: CSV export requested type={pt} x={x_choice} y={y_cols} xlabel='{x_label}'")
        try:
            data = self.core.build_export_dataframe(pt, x_choice, y_cols, x_label)
            if data.empty:
                logger.warning('GUI: CSV export skipped (empty dataset)')
                self.print_status('Nothing to export.')
                return
            path, _ = QFileDialog.getSaveFileName(self, 'Export CSV', 'visible_plot_data.csv', 'CSV files (*.csv)')
            if not path:
                return
            data.to_csv(path, index=False, sep=self.core.last_used_separator, encoding=self.core.last_used_encoding)
            self.print_status(f'CSV exported: {os.path.basename(path)}')
            logger.info(f'GUI: CSV exported to {path}')
        except Exception:
            logger.exception('GUI: error exporting CSV')
            self.print_status('Export error. See datawizard.log')

    def print_status(self, msg: str):
        self.status.showMessage(msg)


# --------- Entry point for direct runs (optional) ---------
def run_app():
    """Start the Qt application (used by main.py and PyInstaller entry)."""
    app = QApplication(sys.argv)
    win = DataWizardGUI()
    win.show()
    sys.exit(app.exec())
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = DataWizardGUI()
    win.show()
    sys.exit(app.exec())
