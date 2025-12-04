"""
world_bank_bi_pipeline.py

A business-intelligence pipeline that:
 - fetches multiple World Bank indicators for chosen countries and years
 - consolidates into a tidy DataFrame
 - computes CAGR, rolling averages, and cross-indicator correlations
 - saves CSV/Excel reports and PNG charts

Dependencies:
 - Python 3.9+
 - pip install pandas requests openpyxl matplotlib sqlalchemy xlsxwriter tqdm

Author: Luiza Barseghyan
"""