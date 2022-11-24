from math import isnan

import pandas as pd
import matplotlib.pyplot as plt

from categories import MINIFIGURE_THEMES, BRAND_THEMES, BRAND_MINIFIGURE_THEMES, THEME_EXCLUDE, LEGO_BRAND_THEMES, \
    PARENT_EXCLUDE, SET_BRANDS, LEGO_SET_BRANDS

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

all_brands = [
    *BRAND_THEMES,
    *LEGO_BRAND_THEMES,
]

sets['parent_theme'] = sets.apply(get_parent_theme, axis=1)
sets['real'] = ~sets.theme_name.isin(non_sets) \
    & ~sets.parent_theme.isin(non_sets) \
    & ~sets.set_num.str.contains('[a-zA-Z]')  # Usually non
sets['branded'] = sets.real \
    & (
        sets.theme_name.isin(all_brands)
        | sets.parent_theme.isin(all_brands)
        | sets.set_name.str.contains('|'.join([*SET_BRANDS, *LEGO_SET_BRANDS]))
    )
plt.hist(
    [
        # Smaller dataset followed by larger
        sets.loc[sets.real & sets.branded].year,
        sets.loc[sets.real & ~sets.branded].year,
    ],
    bins=list(range(sets.year.min(), sets.year.max() + 1)),
    stacked=True,
    label=[
        'Branded',
        'Unbranded',
    ]
)
years = sets.year.unique()
round_up = years.min() + (5 - years.min() % 5)
round_down = years.max() - years.max() % 5
ticks = [*range(round_up, round_down + 5, 5), years.max()]
plt.xticks(ticks=ticks, labels=ticks, rotation=70)
plt.xlabel('Year')
plt.ylabel('# Sets Released')
plt.title('Branded vs unbranded sets released by year')
plt.legend(
    loc='upper left',
)
plt.show()
