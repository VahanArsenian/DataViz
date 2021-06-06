import pandas as pd


target_columns = ['idnumber', 'dob_mm', 'dob_wk', 'bfacil', 'fagecomb','mager41',
                                                         'lbo', 'tbo', 'cig_1', 'cig_2', 'cig_3','rf_ncesar',
                                                         'dmeth_rec', 'bwtr14', 'ab_vent6', 'ab_antibio', 'aged']

friendly_columns_map = {
    'idnumber': 'id',
    'dob_mm': 'birth_month',
    'dob_wk': 'birth_weekday',
    'bfacil': 'birth_facility',
    'fagecomb': 'father_age',
    'mager41': 'mother_age',
    'lbo': 'live_birth_order',  # how many alive children has a mother had
    'tbo': 'total_birth_order',  # how many children has a mother had
    'cig_1': 'num_cig_3',  # number of cigarettes in the first trimester
    'cig_2': 'num_cig_6',  # number of cigarettes in the second trimester
    'cig_3': 'num_cig_9',  # number of cigarettes in the third trimester
    'rf_ncesar': 'num_prev_cesar',  # number of previous Cesarean
    'dmeth_rec': 'delivery_method',
    'bwtr14': 'birth_weight',
    'ab_vent6': 'assisted_vent',
    'ab_antibio': 'assisted_antibiotics',
}


class DataManager:

    def __init__(self, dead_path: str, alive_path: str, processed=True):

        if not processed:
            self.dead_df = pd.read_csv(dead_path, usecols=target_columns)
            self.alive_df = pd.read_csv(alive_path, usecols=target_columns)
            self.dead_df = self.dead_df.rename(columns=friendly_columns_map)
            self.alive_df = self.alive_df.rename(columns=friendly_columns_map)
            self.sample_alive()
            self.filter_age()
        else:
            self.dead_df = pd.read_csv(dead_path)
            self.alive_df = pd.read_csv(alive_path)

    def sample_alive(self):
        self.alive_df = self.alive_df[self.alive_df.id.isna()].sample(len(self.dead_df))

    def filter_age(self):
        self.dead_df = self.dead_df[self.dead_df['father_age'] < 80]
        self.alive_df = self.alive_df[self.alive_df['father_age'] < 80]

