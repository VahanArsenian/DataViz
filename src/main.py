import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.express as px
import pandas as pd

from model import PairHistogramModel, DataManager, ViolinModel, PairPlotModel, BirthConditionModel

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


dm = DataManager('../d_smp.csv', '../l_smp.csv', processed=True)
ph = PairHistogramModel(dm)
vm = ViolinModel(dm)
pm = PairPlotModel(dm)
bcm = BirthConditionModel(dm)


app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-1', children=[
            dcc.Tab(label='Main', value='tab-1'),
            dcc.Tab(label='Cigarettes usage', value='tab-2'),
            dcc.Tab(label='Birth conditions', value='tab-3'),
    ]),
    html.Div(id='tabs-content')
])


@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            dcc.Dropdown(
                id='hist-feature',
                options=ph.drop_down_options(),
                value=list(ph.feature_labels.keys())[0]
            ),
            dcc.Graph(
                id='hist-graph',
            ),
            dcc.Dropdown(
                id='pair-feature-1',
                options=ph.drop_down_options(),
                value=list(ph.feature_labels.keys())[2]
            ),
            dcc.Dropdown(
                id='pair-feature-2',
                options=ph.drop_down_options(),
                value=list(ph.feature_labels.keys())[3]
            ),
            dcc.Graph(
                id='pair-graph',
            )
        ])
    elif tab == 'tab-2':
        return html.Div([
            dcc.RadioItems(
                id='violin-scale',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            ),
            dcc.Graph(
                id='violin-cig',
            )])
    elif tab == 'tab-3':
        return html.Div([
            dcc.Dropdown(
                id='cond-multi',
                options=bcm.drop_down_options(),
                multi=True,
            ),
            dash_table.DataTable(id='cond-table')
        ])


@app.callback(
    Output('hist-graph', 'figure'),
    Input('hist-feature', 'value')
)
def update_hist(new_feature):
    return ph.draw_figure(new_feature)


@app.callback(
    Output('violin-cig', 'figure'),
    Input('violin-scale', 'value')
)
def update_violin(scale):
    return vm.draw_figure(scale)


@app.callback(Output('pair-graph', 'figure'),
              Input('pair-feature-1', 'value'),
              Input('pair-feature-2', 'value'))
def update_pair(ft1, ft2):
    return pm.draw_figure(ft1, ft2)


@app.callback(Output('cond-table', 'data'),
              Output('cond-table', 'columns'),
              Input('cond-multi', 'value'))
def update_info_table(selection):
    res = bcm.prep_data(selection)
    return res


if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=False)