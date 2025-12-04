import requests
import pandas as pd
import numpy as np
import time
from requests.adapters import HTTPAdapter, Retry
from io import BytesIO
import matplotlib.pyplot as plt
from pathlib import Path
from tqdm import tqdm

# ---------- Config ----------
BASE_URL = "https://api.worldbank.org/v2"
INDICATORS = {
    "GDP_per_capita": "NY.GDP.PCAP.CD",
    "Unemployment_%": "SL.UEM.TOTL.ZS",
    "Internet_users_%": "IT.NET.USER.ZS",
}
# Example country codes (ISO2 or ISO3 accepted by endpoints; we'll use ISO2)
COUNTRIES = ["US", "CN", "IN", "BR", "DE", "ZA"]  # USA, China, India, Brazil, Germany, South Africa
START_YEAR = 2000
END_YEAR = 2024  # inclusive
OUTPUT_DIR = Path("wb_bi_output")
OUTPUT_DIR.mkdir(exist_ok=True)
PER_PAGE = 20000  # large so we get all rows in one page when possible

# Retry-enabled requests session
session = requests.Session()
retries = Retry(total=5, backoff_factor=0.5, status_forcelist=(500,502,503,504))
session.mount("https://", HTTPAdapter(max_retries=retries))

# ---------- Helpers ----------
def fetch_indicator(indicator_code, countries, start_year, end_year, per_page=PER_PAGE):
    """
    Fetch indicator data from World Bank API for given countries and year range.
    Returns a DataFrame with columns: countryiso2code, country, date, value, indicator
    """
    country_str = ";".join([c.lower() for c in countries])
    url = f"{BASE_URL}/country/{country_str}/indicator/{indicator_code}"
    params = {
        "date": f"{start_year}:{end_year}",
        "format": "json",
        "per_page": per_page,
    }

    # First request to get pagination info
    r = session.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, list) or len(data) < 2:
        raise RuntimeError("Unexpected API response structure for indicator fetch.")

    paging = data[0]
    total_pages = int(paging.get("pages", 1))

    records = []
    # page 1 content is data[1]
    for rec in data[1]:
        records.append(rec)

    # If more pages, iterate
    for page in range(2, total_pages + 1):
        params["page"] = page
        r = session.get(url, params=params, timeout=30)
        r.raise_for_status()
        page_data = r.json()
        if len(page_data) >= 2:
            records.extend(page_data[1])
        time.sleep(0.05)

    # Normalize records into DataFrame
    df = pd.json_normalize(records)
    if df.empty:
        return pd.DataFrame(columns=["countryiso2code", "country.value", "date", "value", "indicator.id"])
    df = df[["countryiso2code", "country.value", "date", "value", "indicator.id"]]
    df = df.rename(columns={
        "countryiso2code": "country_code",
        "country.value": "country",
        "indicator.id": "indicator_code"
    })
    # convert numeric
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["date"] = df["date"].astype(int)
    return df

def pivot_indicators(dfs):
    """
    dfs: dict indicator_name -> DataFrame (as returned from fetch_indicator)
    Return: wide DataFrame indexed by (country, year) with columns per indicator
    """
    pieces = []
    for name, df in dfs.items():
        if df.empty:
            continue
        tmp = df[["country", "country_code", "date", "value"]].copy()
        tmp = tmp.rename(columns={"value": name, "date": "year"})
        pieces.append(tmp)
    if not pieces:
        return pd.DataFrame()
    merged = pieces[0]
    for other in pieces[1:]:
        merged = pd.merge(merged, other, on=["country", "country_code", "year"], how="outer")
    merged = merged.sort_values(["country", "year"]).reset_index(drop=True)
    return merged

def compute_cagr(series, start_year, end_year):
    """
    Compute CAGR for a pandas Series indexed by year. Returns CAGR as float (decimal)
    Requires at least 2 non-null points.
    """
    s = series.dropna().sort_index()
    if s.shape[0] < 2:
        return np.nan
    # use first and last available within range
    first_year = s.index.min()
    last_year = s.index.max()
    first_val = s.loc[first_year]
    last_val = s.loc[last_year]
    n = last_year - first_year
    if first_val <= 0 or pd.isna(first_val) or pd.isna(last_val):
        return np.nan
    return (last_val / first_val) ** (1.0 / n) - 1.0

