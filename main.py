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
sets['unbranded'] = sets.real & ~sets.branded
fig, ax = plt.subplots(constrained_layout=True)
hist_plot = ax.twinx()
ratio_plot = ax.twinx()
ratio_plot.set_ylim(0, 0.75)
hist_plot.hist(
    [
        sets.loc[sets.branded].year,
        sets.loc[sets.unbranded].year,
    ],
    bins=list(range(sets.year.min(), sets.year.max() + 1)),
    stacked=True,
    label=[
        'Branded',
        'Unbranded',
    ]
)
ax.set_ylim(0, 700)
years = sets.year.unique()
round_up = years.min() + (5 - years.min() % 5)
round_down = years.max() - years.max() % 5
ticks = [*range(round_up, round_down + 5, 5), years.max()]
ax.set_xticks(ticks=ticks, labels=ticks, rotation=70)
hist_plot.set_yticks([])
ax.set_xlabel('Year')
ax.set_ylabel('# Sets Released')
ax.set_title('Branded vs unbranded sets released by year')
hist_plot.legend(
    loc='upper left',
)
ratio_df = sets.groupby('year').agg(
    num_branded=pd.NamedAgg('branded', 'sum'),
    num_unbranded=pd.NamedAgg('unbranded', 'sum'),
)
ratio_df['ratio'] = (ratio_df.num_branded / (ratio_df.num_unbranded + ratio_df.num_branded)).fillna(0.0)
ratio_plot.plot(ratio_df.ratio, label='Ratio')
ratio_plot.set_ylabel('Ratio of branded to # sets')
plt.show()
