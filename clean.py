#! /usr/bin/env python3
# coding: utf-8
"""
Cleans the review_scores.xlsx dataset into first_reviews.csv. Updated reviews are filtered by time and the fields are
renamed to be easier to understand. Only the Overall score is considered as a review score.

Columns:
  * review_id: Unique identifier for all reviews
  * submission_id: Unique identifier for all papers that are being reviewed
  * member_id: Unique identifier for each member of the reviewers
  * member_name: Name of the reviewer
  * phd_year: Year in which the reviewer received his/her PhD
  * track: Academic track the reviewer is in
  * score: The overall score for the review
  * bias: The bias score of the review
  * review_length: Length of the actual review text
  * review_datetime: Review submission datetime
"""
import re
import logging
import pandas as pd
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)


class Field(Enum):
    F_AUDIENCE: int = 3
    F_OVERALL: int = 5
    F_CONFIDENCE: int = 6
    F_ALTERNATIVE: int = 7


def find_first_reviews(reviews: pd.ExcelFile) -> pd.DataFrame:
    """
    Sorts the results to find the first reviews
    :param reviews: Reviews data
    :return: Dataframe with following columns:
      * review_id
      * submission_id
      * member_id
      * member_name
      * phd_year
      * track
      * score
      * bias
      * review_length
      * review_datetime
    """
    all_reviews = read_all_reviews(reviews)
    members = read_members(reviews)
    combined_reviews = combine_all_reviews(all_reviews, members)
    first_reviews = combined_reviews.drop_duplicates(subset=['member_id', 'submission_id'])
    return calculate_bias(first_reviews)


def read_all_reviews(xlsx: pd.ExcelFile) -> pd.DataFrame:
    """
    :param xlsx: Excel data file
    :return: Dataframe with the following columns:
        * review_id
        * submission_id
        * member_id
        * member_name
        * review_datetime
        * score
        * review_length
    """
    logger.info('read_all_reviews')
    all_reviews = pd.read_excel(xlsx, 'All Reviews')

    # Rename columns
    all_reviews.rename(columns={
        '#': 'review_id',
        'submission #': 'submission_id',
        'member #': 'member_id',
        'member name': 'member_name'
    }, inplace=True)

    # Use lower-case for all member names just in case of improper capitalizations
    all_reviews['member_name'] = all_reviews['member_name'].str.lower()

    # Create a datetime object using the date and time columns
    all_reviews['review_datetime'] = all_reviews['date'] + 'T' + all_reviews['time']
    all_reviews['review_datetime'] = pd.to_datetime(all_reviews['review_datetime'], format='%Y-%m-%dT%H:%M')
    all_reviews.drop(columns=['date', 'time'], inplace=True)

    # Extract just the Overall score
    scores = expand_scores(xlsx, all_reviews)
    scores = scores.loc[scores['field_id'] == Field.F_OVERALL.value, :]
    all_reviews = pd.merge(all_reviews, scores, on='review_id')
    all_reviews.drop(columns=['scores', 'field_id'], inplace=True)

    # Calculate the review length
    all_reviews['review_length'] = all_reviews['text'].str.len()
    all_reviews.drop(columns=['text'], inplace=True)
    return all_reviews


def expand_scores(xlsx: pd.ExcelFile, reviews: pd.DataFrame) -> pd.DataFrame:
    """
    Separate the "scores" column into 4 rows, each containing ONE score for each field
    :param xlsx: Excel file that has field metadata
    :param reviews: All reviews cleaned by read_all_reviews
    :return: Dataframe with the following columns:
      * review_id
      * field_id
      * field_name
      * score
    """
    logger.info('expand_scores')
    fields = pd.read_excel(xlsx, 'Fields')[['field #', 'field title']].copy()

    # Rename the columns
    fields.rename(columns={
        'field #': 'field_id',
        'field title': 'field_name'
    }, inplace=True)

    # Only retain unique definition for each field
    fields.drop_duplicates(subset=['field_id'], inplace=True)
    scores = reviews[['review_id', 'scores']].copy()

    # Split a row into four; tolist() is very important
    tmp = pd.DataFrame(scores['scores'].apply(listify_scores).tolist(), index=scores['review_id']).stack()
    tmp = tmp.reset_index()
    tmp.columns = ['review_id', 'field_id', 'score']

    # Reassign the approprate field_id for each
    tmp['field_id'] = tmp['field_id'].map({0: 3, 1: 5, 2: 6, 3: 7})
    return tmp


def listify_scores(scores: str) -> list:
    """
    Listifies a "scores" column using regex that only looks for integers
    :param scores: Text of criteria and scores
    :return: A list of scores, in the order of the 4 criteria (3, 5, 6, 7)
    """
    pattern = r'\-?\d+'
    return [int(i) for i in re.findall(pattern, scores)]


def read_members(xlsx: pd.ExcelFile) -> pd.DataFrame:
    """
    :param xlsx: Excel data file
    :return: Dataframe with following columns:
      * member_name
      * track
      * phd_year
    """
    logger.info('read_members')
    members = pd.read_excel(xlsx, 'Members')[['First name', 'Last name', 'Track', 'Year of PhD']].copy()

    # Rename the columns
    members.rename(columns={
        'First name': 'first_name',
        'Last name': 'last_name',
        'Track': 'track',
        'Year of PhD': 'phd_year'
    }, inplace=True)

    # Create a single "member name" column with both first and last names
    members['member_name'] = members['first_name'].str.lower() + ' ' + members['last_name'].str.lower()
    members.drop(columns=['first_name', 'last_name'], inplace=True)
    return members


def combine_all_reviews(reviews: pd.DataFrame, members: pd.DataFrame) -> pd.DataFrame:
    """
        Merges the reviews data and members data
        :param reviews: Reviews data
        :param members: Members data
        :return: Dataframe with following columns:
          * review_id
          * submission_id
          * member_id
          * member_name
          * phd_year
          * track
          * review_datetime
          * score
          * review_length
        """
    all_reviews = pd.merge(reviews, members, on='member_name')
    all_reviews.sort_values(by=['member_id', 'submission_id', 'review_datetime'], inplace=True)
    return all_reviews


def calculate_bias(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the bias score for each review.
    :param data: The dataset to calculate the bias on
    :return: Dataframe with the "bias" column appended
    """
    grp = data[['submission_id', 'score']].copy().groupby(by='submission_id')
    means = grp['score'].mean()
    num = grp.count()
    stats = pd.concat([means, num], axis=1).reset_index()
    stats.columns = ['submission_id', 'mean', 'count']

    data_with_mean = pd.merge(data, stats, on='submission_id')[['review_id', 'score', 'mean', 'count']]

    # bias = (avg * n - x) / (n - 1)
    data_with_mean['bias'] = data_with_mean['score'] -  \
        (data_with_mean['mean'] * data_with_mean['count'] - data_with_mean['score']) /  \
        (data_with_mean['count'] - 1)
    return pd.merge(data, data_with_mean[['review_id', 'bias']], on='review_id')


if __name__ == '__main__':
    import os
    PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))
    xlsx = pd.ExcelFile('./data/review_scores.xlsx')
    first_reviews = find_first_reviews(xlsx)
    first_reviews.to_csv(os.path.join(PROJECT_ROOT, 'data', 'first_reviews.csv'))
