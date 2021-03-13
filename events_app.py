#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 11:59:33 2021

@author: tcicchini
"""

import os
import pandas as pd
import plotly.express as px  # (version 4.7.0)
import dash  # (version 1.12.0) pip install dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_leaflet as dl
import geojson as gjs
from dash.dependencies import Input, Output
from dash_leaflet import express as dlx

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.FLATLY])


# Bring the data
df_events = pd.read_csv(os.getcwd() + '/events_app.csv',
                        parse_dates = ['Reported Date'],
                        date_parser = pd.to_datetime
                        )
df_events = df_events.rename({'Web ID' : 'Events'},
                             axis = 1)
df_routes = pd.read_csv(os.getcwd() + '/rutas_app.csv')
df_supraRoutes = pd.read_csv(os.getcwd() + '/supraRutas_app.csv')

routes_supraRoutes_options = {'Route' : df_routes.route.to_list(),
                              'Supra Route' : df_supraRoutes.route.to_list()
                              }
atribute_list = ['Events', 'Number Dead','Minimum Estimated Number of Missing', 'Total Dead and Missing','Number of Survivors']

min_date = df_events['Reported Date'].min()
max_date = df_events['Reported Date'].max()

func = {'Events' : 'count',
        'Number Dead' : 'sum',
        'Minimum Estimated Number of Missing' : 'sum',
        'Total Dead and Missing' : 'sum',
        'Number of Survivors' : 'sum'}
select_df_color = {'Supra Route' : df_supraRoutes.set_index('route').to_dict()['colors'],
                   'Route' : df_routes.set_index('route').to_dict()['colors']}

df_routes = gjs.load(open(os.getcwd() + '/routes.geojson','rb'))
# App layout  - Using Bootstrap

app.layout = html.Div([dbc.Row(dbc.Col(html.H1("Routes and SupraRoutes Temporal Analysis",
                                              style = {'text-align': 'center'})
                                      ),
                               className = 'h-10'
                              ),
                       dbc.Row(dbc.Col(html.Br()
                                       ),
                               className = 'h-15'
                               ),
                       dbc.Row([dbc.Col(html.Div([dbc.Row(dbc.Col(dcc.Graph(id = 'temporal-analysis',
                                                                            figure = {}
                                                                            ),
                                                                  width = 12)
                                                          ),
                                                  dbc.Row(dbc.Col(dl.Map(dl.LayersControl([dl.BaseLayer(dl.TileLayer(id = 'layer',
                                                                                                                     url = 'http://{s}.tile.stamen.com/toner-lite/{z}/{x}/{y}.png',
                                                                                                                     attribution = 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.',
                                                                                                                     ),
                                                                                                        name = 'Base Map',
                                                                                                        checked = True
                                                                                                        ),
                                                                                           dl.Overlay([dl.GeoJSON(id = 'map-rutes',
                                                                                                                  data = df_routes
                                                                                                                  )],
                                                                                                      name = 'Base Map',
                                                                                                      checked = True
                                                                                                      ),
                                                                                           dl.Overlay(id = 'map-events',
                                                                                                      children = [],
                                                                                                      name = 'Events Points',
                                                                                                      )
                                                                                           ],
                                                                                          ),
                                                                         style = {'width': '800px', 'height': '400px'},
                                                                         zoom = 4,
                                                                         center = (37,15),
                                                                         id = 'map-analysis'),
                                                                  width = {'offset' : 1}
                                                                  )
                                                          )
                                                  ]
                                                 ),
                                        width = {'size' : 7}
                                        ),
                                dbc.Col(html.Div([dbc.Row([dbc.Col(html.H4('Date Range Selector: ',
                                                                           style = {'text-align': 'left'}
                                                                           ),
                                                                   width = {'size' : 6}
                                                                   ),
                                                           dbc.Col(dcc.DatePickerRange(id = 'date-picker-range',
                                                                                       min_date_allowed = min_date,
                                                                                       max_date_allowed = max_date,
                                                                                       start_date = min_date,
                                                                                       end_date = max_date
                                                                                       )
                                                                  )],
                                                          align = 'top'
                                                          ),
                                                  dbc.Row(dbc.Col(html.Br()
                                                                  )
                                                          ),
                                                  dbc.Row([dbc.Col(html.H6('Route/Supra Route Agregation: '),
                                                                   width = {'size' : 3}),
                                                           dbc.Col(dcc.RadioItems(id = 'agregation_option',
                                                                                  options = [{'label' : 'Route', 'value' : 'Route'},
                                                                                             {'label' : 'Supra Route', 'value' : 'Supra Route'},
                                                                                             ],
                                                                                  value = 'Route'
                                                                                  ),
                                                                    width = {'size' : 3}
                                                                   ),
                                                           dbc.Col(html.H6('Atribute Agregation: '),
                                                                   width = {'size' : 2}
                                                                   ),
                                                           dbc.Col(dcc.Dropdown(id = "slct_atribute",
                                                                                options = [{'label' : atribute, 'value' : atribute} for atribute in atribute_list],
                                                                                multi = False,
                                                                                value = atribute_list[0],
                                                                                style = {'width': "100%"}
                                                                                ),
                                                                    width = {'size' : 4}
                                                                    ),
                                                           ],
                                                          align = 'center'
                                                          ),
                                                  dbc.Row(dbc.Col(html.H5('Option Selection: ')
                                                                  )
                                                          ),
                                                  dbc.Row(dbc.Col(dcc.Dropdown(id = 'routes_selection',
                                                                               multi = True,
                                                                               placeholder = 'Select Route/Supra Route'
                                                                               )
                                                                  ),
                                                          align = 'bottom'
                                                          )
                                                  ]
                                                 )
                                        )
                                ],
                               className = 'h-75',
                               ) 
                       ],
                      )
                      

# Connect the Plotly graphs with Dash Components

@app.callback(Output('routes_selection', 'options'),
              Input('agregation_option', 'value')
              )
def set_routes_options(selected_agregation):
    return [{'label': i, 'value': i} for i in routes_supraRoutes_options[selected_agregation]]

@app.callback(Output('routes_selection', 'value'),
              Input('routes_selection', 'options')
              )
def set_routes_values(avaiable_options):
    return [i['value'] for i in avaiable_options]

@app.callback([Output(component_id = 'temporal-analysis', component_property = 'figure'),
               Output(component_id = 'map-events', component_property = 'children')
               ],
              [Input(component_id = 'date-picker-range', component_property = 'start_date'),
               Input(component_id = 'date-picker-range', component_property = 'end_date'),
               Input(component_id = 'agregation_option', component_property = 'value'),
               Input(component_id = 'routes_selection', component_property = 'value'),
               Input(component_id = 'slct_atribute', component_property = 'value'),
               ]
              )
def update_graph(start_date, end_date, agregation_option, routes, atribute):

    df = df_events.copy()
    df = df[(df[agregation_option].isin(routes)) & (df['Reported Date'].between(start_date, end_date))].groupby(by = [pd.Grouper(key = 'Reported Date',
                                                                                                                                  freq = '60D'),
                                                                                                                      agregation_option]
                                                                                                                )[atribute].agg(func[atribute]).reset_index().sort_values(by = [agregation_option, 'Reported Date'])
    df['color'] = [select_df_color[agregation_option][r] for r in df[agregation_option]]
    fig = px.line(df,
                  x = 'Reported Date',
                  y = atribute,
                  color = agregation_option,
                  color_discrete_map = select_df_color[agregation_option],
                  title = '{} Time Evolution'.format(atribute)
                  )
    df = df_events.copy()
    df = df[(df[agregation_option].isin(routes)) & (df['Reported Date'].between(start_date, end_date))][['Reported Date', 'lat', 'lon']]

    df['popup'] = [d.date() for d in df['Reported Date']]
    df = [row.to_dict() for row in df.iloc]
    df = dlx.dicts_to_geojson(df)

    
    
    return fig, dl.GeoJSON(data = df)
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True,
                   port = '3005')