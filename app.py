import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import streamlit as st
from fpdf import FPDF

# Function to fetch and process data
def fetch_and_process_data():
    # Read the stock parameters data
    all_stock_parameters_df = pd.read_excel('all_stock_parameters.xlsx')

    # Define weights for each parameter
    weights = {
        'Volatility': 0.1,
        'Beta': 0.0,
        'CAGR': 0.1,
        'Debt_to_Equity_Ratio': -0.1,  # Deduct if Debt_to_Equity_Ratio is too high
        'EPS': 0.0,
        'Dividend_Yield': 0.1,
        'RSI': 0.0,
        'MACD': 0.0,
        'Percentage_Difference': 0.8,
        'Correlation_with_event': 0.0
    }

    # Ensure all weights are numeric
    for param in weights:
        if not isinstance(weights[param], (int, float)):
            print(f"Error: Weight for '{param}' is not numeric. Please provide a numeric weight.")
            exit()

    # Apply weights to parameters and calculate total score
    all_stock_parameters_df['Total_Score'] = 0
    for param, weight in weights.items():
        if param == 'Debt_to_Equity_Ratio':
            # Deduct if Debt_to_Equity_Ratio is too high
            all_stock_parameters_df['Total_Score'] -= all_stock_parameters_df[param] * weight
        elif param == 'RSI':
            # Adjust score based on RSI
            all_stock_parameters_df['Total_Score'] += all_stock_parameters_df[param].apply(lambda x: 1 if x < 30 else (-1 if x > 70 else 0)) * weight
        else:
            all_stock_parameters_df[param] = pd.to_numeric(all_stock_parameters_df[param], errors='coerce')  # Convert to numeric and handle errors
            all_stock_parameters_df['Total_Score'] += all_stock_parameters_df[param] * weight

    # Sort stocks by Total_Score in descending order
    all_stock_parameters_df_sorted = all_stock_parameters_df.sort_values(by='Total_Score', ascending=False)

    # Pick top 100 stocks based on Total_Score
    top_100_best_stocks = all_stock_parameters_df_sorted.head(100)
    
    return top_100_best_stocks, all_stock_parameters_df_sorted


# Function to generate the PDF report
def generate_pdf_report(main_topic, industry_topic, top_100_best_stocks, metrics_df):
    pdf = FPDF()

    # Add a page
    pdf.add_page()

    # Set font
    pdf.set_font("Arial", size=12)

    # Add Header
    pdf.image('PredictRAMLOGO.png', x=10, y=8, w=33)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Economic Event Analysis Report", ln=True, align="C")
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Main Event: {main_topic}", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Industry Event: {industry_topic}", ln=True, align="C")
    pdf.cell(200, 10, txt="Prepared By SEBI Registered Research Analyst: Harika Enjamuri", ln=True, align="C")

    # Executive Summary
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Executive Summary", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=f"This financial analysis report explores the relationship between {main_topic} and the performance of the top 100 stocks. By examining historical data and correlating it with stock performance, this report aims to identify patterns and trends for informed investment decisions.\n\n"
                              f"The analysis considers several factors including volatility, beta, CAGR, debt to equity ratio, EPS, dividend yield, RSI, MACD, percentage difference, and correlation with the event. "
                              f"The comprehensive evaluation helps in understanding how {main_topic} impacts various financial metrics and stock performance.\n\n"
                              f"Moreover, the report includes graphical representations and detailed findings to provide a clearer picture of the effects of {main_topic} on the stock market. "
                              f"The goal is to equip investors with the knowledge needed to make sound investment decisions in light of {main_topic}.")

    # Key Findings
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Key Findings", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=f"- Stocks with varying degrees of correlation with {main_topic}, indicating different levels of impact.\n"
                              f"- Stocks with higher volatility and beta may experience greater sensitivity to changes related to {main_topic}.\n"
                              f"- Companies with higher debt to equity ratios may face increased financial risks, impacting their stock prices and investor confidence.\n")

    # Investment Implications
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Investment Implications", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=f"- Diversification: Investors should diversify their portfolios across various sectors and asset classes.\n"
                              f"- Hedging Strategies: Using hedging instruments can help mitigate risks.\n"
                              f"- Long-Term Perspective: A long-term investment approach will help investors navigate volatility and capitalize on growth opportunities.\n")

    # Add the top 20 stocks metrics
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Top 20 Stocks Metrics", ln=True)

    # Add the metrics table
    pdf.set_font("Arial", size=10)
    pdf.ln(5)
    for index, row in metrics_df.iterrows():
        pdf.multi_cell(0, 10, txt=f"{row['Stock Symbol']} | {row['Total Value']} | {row['Correlation with ^NSEI']} | {row['Annualized Alpha (%)']}% | "
                                  f"{row['Annualized Volatility (%)']}% | {row['Sharpe Ratio']} | {row['Treynor Ratio']} | {row['Sortino Ratio']} | {row['Maximum Drawdown']}% | "
                                  f"{row['R-Squared']} | {row['Downside Deviation']} | {row['Annualized Tracking Error (%)']}%")
        pdf.ln(2)

    # Output the report as PDF
    pdf.output("report.pdf")