# ---------- Pipeline ----------
def run_pipeline():
    # 1) Fetch data for each indicator
    indicator_dfs = {}
    print("Fetching indicators from World Bank...")
    for name, code in INDICATORS.items():
        print(f"  - {name} ({code}) ...", end="", flush=True)
        df = fetch_indicator(code, COUNTRIES, START_YEAR, END_YEAR)
        indicator_dfs[name] = df
        print(f" {len(df):,} rows")

    # 2) Pivot to wide table
    wide = pivot_indicators(indicator_dfs)
    if wide.empty:
        print("No data fetched. Exiting.")
        return

    # 3) Ensure year is integer
    wide["year"] = wide["year"].astype(int)
    # 4) Save raw fetched data
    raw_out = OUTPUT_DIR / "raw_wide_data.csv"
    wide.to_csv(raw_out, index=False)
    print(f"Saved raw wide CSV -> {raw_out}")

    # 5) Compute per-country metrics: CAGR for GDP per capita (over whole period), latest values, rolling averages
    metrics = []
    grouped = wide.groupby("country")
    for country, grp in grouped:
        grp = grp.set_index("year").sort_index()
        # CAGR for GDP per capita
        gdp_series = grp["GDP_per_capita"]
        cagr = compute_cagr(gdp_series, START_YEAR, END_YEAR)
        latest_year = grp.index.max()
        latest_row = grp.loc[latest_year]
        metrics.append({
            "country": country,
            "years_observed": grp.shape[0],
            "gdp_per_capita_cagr": cagr,
            "gdp_per_capita_latest": latest_row.get("GDP_per_capita", np.nan),
            "unemployment_latest": latest_row.get("Unemployment_%", np.nan),
            "internet_users_pct_latest": latest_row.get("Internet_users_%", np.nan),
        })
        # compute rolling 3-year average for GDP and add as column
        grp["gdp_3yr_roll"] = grp["GDP_per_capita"].rolling(window=3, min_periods=1).mean()
        # persist rolling back into wide (merge on country/year)
        wide.loc[wide["country"] == country, "gdp_3yr_roll"] = grp["gdp_3yr_roll"].values

    metrics_df = pd.DataFrame(metrics)
    metrics_out = OUTPUT_DIR / "country_summary_metrics.csv"
    metrics_df.to_csv(metrics_out, index=False)
    print(f"Saved country summary metrics -> {metrics_out}")

    # 6) Compute correlations across indicators per country (Pearson) and overall
    # Per-country correlations
    corr_records = []
    for country, grp in wide.groupby("country"):
        g = grp[["GDP_per_capita", "Unemployment_%", "Internet_users_%"]].dropna()
        if g.shape[0] < 3:
            continue
        corr = g.corr()
        corr_records.append({
            "country": country,
            "gdp_unemployment_corr": corr.loc["GDP_per_capita", "Unemployment_%"],
            "gdp_internet_corr": corr.loc["GDP_per_capita", "Internet_users_%"],
            "unemployment_internet_corr": corr.loc["Unemployment_%", "Internet_users_%"],
        })
    corr_df = pd.DataFrame(corr_records)
    corr_out = OUTPUT_DIR / "country_indicator_correlations.csv"
    corr_df.to_csv(corr_out, index=False)
    print(f"Saved country indicator correlations -> {corr_out}")

    # Overall correlation across all countries & years
    overall_corr = wide[["GDP_per_capita", "Unemployment_%", "Internet_users_%"]].corr()

    # 7) Visualizations (one chart per indicator by country)
    print("Generating charts...")
    plt.ioff()
    years = sorted(wide["year"].unique())
    # line charts for each indicator
    for indicator in ["GDP_per_capita", "Unemployment_%", "Internet_users_%"]:
        fig, ax = plt.subplots(figsize=(10,6))
        for country in wide["country"].unique():
            dfc = wide[wide["country"] == country].dropna(subset=[indicator])
            if dfc.empty:
                continue
            ax.plot(dfc["year"], dfc[indicator], label=country)
        ax.set_title(f"{indicator} by country ({START_YEAR}-{END_YEAR})")
        ax.set_xlabel("Year")
        ax.set_ylabel(indicator)
        ax.legend(ncol=2, fontsize="small")
        ax.grid(True)
        out_png = OUTPUT_DIR / f"{indicator}_by_country.png"
        fig.tight_layout()
        fig.savefig(out_png)
        plt.close(fig)
        print(f"  - saved {out_png}")

    # 8) Export an Excel report with three sheets: raw, metrics, correlations; and embed PNGs if desired
    excel_path = OUTPUT_DIR / "wb_bi_report.xlsx"
    with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
        wide.to_excel(writer, sheet_name="raw_wide", index=False)
        metrics_df.to_excel(writer, sheet_name="summary_metrics", index=False)
        corr_df.to_excel(writer, sheet_name="country_correlations", index=False)
        # write overall corr table into separate sheet
        overall_corr.to_excel(writer, sheet_name="overall_correlation")
        workbook = writer.book
        # insert the first PNG into a dashboard sheet (optional)
        dashboard = workbook.add_worksheet("dashboard")
        # insert images (top-left positions)
        try:
            dashboard.insert_image(1, 1, str((OUTPUT_DIR / "GDP_per_capita_by_country.png")), {"x_scale": 0.9, "y_scale": 0.9})
        except Exception:
            pass

    print(f"Excel report written -> {excel_path}")

    # 9) Print a small console summary
    print("\nTop-level summary:")
    print(metrics_df[["country", "gdp_per_capita_cagr", "gdp_per_capita_latest"]].sort_values("gdp_per_capita_latest", ascending=False).to_string(index=False))
    print("\nOverall indicator correlation (Pearson):")
    print(overall_corr.to_string())

if __name__ == "__main__":
    run_pipeline()