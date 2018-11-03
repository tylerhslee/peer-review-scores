# Peer Review Scores
## Table of Contents
  1. Cleaning the dataset
  1. Calculating the bias
  1. Analyses by PhD years
  1. Analyses by Tracks
  1. Analyses by Acceptance

## Cleaning the dataset
```bash
$ python clean.py
```
Running above command will create `first_reviews.csv` file in the data directory. The resulting csv file will only contain the columns that are relevant to future analyses. These include:<br><br>

  | Field Name | Description |
  | ---------- | ------------|
  | review_id | Unique identifier for all reviews |
  | submission_id | Unique identifier for all papers that are being reviewed |
  | member_id | Unique identifier for each member of the reviewers |
  | member_name | Name of the reviewer |
  | phd_year | Year in which the reviewer received his/her PhD |
  | track | Academic track the reviewer is in |
  | score | The overall score for the review |
  | bias | The bias score of the review |
  | review_length | Length of the actual review text |
  | review_datetime | Review submission datetime |

### Column details
#### review_id, submission_id, member_id
These columns have been renamed from `#`, `submission #`, and `member #` for better readability.

#### member_name
Instead of having two columns for first and last names each, they have been consolidated into one.

#### score
This column only includes the review scores for the "Overall" field. As such, scores for other fields, such as Audience, Confidence, and Alternatives, have been dropped.

#### bias, review_length
These columns are the metrics used to conduct future analyses. For details on calculating bias, please refer to [this section]().

#### review_datetime
This column contains Python datetime objects. It is only used to identify the first reviews per submission per reviewer.

## Calculating the bias
The bias is a metric that calculates how much the reviewer's score differs from the rest of the reviews for the same submission. The following formula is used to calculate the bias:

_bias<sub>i, j</sub> = mean<sub>j</sub> * N<sub>j</sub> - score<sub>i, j</sub> / (N<sub>j</sub> - 1)_

where _i_ is the reviewer ID, _j_ is the submission ID, and _N<sub>j</sub>_ is the number of reviews given for the submission _j_.

## Analyses by PhD years
The distribution of the bias, absolute bias, and review length are visualized using violin plots. The following command should create `bias_to_phd.png` and `revlen_to_phd.png` in the `data` directory:

```bash
$ python bias_revlen_to_phd.py
```

### bias_to_phd.png
This image contains two sets of violin plots, each for the bias and absolute bias, respectively. Both sets are separated by PhD years, and all the data above 2018 have been clumped into one `2018+` category.

### revlen_to_phd.png
This image contains a violin plot that is similar to those in `bias_to_phd.png`, but for review lengths. The representation of the PhD years (x-axis) remains the same.

## Analyses by Tracks
The distribution of the bias, absolute bias, and review length are visualized using violin plots. the following command should create `bias_to_track.png` and `revlen_to_track.png` in the `data` directory:

```bash
$ python bias_revlen_to_track.py
```

### bias_to_track.png
This image contains two sets of violin plots, each for the bias and absolute bias, respectively. Both sets are separated by tracks.

### revlen_to_phd.png
This image contains a violin plot that is similar to those in `bias_to_track.png`, but for review lengths. The representation of the tracks (x-axis) remains the same.