# Streamlit App
st.title('Stock Analysis Report Generator')

# User input for event topics
main_topic = st.text_input("Enter the main event topic for the report:")
industry_topic = st.text_input("Enter the industry-specific event topic:")

# Button to generate the report
if st.button("Generate Report"):
    if main_topic and industry_topic:
        # Fetch and process the stock data
        top_100_best_stocks, all_stock_parameters_df_sorted = fetch_and_process_data()

        # Metrics Calculation for the Top 20 stocks
        tickers = top_100_best_stocks['Stock Symbol'].head(20).tolist()

        # Fetch historical data
        end_date = datetime.now()
        start_date = end_date.replace(year=end_date.year - 1)
        stock_data = yf.download(tickers + ['^NSEI'], start=start_date, end=end_date)['Adj Close']
        returns = stock_data.pct_change().dropna()

        # Metrics calculations
        nsei_returns = returns['^NSEI']
        metrics = []
        for ticker in tickers:
            stock_returns = returns[ticker]
            total_value = stock_data[ticker].iloc[-1]
            correlation_with_nsei = stock_returns.corr(nsei_returns)
            excess_returns = stock_returns - nsei_returns.mean()
            annualized_alpha = (excess_returns.mean() * 252)
            annualized_volatility = (stock_returns.std() * np.sqrt(252))
            sharpe_ratio = excess_returns.mean() / stock_returns.std() * np.sqrt(252)
            tracking_error = np.std(stock_returns - nsei_returns) * np.sqrt(252)
            downside_deviation = np.sqrt(np.mean(np.minimum(0, stock_returns - 0) ** 2)) * np.sqrt(252)
            sortino_ratio = excess_returns.mean() / downside_deviation
            treynor_ratio = excess_returns.mean() / stock_returns.cov(nsei_returns)
            maximum_drawdown = (stock_data[ticker].max() - stock_data[ticker].min()) / stock_data[ticker].max()
            r_squared = correlation_with_nsei ** 2

            metrics.append({
                'Stock Symbol': ticker,
                'Total Value': total_value,
                'Correlation with ^NSEI': correlation_with_nsei,
                'Annualized Alpha (%)': annualized_alpha * 100,
                'Annualized Volatility (%)': annualized_volatility * 100,
                'Sharpe Ratio': sharpe_ratio,
                'Treynor Ratio': treynor_ratio,
                'Sortino Ratio': sortino_ratio,
                'Maximum Drawdown': maximum_drawdown,
                'R-Squared': r_squared,
                'Downside Deviation': downside_deviation,
                'Annualized Tracking Error (%)': tracking_error * 100
            })

        metrics_df = pd.DataFrame(metrics)

        # Generate the PDF report
        generate_pdf_report(main_topic, industry_topic, top_100_best_stocks, metrics_df)
        st.success("Report has been generated successfully! Check the output file 'report.pdf'.")
    else:
        st.error("Please fill in both event topics.")
