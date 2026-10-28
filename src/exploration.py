import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
polls_df = pd.read_csv(os.path.join(BASE_DIR, 'data', 'raw_polls.csv'))
pollster_ratings_df = pd.read_csv(os.path.join(BASE_DIR, 'data', 'pollster-ratings-combined.csv'))

df = pd.DataFrame(polls_df.copy())

#print(df.head())
#df.shape
#df.info()


# 1. Duplicates and repeated polls
print(df.duplicated().sum())                    # fully identical rows
print(df['poll_id'].nunique(), len(df))         # distinct polls vs rows
print(df['question_id'].nunique())              # same as len(df)? then question_id is unique per row
repeat = df[df['poll_id'].duplicated(keep=False)].sort_values('poll_id')
print(repeat.head(12))                          # which columns differ within one poll_id?
print(df.duplicated(subset=['poll_id', 'cand1_name', 'cand2_name']).sum())  # same poll AND same matchup

# 2. Value ranges
print(df[['samplesize', 'cand1_pct', 'cand2_pct', 'time_to_election',
          'transparency_score', 'margin_poll']].describe())
print((df['samplesize'] <= 0).sum())            # bad sample sizes
print(((df['cand1_pct'] < 0) | (df['cand1_pct'] > 100)).sum())   # out-of-range percentages
print(((df['cand2_pct'] < 0) | (df['cand2_pct'] > 100)).sum())
print((df['cand1_pct'] + df['cand2_pct'] > 100).sum())            # two candidates summing past 100

# 3. Dates
df['polldate'] = pd.to_datetime(df['polldate'])
df['electiondate'] = pd.to_datetime(df['electiondate'])
print((df['polldate'] > df['electiondate']).sum())                 # polls after the election
check = (df['electiondate'] - df['polldate']).dt.days
print((check - df['time_to_election']).abs().describe())           # does time_to_election match the dates?

# 4. Scope and categories
print(df['type_simple'].value_counts())
print(df['cycle'].value_counts().sort_index())
print(df['location'].nunique(), df['pollster'].nunique())

# 5. Consistency within a race
print(df.groupby('race_id')[['cand1_actual', 'cand2_actual']].nunique().max())
# should be 1 and 1: one actual result per race, per candidate

dup15 = df[df.duplicated(subset=['poll_id', 'cand1_name', 'cand2_name'], keep=False)].sort_values(['poll_id', 'cand1_name'])
print(dup15[['poll_id', 'question_id', 'race_id', 'location', 'type_simple', 'cand1_name', 'cand2_name', 'cand1_pct', 'cand2_pct', 'samplesize']])

over = df[df['cand1_pct'] + df['cand2_pct'] > 100]
print(over[['poll_id', 'location', 'type_simple', 'cand1_pct', 'cand2_pct']])

print(df.nlargest(10, 'samplesize')[['pollster', 'location', 'type_simple', 'cycle', 'samplesize']])