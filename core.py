# core.py - DataWizard functional logic with logging
from __future__ import annotations
import os
import pandas as pd
import numpy as np
import logging
from logging.handlers import RotatingFileHandler
from typing import List, Optional, Tuple

# Logging setup
logger = logging.getLogger("datawizard")
logger.setLevel(logging.INFO)
# Put logs in ../.log/ (relative to exe/app)
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".log")
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, "datawizard.log")
handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=3)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

class DataWizardCore:
    def __init__(self) -> None:
        self.df: Optional[pd.DataFrame] = None
        self.last_used_separator = ','
        self.last_used_encoding = 'utf-8'

    def load_file(self, file_path, decimal='.', separator=',', encoding='utf-8',
                  use_date_index=False, date_format=None, time_col=None):
        logger.info(f"Loading file: {file_path} sep={separator} enc={encoding}")
        self.last_used_separator = separator or ','
        self.last_used_encoding = encoding or 'utf-8'
        ext = os.path.splitext(file_path)[1].lower()
        parse_dates = [time_col] if (use_date_index and time_col) else None
        try:
            if ext in ['.csv','.txt']:
                try:
                    self.df = pd.read_csv(file_path, sep=separator, decimal=decimal,
                                          encoding=encoding, parse_dates=parse_dates,
                                          date_format=(date_format if parse_dates else None))
                except UnicodeDecodeError:
                    self.df = pd.read_csv(file_path, sep=separator, decimal=decimal,
                                          encoding='latin1', parse_dates=parse_dates,
                                          date_format=(date_format if parse_dates else None))
            elif ext in ['.xlsx','.xls']:
                self.df = pd.read_excel(file_path)
            else:
                raise ValueError('Unsupported file type')
            if use_date_index and time_col in self.df.columns:
                logger.info(f"Setting date index column: {time_col}")
                self.df.set_index(time_col, inplace=True)
            return self.df
        except Exception:
            logger.exception("Error while loading file")
            raise

    def normalize_to_minutes(self, method='median', freq='1min'):
        logger.info(f"Resampling: method={method} freq={freq}")
        try:
            if self.df is None:
                raise ValueError('No DataFrame loaded')
            if not isinstance(self.df.index, pd.DatetimeIndex):
                self.df.index = pd.to_datetime(self.df.index, errors='coerce')
            self.df = self.df[~self.df.index.isna()]
            self.df.sort_index(inplace=True)
            start = self.df.index.min().floor(freq)
            end = self.df.index.max().ceil(freq)
            full_index = pd.date_range(start=start, end=end, freq=freq)
            by_freq = self.df.groupby(pd.Grouper(freq=freq))
            num_cols = self.df.select_dtypes(include=np.number).columns
            non_cols = [c for c in self.df.columns if c not in num_cols]
            if method == 'median':
                df_num = by_freq[num_cols].median()
            elif method == 'mean':
                df_num = by_freq[num_cols].mean()
            elif method == 'sum':
                df_num = by_freq[num_cols].sum()
            elif method in ['ffill','bfill']:
                df_min = by_freq.last().reindex(full_index)
                self.df = df_min.ffill() if method=='ffill' else df_min.bfill()
                return self.df
            else:
                raise ValueError('Unknown method')
            df_non = by_freq[non_cols].last() if non_cols else pd.DataFrame(index=df_num.index)
            out = pd.concat([df_num, df_non], axis=1).reindex(full_index)
            if non_cols:
                out[non_cols] = out[non_cols].ffill()
            self.df = out
            logger.info(f"Resample complete: rows={len(self.df)}")
            return self.df
        except Exception:
            logger.exception("Error during resampling")
            raise

    def preview(self, limit=500):
        return self.df.head(limit) if self.df is not None else pd.DataFrame()

    def axis_options(self):
        if self.df is None:
            return [], [], False
        cols = list(self.df.columns)
        nums = list(self.df.select_dtypes(include=np.number).columns)
        has_idx = isinstance(self.df.index, pd.DatetimeIndex) or (self.df.index.name is not None)
        return cols, nums, has_idx

    def corr_matrix(self):
        return self.df.corr(numeric_only=True) if self.df is not None else pd.DataFrame()

    def melt_for_boxplot(self, x_choice):
        if self.df is None:
            return pd.DataFrame()
        if x_choice and x_choice != '<index>':
            return self.df.reset_index().melt(id_vars=[x_choice], var_name='Variable', value_name='Value')
        return self.df.reset_index().melt(var_name='Variable', value_name='Value')

    def build_export_dataframe(self, plot_type, x_choice, y_cols, x_label):
        logger.info(f"Exporting plot data: plot={plot_type} X={x_choice} Y={y_cols}")
        if self.df is None:
            return pd.DataFrame()
        if plot_type == 'Heatmap':
            return self.corr_matrix()
        if plot_type == 'Box Plot':
            return self.melt_for_boxplot(x_choice)
        if not y_cols:
            return pd.DataFrame()
        x_label = x_label.strip() if x_label else ''
        if x_choice == '<index>':
            x_series = self.df.index.to_series()
            x_col = x_label or (self.df.index.name or 'Index')
        else:
            x_series = self.df[x_choice]
            x_col = x_label or x_choice
        out = pd.DataFrame({x_col: x_series})
        for c in y_cols:
            out[c] = self.df[c]
        return out
