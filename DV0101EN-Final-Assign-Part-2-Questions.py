#!/usr/bin/env python
# coding: utf-8

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import numpy as np

# --- OFFLINE DATA GENERATION (Bypasses network connection blocks) ---
np.random.seed(42)
years = list(range(1980, 2014)) * 12
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] * len(range(1980, 2014))
v_types = ['SUV', 'Convertible', 'LowCost Wagon', 'Economy', 'Sports']

data_dict = {
    'Year': sorted(years),
    'Month': months,
    'Recession': [1 if y in [1980, 1981, 1982, 1991, 2001, 2008, 2009] else 0 for y in sorted(years)],
    'Vehicle_Type': np.random.choice(v_types, len(years)),
    'Automobile_Sales': np.random.randint(500, 5000, len(years)),
    'Advertising_Expenditure': np.random.randint(10000, 90000, len(years)),
    'unemployment_rate': np.random.uniform(4.5, 9.5, len(years))
}
data = pd.DataFrame(data_dict)

# Initialize the Dash app
app = dash.Dash(__name__)

# Create the layout of the app
app.layout = html.Div([
    html.H1(
        "Automobile Sales Statistics Dashboard (1980-2013)",
        style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 24, 'padding': '10px'}
    ),
    
    html.Div([
        html.Label("Select Report Type:"),
        dcc.Dropdown(
            id='dropdown-statistics',
            options=[
                {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
                {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
            ],
            placeholder='Select a report type...',
            style={'width': '80%', 'padding': '3px', 'fontSize': '20px', 'textAlignLast': 'center'}
        )
    ]),
    
    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(
            id='select-year',
            options=[{'label': int(i), 'value': int(i)} for i in sorted(data['Year'].unique())],
            placeholder='Select a year...',
            disabled=True,
            style={'width': '80%', 'padding': '3px', 'fontSize': '20px', 'textAlignLast': 'center'}
        )
    ], style={'margin-top': '15px'}),

    html.Div(id='output-container', className='chart-grid', style={'display': 'flex', 'flexDirection': 'column', 'marginTop': '20px'})
])

# Turn on/off the input year dropdown
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics', component_property='value')
)
def update_input_container(selected_statistics):
    if selected_statistics == 'Yearly Statistics':
        return False
    else:
        return True

# Callback for plotting
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='dropdown-statistics', component_property='value'), 
     Input(component_id='select-year', component_property='value')]
)
def update_output_container(selected_statistics, input_year):
    if not selected_statistics:
        return []

    if selected_statistics == 'Recession Period Statistics':
        recession_data = data[data['Recession'] == 1]
        
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(figure=px.line(yearly_rec, x='Year', y='Automobile_Sales', title="Average Sales Fluctuation"))
        
        average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        R_chart2 = dcc.Graph(figure=px.bar(average_sales, x='Vehicle_Type', y='Automobile_Sales', title="Sales by Vehicle Type"))
        
        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(figure=px.pie(exp_rec, values='Advertising_Expenditure', names='Vehicle_Type', title="Ad Spend Distribution"))
        
        unemp_data = recession_data.groupby(['unemployment_rate', 'Vehicle_Type'])['Automobile_Sales'].mean().reset_index()
        R_chart4 = dcc.Graph(figure=px.bar(unemp_data, x='unemployment_rate', y='Automobile_Sales', color='Vehicle_Type', barmode='group', title="Unemployment Effect"))
        
        return [
            html.Div([R_chart1, R_chart2], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px'}),
            html.Div([R_chart3, R_chart4], style={'display': 'flex', 'justifyContent': 'space-around'})
        ]

    elif selected_statistics == 'Yearly Statistics' and input_year:
        yearly_data = data[data['Year'] == input_year]
        
        monthly_sales = yearly_data.groupby('Month')['Automobile_Sales'].sum().reset_index()
        month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        Y_chart1 = dcc.Graph(figure=px.line(monthly_sales, x='Month', y='Automobile_Sales', category_orders={"Month": month_order}, title=f"Monthly Sales Trend - {input_year}"))
        
        avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        Y_chart2 = dcc.Graph(figure=px.bar(avr_vdata, x='Vehicle_Type', y='Automobile_Sales', title="Average Sold by Type"))
        
        exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart3 = dcc.Graph(figure=px.pie(exp_data, values='Advertising_Expenditure', names='Vehicle_Type', title="Ad Expenses Share"))
        
        Y_chart4 = dcc.Graph(figure=px.bar(exp_data, x='Vehicle_Type', y='Advertising_Expenditure', color='Vehicle_Type', title="Ad Budget Breakdown"))
        
        return [
            html.Div([Y_chart1, Y_chart2], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px'}),
            html.Div([Y_chart3, Y_chart4], style={'display': 'flex', 'justifyContent': 'space-around'})
        ]
        
    return []

if __name__ == '__main__':
    app.run(debug=True)