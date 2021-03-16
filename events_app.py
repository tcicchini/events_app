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
from dash.dependencies import Input, Output
import geopandas as gpd

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.FLATLY])
# Global Path for data
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
# Bring the data
df_events = pd.read_csv(os.path.join(THIS_FOLDER, 'IOM_EV_input.csv'),
                        sep = ';',
                        parse_dates = ['Reported Date'],
                        date_parser = pd.to_datetime,
                        )[['Reported Date',
                           'Minimum Estimated Number of Missing',
                           'Total Dead and Missing',
                           'Number of Survivors',
                           'Number Dead',
                           'Location Coordinates']
                           ]        
df_events['Events'] = [1 for i in range(len(df_events))]
df_events['Total Dead and Missing'] = df_events['Total Dead and Missing'].apply(lambda x: x.replace(',','')).astype(int)
df_events = gpd.GeoDataFrame(df_events, geometry = gpd.points_from_xy(df_events['Location Coordinates'].apply(lambda x:x.split(',')[1][1:]), df_events['Location Coordinates'].apply(lambda x: x.split(',')[0])))
df_events.crs = 'EPSG:4326'
df_routes = gpd.read_file(os.path.join(THIS_FOLDER, 'newRoutes'))
df_routes['route'] = df_routes['route'].apply(lambda x: x.replace('Polygon_','').replace('_',' '))

dict_route_supraRoute = {'Central Mediterranean 1' : 'Central Mediterranean',
                         'Central Mediterranean 2' : 'Central Mediterranean',
                         'Central Mediterranean 3' : 'Central Mediterranean',
                         'Strait + goulf of Cadix route' : 'Western Mediterranean',
                         'Alboran route' : 'Western Mediterranean',
                         'Canary islands route 1' : 'Canary islands route',
                         'Canary islands route 2' : 'Canary islands route',
                         'Algeria route' : 'Western Mediterranean',
                         'Eastern Mediterranean 1' : 'Eastern Mediterranean',
                         'Eastern Mediterranean 2' : 'Eastern Mediterranean',
                         'Eastern Mediterranean 3' : 'Eastern Mediterranean',
                         'Lebanon to Cyprus route' : 'Lebanon to Cyprus route',
                         'Evros and Rodopi route' : 'Eastern Mediterranean',
                         'Marmaris to Rhodes route' : 'Eastern Mediterranean',
                         'Kas to Kastellorizo' : 'Eastern Mediterranean',
                         'Cesme to Chios route' : 'Eastern Mediterranean',
                         'Egypt Greece Italy route' : 'Egypt Greece Italy route'}
dict_colors = {'Alboran route': '#80FF00',
               'Algeria route': '#00FF40',
               'Canary islands route 1': '#20FF00',
               'Canary islands route 2': '#00FFFF',
               'Central Mediterranean 1': '#FF0000',
               'Central Mediterranean 2': '#FF6000',
               'Central Mediterranean 3': '#FFBF00',
               'Cesme to Chios route': '#FF00BF',
               'Eastern Mediterranean 1': '#00FF9F',
               'Eastern Mediterranean 2': '#00FFFF',
               'Eastern Mediterranean 3': '#009FFF',
               'Egypt Greece Italy route': '#FF0060',
               'Evros and Rodopi route': '#2000FF',
               'Kas to Kastellorizo': '#DF00FF',
               'Lebanon to Cyprus route': '#0040FF',
               'Marmaris to Rhodes route': '#8000FF',
               'Other': 'black',
               'Strait + goulf of Cadix route': '#DFFF00'}
df_routes['colors'] = df_routes.route.apply(lambda x: dict_colors[x])
df_routes['Supra Route'] = df_routes.route.apply(lambda x: dict_route_supraRoute[x])
df_routes.rename({'route' : 'Route'}, axis = 1, inplace = True)

df_events = gpd.sjoin(df_events,
                      df_routes,
                      how = 'left'
                      )[['Reported Date',
                         'Minimum Estimated Number of Missing',
                         'Total Dead and Missing',
                         'Number of Survivors',
                         'Number Dead',
                         'Events',
                         'geometry',
                         'Route',
                         'Supra Route',
                         ]
                         ]
df_events['Route'].fillna('Other', inplace = True)
df_events['Supra Route'].fillna('Other', inplace = True)


