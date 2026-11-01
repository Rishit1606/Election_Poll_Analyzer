import os

import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'polls_clean.csv')
OUTPUT_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'race_averages.csv')

SAMPLE_CAP = 3000      # polls larger than this count as 3000
HALF_LIFE_DAYS = 14    # a poll's weight halves every 14 days before the election


def add_weights(df):
    """Add one weight per poll: sample size x recency x pollster quality."""
    df = df.copy()

    # Sampling error shrinks with sqrt(n); the cap stops huge online polls dominating.
    df['sample_weight'] = np.sqrt(df['samplesize'].clip(upper=SAMPLE_CAP))

    # Exponential decay: closer to election day = higher weight.
    df['recency_weight'] = 0.5 ** (df['time_to_election'] / HALF_LIFE_DAYS)

    # Lower pollster error = higher weight. Unrated pollsters get the median error.
    error = df['error_ppm'].fillna(df['error_ppm'].median()).clip(lower=0.1)
    df['quality_weight'] = 1 / error

    df['weight'] = df['sample_weight'] * df['recency_weight'] * df['quality_weight']
    return df


def weighted_mean(values, weights):
    return (values * weights).sum() / weights.sum()


def race_averages(df):
    """One row per race: weighted and simple averages, plus the actual result."""
    rows = []
    for race_id, g in df.groupby('race_id'):
        w1 = weighted_mean(g['cand1_pct'], g['weight'])
        w2 = weighted_mean(g['cand2_pct'], g['weight'])
        s1, s2 = g['cand1_pct'].mean(), g['cand2_pct'].mean()
        actual_margin = g['margin_actual'].iloc[0]

        rows.append({
            'race_id': race_id,
            'cycle': g['cycle'].iloc[0],
            'location': g['location'].iloc[0],
            'n_polls': len(g),
            'weighted_cand1': w1,
            'weighted_cand2': w2,
            'simple_cand1': s1,
            'simple_cand2': s2,
            'actual_margin': actual_margin,
            'weighted_error': abs((w1 - w2) - actual_margin),
            'simple_error': abs((s1 - s2) - actual_margin),
        })
    return pd.DataFrame(rows)


if __name__ == '__main__':
    polls = add_weights(pd.read_csv(INPUT_PATH))
    races = race_averages(polls)
    races.to_csv(OUTPUT_PATH, index=False)

    print(f"Races: {len(races)}")
    print(f"Mean margin error, weighted: {races['weighted_error'].mean():.2f}")
    print(f"Mean margin error, simple:   {races['simple_error'].mean():.2f}")


