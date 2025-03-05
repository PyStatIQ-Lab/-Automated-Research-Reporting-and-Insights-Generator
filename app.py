import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Create a function to generate a PDF report
def generate_pdf(main_topic, industry_topic, report_data):
    # Set up PDF file path
    pdf_filename = "Financial_Analysis_Report.pdf"
    
    # Create a new PDF object
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    c.setFont("Helvetica", 12)
    
    # Add title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(200, 750, f"Economic Event Analysis Report: {main_topic}")
    c.setFont("Helvetica", 12)
    c.drawString(200, 730, f"Prepared by: Harika Enjamuri")
    c.drawString(200, 710, "SEBI Registered Research Analyst, INH000017417")
    
    # Add Executive Summary
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, 680, "Executive Summary:")
    c.setFont("Helvetica", 12)
    summary = f"This financial analysis report explores the relationship between {main_topic} and the performance of the top 100 stocks. By examining historical data and correlating it with stock performance, this report aims to identify patterns and trends for informed investment decisions."
    c.drawString(30, 660, summary)
    
    # Key Findings
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, 630, "Key Findings:")
    c.setFont("Helvetica", 12)
    key_findings = [
        "Analysis: The top 100 stocks exhibit varying degrees of correlation with the event.",
        "Volatility and Beta: Stocks with higher volatility may experience greater sensitivity.",
        "Return on Investment (ROI): Some stocks demonstrate strong ROI despite the pressures.",
        "Debt to Equity Ratio: Companies with higher debt to equity ratios may face increased financial risks."
    ]
    
    y_position = 610
    for finding in key_findings:
        c.drawString(30, y_position, f"- {finding}")
        y_position -= 20
    
    # Industry-Specific Insights
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, y_position, "Industry-Specific Insights:")
    c.setFont("Helvetica", 12)
    industry_insights = [
        "Positive Impact: Industries such as technology and renewable energy may benefit.",
        "Neutral Impact: Healthcare sector may experience both challenges and opportunities.",
        "Negative Impact: Traditional retail may face challenges due to shifts in consumer behavior."
    ]
    
    y_position -= 20
    for insight in industry_insights:
        c.drawString(30, y_position, f"- {insight}")
        y_position -= 20
    
    # Add table for top stocks or metrics (Example of adding a simple table)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, y_position, "Top 20 Stocks Metrics:")
    y_position -= 20
    
    # Displaying data from the report in the PDF
    for index, row in report_data.iterrows():
        c.setFont("Helvetica", 10)
        text = f"{row['Stock Symbol']} | {row['Total Value']}"
        c.drawString(30, y_position, text)
        y_position -= 20
    
    # Save the PDF
    c.save()

# Function to fetch data and calculate stock metrics
def fetch_and_calculate_data(main_topic):
    # Example code to fetch stock data using yfinance and perform calculations
    tickers = ["AAPL", "MSFT", "GOOGL"]  # Example stock symbols
    
    # Fetch data for the past year
    end_date = datetime.now()
    start_date = end_date.replace(year=end_date.year - 1)
    stock_data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
    
    # Calculate returns and metrics (Example: Total Value and correlation)
    returns = stock_data.pct_change().dropna()
    metrics = []
    for ticker in tickers:
        stock_returns = returns[ticker]
        total_value = stock_data[ticker].iloc[-1]
        metrics.append({
            'Stock Symbol': ticker,
            'Total Value': total_value
        })
    
    metrics_df = pd.DataFrame(metrics)
    return metrics_df

# Streamlit app setup
st.title("Financial Analysis Report Generator")

# Input fields for user to enter event and industry-specific topic
main_topic = st.text_input("Enter the main event for the report:")
industry_topic = st.text_input("Enter the industry-specific event topic:")

# Button to generate PDF report
if st.button("Generate PDF Report"):
    if main_topic and industry_topic:
        st.write("Generating the report...")
        
        # Fetch data and calculate metrics
        report_data = fetch_and_calculate_data(main_topic)
        
        # Generate PDF report
        generate_pdf(main_topic, industry_topic, report_data)
        
        st.write("Report generated successfully!")
        st.download_button(
            label="Download PDF Report",
            data=open("Financial_Analysis_Report.pdf", "rb").read(),
            file_name="Financial_Analysis_Report.pdf",
            mime="application/pdf"
        )
    else:
        st.write("Please enter both the main event and industry-specific topic.")

