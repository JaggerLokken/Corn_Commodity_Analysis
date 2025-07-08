import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for Flask
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
import requests
from pathlib import Path
from sklearn.linear_model import LinearRegression

Path("static").mkdir(exist_ok=True)

def run_analysis():
    # Fetch Corn Data from USDA
    API_KEY = "E64DC9DA-5617-380B-9AF5-11373F58C513"
    BASE_URL = "https://quickstats.nass.usda.gov/api/api_GET/"

    params = {
        "key": API_KEY,
        "sector_desc": "CROPS",
        "commodity_desc": "CORN",
        "statisticcat_desc": "PRICE RECEIVED",
        "unit_desc": "$ / BU",
        "agg_level_desc": "NATIONAL",
        "freq_desc": "MONTHLY",
        "year__GE": 2017,
        "format": "JSON"
    }

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()["data"]

    df = pd.json_normalize(data)[["year", "reference_period_desc", "Value"]]
    df.columns = ["Year", "Month", "Corn_Price"]
    df["Corn_Price"] = pd.to_numeric(df["Corn_Price"], errors="coerce")
    df["Date"] = pd.to_datetime(df["Month"] + " " + df["Year"].astype(str), format="%b %Y")
    df = df[["Date", "Corn_Price"]].dropna().sort_values("Date").set_index("Date")

    # Calculate Corn Returns and Fetch DBC
    corn_returns = df["Corn_Price"].pct_change().dropna()
    start_date = df.index.min().strftime('%Y-%m-%d')
    end_date = df.index.max().strftime('%Y-%m-%d')

    dbc = yf.download("DBC", start=start_date, end=end_date, interval="1mo", auto_adjust=True)[["Close"]]
    dbc.rename(columns={"Close": "DBC_Price"}, inplace=True)
    dbc["DBC_Returns"] = dbc["DBC_Price"].pct_change()
    dbc.dropna(inplace=True)

    # Combine & Metrics
    combined = pd.concat([corn_returns, dbc["DBC_Returns"]], axis=1).dropna()
    combined.columns = ["Corn_Returns", "DBC_Returns"]

    return df, combined

# CAPM Summary Statistics
def generate_summary():
    _, combined = run_analysis()
    corn_annual_return = combined["Corn_Returns"].mean() * 12
    corn_annual_std = combined["Corn_Returns"].std() * (12 ** 0.5)
    cov_matrix = combined.cov()
    corn_beta = cov_matrix.loc["Corn_Returns", "DBC_Returns"] / cov_matrix.loc["DBC_Returns", "DBC_Returns"]
    rf = 0.03
    market_return = combined["DBC_Returns"].mean() * 12
    expected_return_capm_corn = rf + corn_beta * (market_return - rf)

    result_text = (
        f"β: Corn Beta vs DBC: {corn_beta:.4f}\n"
        f"E(R): CAPM Expected Return: {expected_return_capm_corn*100:.2f}%\n"
        f"R: Actual Annual Return: {corn_annual_return*100:.2f}%\n"
        f"σ: Annual Volatility (Std Dev): {corn_annual_std*100:.2f}%"
    )

    with open("static/metrics_output.txt", "w", encoding="utf-8") as f:
        f.write(result_text)

    return result_text

def plot_returns():
    _, combined = run_analysis()
    plt.figure(figsize=(10, 6))
    combined.plot()
    plt.title("Corn vs. DBC Monthly Returns")
    plt.xlabel("Date")
    plt.ylabel("Monthly Return")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("static/returns_plot.png")
    plt.close()
    return "static/returns_plot.png"

# Regression Plot
def plot_regression():
    _, combined = run_analysis()

    X = combined["DBC_Returns"].values.reshape(-1, 1)
    y = combined["Corn_Returns"].values

    reg = LinearRegression().fit(X, y)
    reg_line = reg.predict(X)

    plt.figure(figsize=(10, 6))
    plt.scatter(X, y, alpha=0.6)
    plt.plot(X, reg_line, color='red', linewidth=2)
    plt.title("CAPM Regression: Corn vs DBC")
    plt.xlabel("DBC Returns (Market)")
    plt.ylabel("Corn Returns (Asset)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("static/regression_plot.png")
    plt.close()

    # CAPM regression stats
    X = combined["DBC_Returns"]
    y = combined["Corn_Returns"]
    X_with_const = sm.add_constant(X)
    model = sm.OLS(y, X_with_const).fit()

    with open("static/capm_summary.txt", "w", encoding="utf-8") as f:
        f.write(str(model.summary()))

    return "static/regression_plot.png"

#Security Market Line Plot
def plot_sml():
    _, combined = run_analysis()
    corn_annual_return = combined["Corn_Returns"].mean() * 12
    cov_matrix = combined.cov()
    corn_beta = cov_matrix.loc["Corn_Returns", "DBC_Returns"] / cov_matrix.loc["DBC_Returns", "DBC_Returns"]
    rf = 0.03
    market_return = combined["DBC_Returns"].mean() * 12
    expected_return_capm_corn = rf + corn_beta * (market_return - rf)

    betas = [0, 0.5, 1, 1.5, 2]
    sml_returns = [rf + b * (market_return - rf) for b in betas]

    plt.figure(figsize=(10, 6))
    plt.plot(betas, sml_returns, label="Security Market Line", color="black")
    plt.scatter(corn_beta, corn_annual_return, color="green", label="Actual Corn Return", s=100)
    plt.scatter(corn_beta, expected_return_capm_corn, color="red", label="CAPM Expected Return", marker="x", s=100)
    plt.text(corn_beta, corn_annual_return + 0.005, "Actual", ha="center", color="green")
    plt.text(corn_beta, expected_return_capm_corn - 0.01, "CAPM", ha="center", color="red")
    plt.xlabel("Beta (Risk)")
    plt.ylabel("Annual Return")
    plt.title("Security Market Line (SML) with Corn")
    plt.legend()
    plt.grid(True)
    plt.savefig("static/sml_graph.png")
    plt.close()
    return "static/sml_graph.png"