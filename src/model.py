import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from collections import Counter
import plotly.express as px
import pandas as pd
import numpy as np

from data import DataManager


class FigureModel:

    def __init__(self, dm: DataManager):
        self.data_manager = dm

    def draw_figure(self, **kwargs):
        raise NotImplementedError

    def prep_data(self, **kwargs):
        raise NotImplementedError


class PairHistogramModel(FigureModel):
    target_features = ['birth_month', 'birth_weekday', 'birth_facility', 'father_age', 'mother_age',
                       'live_birth_order', 'total_birth_order', 'num_prev_cesar']
    feature_labels = {'birth_month': 'Birth month', 'birth_weekday': 'Birth weekday', 'birth_facility':
        'Birth facility', 'father_age': 'Father age', 'mother_age': 'Mother age',
                      'live_birth_order': 'Live birth order', 'total_birth_order': 'Total birth order',
                      'num_prev_cesar': 'Number of previous Cesarean'}

    def drop_down_options(self):
        return [{'label': v, 'value': k} for k, v in self.feature_labels.items()]

    def draw_figure(self, target_feature: str):
        data = self.prep_data(target_feature)
        return px.histogram(data, x=target_feature, color='Status',
                            histnorm='percent', labels=self.feature_labels, barmode='overlay')

    def prep_data(self, target_feature: str):
        target_dead = self.data_manager.dead_df[[target_feature]]
        target_dead['Status'] = 'Dead'
        target_alive = self.data_manager.alive_df[[target_feature]]
        target_alive['Status'] = 'Alive'
        return pd.concat([target_dead, target_alive])


class ViolinModel(FigureModel):

    def prep_data(self, scale):
        df_d = self.data_manager.dead_df[['num_cig_3', 'num_cig_6', 'num_cig_9']]
        df_l = self.data_manager.dead_df[['num_cig_3', 'num_cig_6', 'num_cig_9']]

        df_d = df_d[(df_d < 100).all(axis=1)]
        df_l = df_l[(df_l < 100).all(axis=1)]

        df_d = df_d.melt(value_vars=['num_cig_3', 'num_cig_6', 'num_cig_9'], var_name='per', value_name='n_cig')
        df_d['Status'] = 'Dead'

        df_l = df_l.melt(value_vars=['num_cig_3', 'num_cig_6', 'num_cig_9'], var_name='per', value_name='n_cig')
        df_l['Status'] = 'Alive'

        n_cig_mapper = {
            'num_cig_3': "# cigarettes during I trimester'",
            'num_cig_6': '# cigarettes during II trimester',
            "num_cig_9": '# cigarettes during III trimester'
        }

        result = pd.concat([df_l, df_d])
        result['per'] = result['per'].map(n_cig_mapper)
        result['n_cig'] = np.log10(result['n_cig']) if scale else result['n_cig']
        return result

    def draw_figure(self, scale):
        df = self.prep_data(scale != 'Linear')
        fig = go.Figure()
        fig.add_trace(go.Violin(x=df['per'][df['Status'] == 'Dead'],
                                y=df['n_cig'][df['Status'] == 'Dead'],
                                legendgroup='Dead', scalegroup='Dead', name='Dead',
                                side='negative',
                                line_color='blue', points=False)
                      )
        fig.add_trace(go.Violin(x=df['per'][df['Status'] == 'Alive'],
                                y=df['n_cig'][df['Status'] == 'Alive'],
                                legendgroup='Alive', scalegroup='Alive', name='Alive',
                                side='positive',
                                line_color='orange', points=False)
                      )
        return fig


class PairPlotModel(FigureModel):

    def draw_figure(self, feature_1, feature_2):
        df = self.prep_data(feature_1, feature_2)
        return px.scatter_matrix(df, dimensions=[feature_1, feature_2], color='Status', opacity=0.5)

    def prep_data(self, feature_1, feature_2):
        dead = self.data_manager.dead_df[[feature_1, feature_2]]
        alive = self.data_manager.alive_df[[feature_1, feature_2]]

        dead['Status'] = 'Dead'
        alive['Status'] = 'Alive'

        return pd.concat([dead, alive])


class BirthConditionModel(FigureModel):
    condition_features = ['delivery_method', 'assisted_vent', 'assisted_antibiotics']
    condition_labels = {'delivery_method': 'Delivery method', 'assisted_vent': 'Assisted by ven',
                        'assisted_antibiotics': 'Assisted by antibiotics'}

    def prep_data(self, preselected):
        if preselected is None:
            return None, None
        dead = self.data_manager.dead_df[preselected]
        alive = self.data_manager.alive_df[preselected]

        dead['Status'] = 'Dead'
        alive['Status'] = 'Alive'

        tot = pd.concat([dead, alive])
        res = tot.groupby(preselected).agg(Counter)
        res = res.apply(lambda x: x.Status, result_type='expand', axis=1).sort_index().reset_index()

        if self.condition_features[0] in res.columns:
            res[self.condition_features[0]] = res[self.condition_features[0]].map({1: 'Natural',
                                                                                   2: 'Cesarean', 9: 'Unknown'})

        for cl in set(res.columns) & set(self.condition_features[1:]):
            res[cl] = res[cl].map({'N': 'No', 'Y': 'Yes', 'U': 'Unknown'})

        res = res.rename(columns=self.condition_labels).fillna(0)
        return res.to_dict('record'), [{"name": i, "id": i} for i in
                                       list(map(lambda x: self.condition_labels[x], preselected)) + ['Dead', 'Alive']]

    def draw_figure(self, **kwargs):
        pass

    def drop_down_options(self):
        return [{'label': v, 'value': k} for k, v in self.condition_labels.items()]
