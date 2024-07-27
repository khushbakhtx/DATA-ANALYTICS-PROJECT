import dash
from dash import Dash, dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

app = dash.Dash(__name__)

app.layout = html.Div()

if __name__ == '__main__':
    app.run_server(debug=True)