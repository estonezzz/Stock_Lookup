from flask import Flask, render_template, request, redirect
import requests
import pandas as pd
from bokeh.plotting import figure, ColumnDataSource, output_file, show
from bokeh.embed import components

app = Flask(__name__)
app.vars = {}

def grab_ticker(ticker, PriceType):
    output_size = "full"# 0r "compact" "full"

    r = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=" + ticker +"&outputsize=" + output_size \
        + "&apikey=534L2Q54981Z0KG7")
    
    data_json = r.json()
    return data_json
    
def jsonToPandas(data_json):
    df = pd.DataFrame.from_dict(data_json['Time Series (Daily)']).T.reset_index().rename(columns = {'index':'Date', \
    '1. open':'Open', '2. high':'High','3. low':'Low','4. close':'Close','5. adjusted close':'Adj_Close', \
    '6. volume':'Volume', '7. dividend amount':'Dividends', '8. split coefficient':'Splits'})
    df["Date"] = pd.to_datetime(df["Date"])
    df["Close"] = pd.to_numeric(df["Close"])
    df["Adj_Close"] = pd.to_numeric(df["Adj_Close"])
    return df
    
def Plotting(df, ticker, Price_type, Period):
    timeRange = int(Period) #30  or 90 or 254 days
    df1 = df[:timeRange] 
    HEIGHT = 500
    WIDTH = 800
    TOOLS = 'pan,wheel_zoom,save,reset'
    p = figure(x_axis_type="datetime", title="Alpha Vantage Stock Prices", plot_height=HEIGHT, plot_width=WIDTH, tools = TOOLS)

    p.xgrid.grid_line_color=None
    p.ygrid.grid_line_alpha=0.5
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Stock Price'

    stock = ColumnDataSource(data=dict(Date=[], Open=[], Close=[],Adj_Close=[], High=[], Low=[],index=[]))
    stock.data = stock.from_df(df1)
    if Price_type:
        p.line(stock.data['Date'], stock.data['Adj_Close'], line_width=2, alpha=0.8, legend = ticker.upper() + '  Adj. Close' )
    else: p.line(stock.data['Date'], stock.data['Close'], line_width=2, alpha=0.8, legend = ticker.upper() + '  Close' )
    p.legend.location = "top_left"
    return p

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', message = "")
    else:
        app.vars['ticker'] = request.form['ticker']
        app.vars['Period'] = request.form['Period']
        #print(app.vars['ticker'])
        if request.form['Price_type'] == 'cl-price':
            app.vars['Price'] = False
        else: app.vars['Price'] = True 
        json_file = grab_ticker(app.vars['ticker'],app.vars['Price'])
        if 'Error Message' in json_file.keys():
            message = "Double check you entered correct ticker"
            return render_template('index.html', message = message)
        df = jsonToPandas(json_file)
        plot = Plotting(df,app.vars['ticker'],app.vars['Price'],app.vars['Period'])
        script, div = components(plot)
        
        return render_template('chart.html',the_div=div, the_script=script)
        
@app.route('/about')
def about():
  return render_template('about.html')
  
@app.route('/chart', methods=['GET','POST'])
def chart():
    #print(app.vars)
    app.vars['ticker'] = request.form['ticker']
    app.vars['Period'] = request.form['Period']
    #print(app.vars['ticker'])
    if request.form['Price_type'] == 'cl-price':
        app.vars['Price'] = False
    else: app.vars['Price'] = True 
    json_file = grab_ticker(app.vars['ticker'],app.vars['Price'])
    if 'Error Message' in json_file.keys():
        message = "Double check you entered correct ticker"
        return render_template('index.html', message = message)
    df = jsonToPandas(json_file)
    plot = Plotting(df,app.vars['ticker'],app.vars['Price'],app.vars['Period'])
    script, div = components(plot)
    
    return render_template('chart.html',the_div=div, the_script=script)

if __name__ == '__main__':
  app.run()
