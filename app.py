from flask import Flask, render_template, request, redirect, url_for, flash
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Change this to your secret key!

# Nifty 50 stocks with yfinance tickers (.NS suffix)
nifty_50_stocks = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
    "ICICIBANK.NS", "KOTAKBANK.NS", "LT.NS", "SBIN.NS", "ITC.NS",
    "AXISBANK.NS", "HDFC.NS", "BAJFINANCE.NS", "MARUTI.NS", "BHARTIARTL.NS",
    "ASIANPAINT.NS", "NESTLEIND.NS", "TITAN.NS", "DIVISLAB.NS", "ULTRACEMCO.NS",
    "JSWSTEEL.NS", "WIPRO.NS", "POWERGRID.NS", "DRREDDY.NS", "M&M.NS",
    "TECHM.NS", "BPCL.NS", "COALINDIA.NS", "HCLTECH.NS", "TATASTEEL.NS",
    "GRASIM.NS", "EICHERMOT.NS", "CIPLA.NS", "ADANIGREEN.NS", "ONGC.NS",
    "BAJAJFINSV.NS", "HEROMOTOCO.NS", "SBILIFE.NS", "INDUSINDBK.NS", "TATAMOTORS.NS",
    "UPL.NS", "HDFCLIFE.NS", "SHREECEM.NS", "NTPC.NS", "BRITANNIA.NS",
    "GAIL.NS", "TATACONSUM.NS"
]

def fetch_yfinance_data(symbol):
    """
    Fetch daily historical data for a stock symbol from yfinance.
    Returns a DataFrame with Date as index.
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="100d", auto_adjust=False)
        if df.empty:
            return None
        df = df.rename(columns={'Open': 'Open', 'High': 'High', 'Low': 'Low', 'Close': 'Close'})
        df = df[['Open', 'High', 'Low', 'Close']]
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def generate_plot(stock, chart_type):
    traces = []
    roi_info = {}
    ohlc_info = {}

    data = fetch_yfinance_data(stock)
    if data is None or data.empty:
        flash(f"No data available for {stock}")
        return "", {}, {}

    # Calculate Moving Averages
    data["SMA_7"] = data["Close"].rolling(window=7).mean()
    data["SMA_14"] = data["Close"].rolling(window=14).mean()

    # Calculate ROI (Return on Investment) over period
    initial_close = data["Close"].iloc[0]
    final_close = data["Close"].iloc[-1]
    roi = ((final_close - initial_close) / initial_close) * 100
    roi_info[stock] = round(roi, 2)

    # Latest OHLC data
    latest_row = data.iloc[-1]
    ohlc_info[stock] = {
        "Open": round(latest_row["Open"], 2),
        "High": round(latest_row["High"], 2),
        "Low": round(latest_row["Low"], 2),
        "Close": round(latest_row["Close"], 2)
    }

    # Create charts based on user selection
    if chart_type == "line":
        traces.append(go.Scatter(x=data.index, y=data["Close"], mode="lines", name=f"{stock} Close"))
        traces.append(go.Scatter(x=data.index, y=data["SMA_7"], mode="lines", name=f"{stock} SMA 7"))
        traces.append(go.Scatter(x=data.index, y=data["SMA_14"], mode="lines", name=f"{stock} SMA 14"))

    elif chart_type == "candlestick":
        traces.append(go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name=stock
        ))

    elif chart_type == "bar":
        traces.append(go.Bar(x=data.index, y=data["Close"], name=stock))

    elif chart_type == "hist":
        traces.append(go.Histogram(x=data["Close"], name=stock))

    layout = go.Layout(
        title=f"Stock Price Visualization for {stock}",
        xaxis_title="Date",
        yaxis_title="Price (INR)",
        template="plotly_dark"
    )

    fig = go.Figure(data=traces, layout=layout)
    fig_html = fig.to_html(full_html=False)

    return fig_html, roi_info, ohlc_info

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        selected_stock = request.form.get("stock")
        chart_type = request.form.get("chart_type")

        if not selected_stock:
            flash("Please select a stock.")
            return redirect(url_for("index"))

        return redirect(url_for("visualize", stock=selected_stock, chart_type=chart_type))

    return render_template("index.html", all_stocks=nifty_50_stocks)

@app.route("/visualize")
def visualize():
    stock = request.args.get("stock")
    chart_type = request.args.get("chart_type", "line")

    if not stock:
        flash("Invalid stock selection.")
        return redirect(url_for("index"))

    plot_html, roi_info, ohlc_info = generate_plot(stock, chart_type)

    return render_template(
        "visualize.html",
        stock=stock,
        chart_type=chart_type,
        plot_html=plot_html,
        roi_info=roi_info,
        ohlc_info=ohlc_info
    )

if __name__ == "__main__":
    app.run(debug=True)
