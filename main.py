from math import isnan

import pandas as pd
import matplotlib.pyplot as plt

from categories import MINIFIGURE_THEMES, BRAND_THEMES, BRAND_MINIFIGURE_THEMES, THEME_EXCLUDE, LEGO_BRAND_THEMES, \
    PARENT_EXCLUDE, SET_BRANDS

rebrickable_url = 'https://rebrickable.com/downloads/'

sets = pd.read_csv('sets.csv.gz')
themes = pd.read_csv('themes.csv.gz')
sets = sets.merge(
    themes,
    left_on='theme_id',
    right_on='id',
    suffixes=('_set', '_theme'),
)
sets = sets.rename(
    columns={
        'name_set': 'set_name',
        'name_theme': 'theme_name',
    },
)


def get_parent_theme(x):
    if not isnan(x.parent_id):
        return themes.loc[themes.id == x.parent_id, 'name'].values[0]


non_sets = [
    *MINIFIGURE_THEMES,
    *BRAND_MINIFIGURE_THEMES,
    *THEME_EXCLUDE,
    *PARENT_EXCLUDE,
]


all_exclude = [
    *non_sets,
    *BRAND_THEMES,
    *LEGO_BRAND_THEMES,
]

sets['parent_theme'] = sets.apply(get_parent_theme, axis=1)
real_sets = sets.loc[
    (~sets.theme_name.isin(non_sets))
    | (~sets.parent_theme.isin(non_sets))
]
branded = real_sets.loc[
    (real_sets.theme_name.isin(BRAND_THEMES))
    | (real_sets.parent_theme.isin(BRAND_THEMES))
    | (real_sets.set_name.str.contains('|'.join(SET_BRANDS)))
]
year_hist = branded.hist(
    column='year',
    bins=len(branded.year.unique()),
)
plt.show()
