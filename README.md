# Election Polling Analyzer

A Python tool for loading, cleaning, and analyzing election polling data to surface trends, averages, and uncertainty across pollsters.

## Features

- Load polling data from CSV files
- Clean and normalize poll records (dates, sample sizes, candidate names)
- Compute weighted polling averages (by sample size and recency)
- Estimate margin of error for each poll and for the aggregate
- Track candidate support over time
- Visualize trends with charts

## Tech Stack

- Python 3.10+
- pandas, NumPy
- matplotlib

## Project Structure

```
election-polling-analyzer/
├── data/            # Raw and cleaned polling CSVs
├── src/
│   ├── loader.py    # Reads and validates poll data
│   ├── cleaner.py   # Normalizes fields and removes bad rows
│   ├── analysis.py  # Averages, weighting, margin of error
│   └── plots.py     # Trend charts
├── main.py          # Entry point
├── requirements.txt
└── README.md
```

## Getting Started

```bash
git clone https://github.com/Rishit1606/election-polling-analyzer.git
cd election-polling-analyzer
pip install -r requirements.txt
python main.py --input data/polls.csv
```

## Input Format

| Column       | Description                      |
|--------------|----------------------------------|
| pollster     | Name of the polling organization |
| date         | Poll end date (YYYY-MM-DD)       |
| sample_size  | Number of respondents            |
| candidate    | Candidate name                   |
| percent      | Support percentage               |

## How It Works

1. **Load**: read the CSV and validate required columns.
2. **Clean**: parse dates, drop incomplete rows, standardize names.
3. **Aggregate**: weight each poll by sample size and recency, then average per candidate.
4. **Uncertainty**: compute margin of error using the standard proportion formula.
5. **Visualize**: plot support over time with the weighted average overlaid.

## Roadmap

- [ ] Pollster quality ratings as weights
- [ ] State-level breakdowns
- [ ] Command-line filters (date range, pollster)
- [ ] Unit tests

## Author

Rishit, Computer Science, Arizona State University
GitHub: [@Rishit1606](https://github.com/Rishit1606)