routes_supraRoutes_options = {'Route' : df_routes['Route'].unique().tolist(),
                              'Supra Route' : df_routes['Supra Route'].unique().tolist()
                              }
routes_supraRoutes_options['Route'].append('Other')
routes_supraRoutes_options['Supra Route'].append('Other')
atribute_list = ['Events', 'Number Dead','Minimum Estimated Number of Missing', 'Total Dead and Missing','Number of Survivors']

min_date = df_events['Reported Date'].min()
max_date = df_events['Reported Date'].max()

select_df_color = {'Supra Route' : df_routes[['Supra Route','colors']].drop_duplicates('Supra Route', ).set_index('Supra Route').to_dict()['colors'],
                   'Route' : dict_colors}
select_df_color['Supra Route']['Other'] = 'black'

map_key = 'Z1IZmXwfuHxpLnPUW9lp'
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
                                                                                                                     url = 'https://api.maptiler.com/maps/outdoor/256/{z}/{x}/{y}@2x.png?key=' + map_key,
                                                                                                                     attribution = '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> ' + '<a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap contributors</a>',
                                                                                                                     ),
                                                                                                        name = 'Base Map',
                                                                                                        checked = True
                                                                                                        ),
                                                                                           dl.Overlay(children = [],
                                                                                                      name = 'Routes Polygons',
                                                                                                      checked = True,
                                                                                                      id = 'map-routes'
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
               ],
              [Input(component_id = 'date-picker-range', component_property = 'start_date'),
               Input(component_id = 'date-picker-range', component_property = 'end_date'),
               Input(component_id = 'agregation_option', component_property = 'value'),
               Input(component_id = 'routes_selection', component_property = 'value'),
               Input(component_id = 'slct_atribute', component_property = 'value'),
               ]
              )
def update_graph(start_date, end_date, agregation_option, routes, atribute):
    # Temporal analysis
    df = df_events.copy()
    df = df[(df[agregation_option].isin(routes)) & (df['Reported Date'].between(start_date, end_date))].groupby(by = [pd.Grouper(key = 'Reported Date',
                                                                                                                                  freq = '60D'),
                                                                                                                      agregation_option]
                                                                                                                )[atribute].apply(sum).reset_index().sort_values(by = [agregation_option, 'Reported Date'])
    df['color'] = [select_df_color[agregation_option][r] for r in df[agregation_option]]
    fig = px.line(df,
                  x = 'Reported Date',
                  y = atribute,
                  color = agregation_option,
                  color_discrete_map = select_df_color[agregation_option],
                  title = '{} Time Evolution'.format(atribute)
                  )
        
    
    return fig,
@app.callback([Output(component_id = 'map-events', component_property = 'children'),
               ],
              [Input(component_id = 'date-picker-range', component_property = 'start_date'),
               Input(component_id = 'date-picker-range', component_property = 'end_date'),
               Input(component_id = 'agregation_option', component_property = 'value'),
               Input(component_id = 'routes_selection', component_property = 'value'),
               ]
              )
def update_events(start_date, end_date, agregation_option,routes):
    # Events Layer Map
    df = df_events.copy()
    df = df[(df[agregation_option].isin(routes)) & (df['Reported Date'].between(start_date, end_date))]
    df['color'] = [select_df_color[agregation_option][r] for r in df[agregation_option]]
    map_events_children = []

    for row in df.itertuples():
        map_events_children.append(dl.Marker(position = [row.geometry.y, row.geometry.x],
                                             children = dl.Popup('Reported Date: {}'.format(row._1.date()
                                                                                            )
                                                                 )
                                             )
                                   )

    return dl.LayerGroup(map_events_children),

@app.callback([Output(component_id = 'map-routes', component_property = 'children'),
               ],
              [Input(component_id = 'agregation_option', component_property = 'value'),
               Input(component_id = 'routes_selection', component_property = 'value'),
               ]
              )
def update_routes(agregation_option, routes):
    # Routes Layer Map
    df = df_routes.copy()
    df = df[df[agregation_option].isin(routes)]
    map_routes_children = []
    for row in df.itertuples():
        map_routes_children.append(dl.Polygon(positions = [(p[1], p[0]) for p in row.geometry.exterior.coords],
                                              children = dl.Tooltip(row.Route),
                                              color = dict_colors[row.Route],
                                              fillColor = dict_colors[row.Route]
                                              )
                                   )
    
    return dl.LayerGroup(map_routes_children),
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True,
                   port = '3005')
