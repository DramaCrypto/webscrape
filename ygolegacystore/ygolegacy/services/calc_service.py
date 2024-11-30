import os
import pickle

from ygolegacy.db_config import PICKLE_PATH


def read_pickle(name):
    path = os.path.join(PICKLE_PATH, f'{name}.pickle')
    with open(path, 'rb') as handle:
        return pickle.load(handle)


def get_calc_page(page_type):
    if page_type in ['stock', 'value_usd', 'value_cad']:
        return read_pickle(page_type)
    return {}
