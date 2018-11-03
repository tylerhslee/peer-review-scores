#! /usr/bin/env python3
# coding: utf-8
"""
Line graph of Mean Bias and Mean Absolute Bias as a function of Review Length

Output:
  - bias_to_revlen.png
  - mean_bias_to_revlen.png
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plot_bias(data: pd.DataFrame, outdir: str) -> None:
    """
    Scatterplot with hue of tracks
    :param data:
    :param outdir:
    """
    fig, (ax1, ax2) = plt.subplots(2)
    fig.set_size_inches((25, 10))

    # Mean Bias vs. Review Length
    ax = sns.scatterplot('review_length', 'bias', data=data, hue='track', legend=False, ax=ax1)
    ax.set(xlabel='Review Length', ylabel='Bias')

    # Mean Absolute Bias vs. Review Length
    ax = sns.scatterplot('review_length', 'abs_bias', data=data, hue='track', ax=ax2)
    ax.set(xlabel='Review Length', ylabel='Absolute Bias')

    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.savefig(os.path.join(outdir, 'bias_to_revlen.png'), bbox_inches='tight')


def plot_mean_bias(data: pd.DataFrame, outdir: str) -> None:
    """
    Line graph of mean (absolute) bias as a function of review length
    :param data:
    :param outdir:
    """
    grp = data.groupby(by='review_length').mean()

    plt.figure(figsize=(30, 12))
    plt.subplot(2, 1, 1)
    plt.plot(grp.index, grp['bias'])
    plt.xlabel('Review Length')
    plt.ylabel('Mean Bias')
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(grp.index, grp['abs_bias'])
    plt.xlabel('Review Length')
    plt.ylabel('Mean Absolute Bias')
    plt.legend()

    plt.savefig(os.path.join(outdir, 'mean_bias_to_revlen.png'))


if __name__ == '__main__':
    import numpy as np
    PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))
    DATA = pd.read_csv(os.path.join(PROJECT_ROOT, 'data', 'first_reviews.csv'))
    DATA = DATA[['review_length', 'bias', 'track']]
    DATA['review_length'] = DATA[DATA['review_length'] <= 6000]  # Remove outliers
    DATA['abs_bias'] = np.sqrt(DATA['bias'] ** 2)

    # Plot scatter of individual data
    plot_bias(DATA, os.path.join(PROJECT_ROOT, 'data'))

    # Plot line graph of mean biases
    plot_mean_bias(DATA, os.path.join(PROJECT_ROOT, 'data'))
