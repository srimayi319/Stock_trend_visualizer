# Import necessary libraries
from flask import Flask, render_template, request, redirect, url_for, flash  # Flask framework for web application
import yfinance as yf  # Yahoo Finance API to fetch stock data
import plotly.graph_objs as go  # Plotly for interactive stock visualizations
import pandas as pd  # Pandas for data handling

# Initialize Flask application
app = Flask(__name__) 
app.secret_key = "your_secret_key"  # Required for using flash messages (temporary messages to display alerts)

def generate_plot(stocks, chart_type):
    """
    Fetches stock data from Yahoo Finance and generates an interactive chart using Plotly.

    Parameters:
        stocks (list): A list of stock ticker symbols (e.g., ["AAPL", "GOOGL"])
        chart_type (str): Type of chart to generate ("line", "bar", "hist", or "candlestick")

    Returns:
        str: HTML representation of the generated Plotly chart.
    """

    traces = []  # List to store stock data traces (each stock is a separate trace)

    for stock in stocks:
        try:
            # Download stock data for the last 1 month
            data = yf.download(stock, period="1mo")  

            # If no data is available, display a flash message and skip this stock
            if data.empty:
                flash(f"No data available for {stock}")
                continue  

            # Generate different chart types based on user selection
            if chart_type == "line":
                traces.append(go.Scatter(x=data.index, y=data["Close"], mode="lines", name=stock))  # Line chart
            elif chart_type == "bar":
                traces.append(go.Bar(x=data.index, y=data["Close"], name=stock))  # Bar chart
            elif chart_type == "hist":
                traces.append(go.Histogram(x=data["Close"], name=stock))  # Histogram of closing prices
            elif chart_type == "candlestick":
                traces.append(go.Candlestick(
                    x=data.index, open=data["Open"], high=data["High"], low=data["Low"], close=data["Close"], name=stock
                ))  # Candlestick chart

        except Exception as e:
            flash(f"Error fetching data for {stock}: {str(e)}")  # Handle errors gracefully
            continue

    # If no valid stock data was fetched, return an empty string
    if not traces:
        flash("No valid data to visualize.")
        return ""

    # Define chart layout with title and axis labels
    layout = go.Layout(title="Stock Price Visualization", 
                       xaxis_title="Date", 
                       yaxis_title="Price", 
                       template="plotly_dark")

    # Create the figure using the collected traces
    fig = go.Figure(data=traces, layout=layout)

    # Convert the figure to an HTML format for rendering in the template
    return fig.to_html(full_html=False)

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Handles the main page where users select stocks and chart types.

    Methods:
        - GET: Renders the stock selection form.
        - POST: Processes the form submission and redirects to the visualization page.

    Returns:
        - If form submission is valid, redirects to the visualization page.
        - If invalid (e.g., no stock selected), reloads the page with a flash message.
    """

    if request.method == "POST":
        # Get the selected stocks from the form
        stocks = request.form.getlist("stocks")  

        # Get the selected chart type
        chart_type = request.form.get("chart_type")  

        # If no stocks are selected, display an error message and reload the form
        if not stocks:
            flash("Please select at least one stock.")
            return redirect(url_for("index"))

        # Redirect to the visualize page with the selected stocks and chart type
        return redirect(url_for("visualize", stocks=",".join(stocks), chart_type=chart_type))

    # Render the main form page
    return render_template("index.html")

@app.route("/visualize")
def visualize():
    """
    Handles the visualization page where stock charts are displayed.

    Query Parameters:
        - stocks (str): Comma-separated list of selected stock ticker symbols.
        - chart_type (str): Type of chart to display.

    Returns:
        - If valid, renders the visualization page with the generated plot.
        - If invalid (e.g., incorrect chart type), redirects to the index page with an error message.
    """

    # Get the selected stocks and split them into a list
    stocks = request.args.get("stocks", "").split(",")

    # Get the selected chart type, default to "line" if not provided
    chart_type = request.args.get("chart_type", "line")  

    # If no stocks are provided, display an error message and redirect to the home page
    if not stocks or stocks == [""]:
        flash("Invalid stock selection.")
        return redirect(url_for("index"))

    # Define the list of valid chart types
    valid_chart_types = ["line", "bar", "hist", "candlestick"]

    # Validate the selected chart type
    if chart_type not in valid_chart_types:
        flash("Invalid chart type selected.")
        return redirect(url_for("index"))

    # Generate the stock chart based on selected options
    plot_html = generate_plot(stocks, chart_type)

    # Render the visualization page with the generated plot
    return render_template("visualize.html", stocks=stocks, chart_type=chart_type, plot_html=plot_html)

# Run the Flask application in debug mode
if __name__ == "__main__":
    app.run(debug=True)
