#! /usr/bin/env python3
# coding: utf-8
"""
Analyses of the effect of PhD. Bar graph shows mean bias, absolute bias, and review length for each PhD year.

Output:
  - bias_revlen_to_phd.py
  - revlen_to_phd.py
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
from matplotlib.axes import Axes


def prep_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare the dataset for violin plotting.
    :param data: Original dataset
    :return: Dataframe to use in plotting
    """
    # Remove all datapoints without PhD year
    data = data.loc[data['phd_year'].notna(), :]

    # Clump the extremes (oldest and most recent records)
    data = data.apply(create_phd_year_group, axis=1)
    data['abs_bias'] = np.sqrt(data['bias'] ** 2)

    # Sorting here makes the plot's x-axis sorted later as well, which is a string
    data = data.sort_values(by='phd_year')
    return data[['phd_year_group', 'bias', 'abs_bias', 'review_length']]


def create_phd_year_group(row: pd.DataFrame) -> pd.DataFrame:
    """
    Clump all recent (2018+) PhD holders
    :param row:
    :return:
    """
    if row['phd_year'] <= 1990:
        row['phd_year_group'] = '~1990'
    elif row['phd_year'] > 2017:
        row['phd_year_group'] = '2018~'
    else:
        row['phd_year_group'] = str(int(row['phd_year']))
    return row


def plot_violin(data: pd.DataFrame, y: str, ax: Axes, color: str='orange'):
    sb.violinplot(
        data=data,
        x='phd_year_group',
        y=y,
        color=color,
        scale='width',
        split=False,
        ax=ax
    )
    ax.set_xlabel('')


if __name__ == '__main__':
    import os
    PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))
    data = pd.read_csv(os.path.join(PROJECT_ROOT, 'data', 'first_reviews.csv'))
    data = prep_data(data)

    # 1. Plotting bias and absolute bias

    # Create a common x-axis
    fig = plt.figure()
    common_ax = fig.add_subplot(111)
    common_ax.spines['top'].set_color('none')
    common_ax.spines['bottom'].set_color('none')
    common_ax.spines['left'].set_color('none')
    common_ax.spines['right'].set_color('none')
    common_ax.tick_params(labelcolor='w', top=False, bottom=False, left=False, right=False)

    common_ax.set_xlabel('PhD Year')

    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    fig.set_size_inches((40, 10))

    # Individual axes
    for ax in [ax1, ax2]:
        ax.grid(which='major', color='gray', linewidth=0.25, alpha=0.5)

    # Plotting and saving
    plot_violin(data, 'bias', ax1, 'orange')
    plot_violin(data, 'abs_bias', ax2, 'blue')

    ax1.set_ylabel('Bias')
    ax2.set_ylabel('Absolute Bias')
    plt.savefig(os.path.join(PROJECT_ROOT, 'data', 'bias_to_phd.png'), bbox_inches='tight')

    # 2. Plotting review length

    # Figure & Axes set up
    fig, ax = plt.subplots()
    fig.set_size_inches((20, 10))
    ax.grid(which='major', color='gray', linewidth=0.25, alpha=0.5)

    # Plotting and saving
    plot_violin(data, 'review_length', ax, 'orange')
    ax.set_xlabel('PhD Year')
    ax.set_ylabel('Review Length')
    plt.xticks(rotation=75)
    plt.savefig(os.path.join(PROJECT_ROOT, 'data', 'revlen_to_phd.png'), bbox_inches='tight')
