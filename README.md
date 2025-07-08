# Corn Commodity Analysis Dashboard

An interactive Flask web app that models CAPM behavior in corn futures using historical data, commodity benchmarks, and government-reported supply metrics. 
The app combines Yahoo Finance data and USDA economic releases to calculate and visualize risk-adjusted performance.


# Features

- **CAPM Summary**: Real-time beta, expected return, actual return, and volatility for corn vs. DBC
- **SML Plot**: Security Market Line with visualized expected vs. actual return
- **Regression Analysis**: Linear CAPM regression chart with alpha and R²
- **Return Tracking**: Monthly return comparison of corn vs. DBC


# Tools Used

- **Backend**: Flask, Python
- **Finance Data**: `yfinance` for corn and commodity index pricing
- **Government Data**: USDA API (using custom `requests`-based scraper)
- **Stats & Modeling**: numpy, scipy, pandas
- **Charts**: matplotlib
- **Frontend**: HTML, JavaScript


# Project Structure
CORN_DASHBOARD/
├── app.py # Flask backend
├── corn_model.py # CAPM + USDA model logic
├── templates/
│ └── index.html
├── static/
│ ├── script.js
│ ├── *.png # Plots: SML, regression, returns
│ └── *.txt # CAPM summary output
└── README.md

# Run It Locally
git clone https://github.com/JaggerLokken/Corn_Commodity_Analysis.git
cd Corn_Commodity_Analysis
pip install -r requirements.txt
python app.py

Open http://127.0.0.1:5000

# Sample Output
![image](https://github.com/user-attachments/assets/f54ec674-237a-4f35-ab90-fdde2c6c02f9)




