#! /usr/bin/env python3
# coding: utf-8
"""
Analyses on the acceptance of the paper. Negative score means "reject"; positive score means "accept"; otherwise, the
paper's reviews are "mixed".

Output:
  - bias_to_acceptance.png
  - revlen_to_acceptance.png
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
from matplotlib.axes import Axes


def prep_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    0 means mixed. Positive means "accepted". Negative means "rejected".
    :param data:
    :return:
    """
    data['abs_bias'] = np.sqrt(data['bias'] ** 2)

    # Normalize scores into (-1, 1). There is no score of 0
    data['norm'] = data['score'] / abs(data['score'])
    grp = data.groupby(by='submission_id')

    # If a submission has two unique normalized scores (must be 1 and -1), then its reviews must be mixed (0).
    # If a submission has one unique normalized score (either 1 or -1), then its reviews' leaning can be determined
    # by summing all the scores, which should either all be positive or negative.
    data['acceptance'] = grp['norm'].transform(lambda x: 2 - x.nunique()) * grp['score'].transform(sum)
    data['acceptance'] = data.apply(label_acceptance, axis=1)
    return data[['acceptance', 'bias', 'abs_bias', 'review_length']]


def label_acceptance(x: pd.Series) -> str:
    if x['acceptance'] < 0:
        return 'rejected'
    elif x['acceptance'] > 0:
        return 'accepted'
    else:
        return 'mixed'


def plot_violin(data: pd.DataFrame, y: str, ax: Axes, color: str='orange'):
    sb.violinplot(
        data=data,
        x='acceptance',
        y=y,
        color=color,
        scale='width',
        split=False,
        ax=ax
    )
    ax.set_xlabel('')


if __name__ == '__main__':
    PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))
    data = pd.read_csv(os.path.join(PROJECT_ROOT, 'data', 'first_reviews.csv'))
    data = prep_data(data)

    # 1. Plotting bias and absolute bias

    # Create a common x-axis
    fig = plt.figure()
    fig.set_size_inches((20, 10))
    common_ax = fig.add_subplot(111)
    common_ax.spines['top'].set_color('none')
    common_ax.spines['bottom'].set_color('none')
    common_ax.spines['left'].set_color('none')
    common_ax.spines['right'].set_color('none')
    common_ax.tick_params(labelcolor='w', top=False, bottom=False, left=False, right=False)

    common_ax.set_xlabel('Acceptance')

    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)

    # Individual axes
    for ax in [ax1, ax2]:
        ax.grid(which='major', color='gray', linewidth=0.25, alpha=0.5)

    # Plotting and saving
    plot_violin(data, 'bias', ax1, 'orange')
    plot_violin(data, 'abs_bias', ax2, 'blue')

    ax1.set_ylabel('Bias')
    ax2.set_ylabel('Absolute Bias')
    plt.savefig(os.path.join(PROJECT_ROOT, 'data', 'bias_to_acceptance.png'), bbox_inches='tight')

    # 2. Plotting review length

    # Figure & Axes set up
    fig, ax = plt.subplots()
    fig.set_size_inches((20, 10))
    ax.grid(which='major', color='gray', linewidth=0.25, alpha=0.5)

    # Plotting and saving
    plot_violin(data, 'review_length', ax, 'orange')
    ax.set_xlabel('Acceptance')
    ax.set_ylabel('Review Length')
    plt.savefig(os.path.join(PROJECT_ROOT, 'data', 'revlen_to_acceptance.png'), bbox_inches='tight')

