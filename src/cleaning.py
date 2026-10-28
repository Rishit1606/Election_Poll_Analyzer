import os

import pandas as pd

# Resolve paths from the project root (one level above src/), so the script
# works no matter which directory it is run from.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The raw CSVs live directly in data/, not data/raw/.
POLLS_PATH = os.path.join(BASE_DIR, 'data', 'raw_polls.csv')
RATINGS_PATH = os.path.join(BASE_DIR, 'data', 'pollster-ratings-combined.csv')
OUTPUT_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'polls_clean.csv')

KEEP_COLUMNS = [
    'poll_id', 'race_id', 'cycle', 'location', 'type_simple', 'race', 'pollster',
    'pollster_rating_id', 'transparency_score', 'aapor_roper', 'polldate',
    'electiondate', 'time_to_election', 'samplesize', 'cand1_name', 'cand1_party',
    'cand1_pct', 'cand1_actual', 'cand2_name', 'cand2_party', 'cand2_pct',
    'cand2_actual', 'margin_poll', 'margin_actual',
]


def load_polls(path):
    """Read the raw polls CSV and drop columns we don't use."""
    df = pd.read_csv(path)
    # errors='ignore' so this still works if a column is already missing.
    return df.drop(columns=['partisan', 'methodology'], errors='ignore')


def clean_polls(df):
    """Filter to presidential general-election polls, parse dates, and validate."""
    print(f"Rows before cleaning: {len(df)}")

    # Only presidential general elections are in scope for this analysis.
    df = df[df['type_simple'] == 'Pres-G']

    # Parse dates so we can compare them and do date arithmetic later.
    df = df.assign(
        polldate=pd.to_datetime(df['polldate']),
        electiondate=pd.to_datetime(df['electiondate']),
    )

    # .copy() so later edits don't trigger SettingWithCopyWarning on a slice.
    # cand1_actual / cand2_actual are kept only as columns, never used here.
    df = df[KEEP_COLUMNS].copy()

    # Sanity checks: fail loudly rather than silently analysing bad data.
    assert not df.duplicated(subset=['poll_id', 'race_id']).any(), \
        "Duplicate (poll_id, race_id) rows found"
    assert (df['samplesize'] > 0).all(), "Found samplesize <= 0"
    assert (df['polldate'] <= df['electiondate']).all(), \
        "Found polldate after electiondate"

    print(f"Rows after cleaning: {len(df)}")
    return df


def merge_ratings(polls, ratings):
    """Left-merge pollster ratings onto polls and report polls with no rating."""
    # Both files have 'pollster', 'aapor_roper' and 'inactive'; keep the poll's
    # own values and drop the ratings' copies to avoid _x/_y column suffixes.
    ratings = ratings.drop(columns=['pollster', 'aapor_roper', 'inactive'], errors='ignore')

    # Left merge keeps every poll even if its pollster has no rating.
    # validate='m:1' guarantees one rating per pollster, so rows can't multiply.
    # indicator=True adds a _merge column telling us which polls matched.
    merged = polls.merge(ratings, on='pollster_rating_id', how='left',
                         validate='m:1', indicator=True)

    unmatched = (merged['_merge'] == 'left_only').sum()
    print(f"Polls with no rating: {unmatched} of {len(merged)} "
          f"({1 - unmatched / len(merged):.1%} matched)")

    return merged.drop(columns='_merge')


if __name__ == '__main__':
    polls = clean_polls(load_polls(POLLS_PATH))
    ratings = pd.read_csv(RATINGS_PATH)
    merged = merge_ratings(polls, ratings)

    # Create data/processed/ if it doesn't exist yet.
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    merged.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(merged)} rows to {OUTPUT_PATH}")
