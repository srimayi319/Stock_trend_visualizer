from flask import Flask, render_template, request, redirect, url_for, flash
import yfinance as yf
import plotly.graph_objects as go


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        stocks = request.form.getlist('stocks')
        chart_type = request.form['chart_type']
        return redirect(url_for('visualize', stocks=','.join(stocks), chart_type=chart_type))
    return render_template('index.html')

@app.route('/visualize')
def visualize():
    stocks = request.args.get('stocks').split(',')
    chart_type = request.args.get('chart_type')

    data = {}
    for stock in stocks:
        try:
            df = yf.download(stock, period='1y', interval='1d')  # Ensure adequate data range
            if not df.empty and all(col in df.columns for col in ['Open', 'High', 'Low', 'Close']):
                data[stock] = df
            else:
                flash(f"Data for {stock} is incomplete or missing required columns.")
                return redirect(url_for('index'))
        except Exception as e:
            flash(f"Error fetching data for {stock}: {str(e)}")
            return redirect(url_for('index'))

    plot_html = ""

    if chart_type == 'line':
        fig = go.Figure()
        for stock, df in data.items():
            fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name=stock))
        fig.update_layout(title=f'Line Chart for {", ".join(stocks)}', xaxis_title='Date', yaxis_title='Close Price')
        plot_html = fig.to_html(full_html=False)
    elif chart_type == 'bar':
        fig = go.Figure()
        for stock, df in data.items():
            fig.add_trace(go.Bar(x=df.index, y=df['Close'], name=stock))
        fig.update_layout(title=f'Bar Chart for {", ".join(stocks)}', xaxis_title='Date', yaxis_title='Close Price')
        plot_html = fig.to_html(full_html=False)
    elif chart_type == 'hist':
        fig = go.Figure()
        for stock, df in data.items():
            fig.add_trace(go.Histogram(x=df['Close'], name=stock, opacity=0.75))
        fig.update_layout(title=f'Histogram for {", ".join(stocks)}', xaxis_title='Close Price', yaxis_title='Frequency')
        plot_html = fig.to_html(full_html=False)
    elif chart_type == 'candlestick':
        fig = go.Figure()
        for stock, df in data.items():
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name=stock
            ))
        fig.update_layout(
            title=f'Candlestick Chart for {", ".join(stocks)}',
            xaxis_title='Date',
            yaxis_title='Price',
            xaxis_rangeslider_visible=False  # Hide range slider if not needed
        )
        plot_html = fig.to_html(full_html=False)
    else:
        flash("Invalid chart type selected")
        return redirect(url_for('index'))

    return render_template('visualize.html', stocks=stocks, chart_type=chart_type, plot_html=plot_html)


if __name__ == '__main__':
    app.run(debug=True)


