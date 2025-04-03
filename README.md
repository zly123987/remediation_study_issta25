# remediation-study
This repository contains the script for the paper submitted to ISSTA25 named "Fixing Outside the Box: Uncovering Tactics for Open-Source
Security Issue Management"

## Usage of scripts
### Environment
Setup the environment by running
```
python3 -m venv venv
&& source venv/bin/activate
&& pip install -r requirement.txt
```
Note that all data interacted are stored in a mongodb instance. To start, the mongodb must be running with the default configuration (localhost:27017) without credentials. The mongodb instance can be initialized and run in a docker container by 
```
docker-compose build
&& docker-compose up
```
### Credential Setup
As the crawling from GitHub requires interaction with GitHub API demanding the GitHub tokens for swift crawling. Please supply four GitHub tokens that allowing to use GitHub API in `config.py`.
The credential of mongodb instance has already been set in `config.py` by default. 

### Running Scripts
The scripts are categorized into Data collection and Statistics Scripts. 
Run the `entry_data.py` to collect issues and repositories from GitHub via GitHub API and store them to mongodb instance by
```
python entry_data.py
```
* **For specific functions with documentations please refer to `entry_data.py`**


Run the statistics scripts to generate the statistics for the paper by
```
python entry_script.py
```

### Directory Structure
```
├── config.py # For credential setup
├── docker-compose.yml # For mongodb setup
├── entry_data.py # Entry script for data collection
├── entry_script.py # Entry script for statistics generation
├── README.md # This file
├── requirements.txt # Required packages for python
├── scripts # Scripts for data collection and statistics
│   ├── all_to_one.py # Combine all the data into one collection
│   ├── categorize_rejected_fix.py # Categorize the rejected fix
│   ├── count_any.py # Count the number of issues
│   ├── data_collection # Scripts for data collection
│   │   ├── github_advisory.py # Collect advisory
│   │   ├── github_issue_events.py # Collect issue events
│   │   ├── github_pr.py # Collect pull requests
│   │   └── github.py # All GitHub related utilities
│   ├── issue_events_anaylsis.py # Analyze the issue events
│   ├── issues_summary_extraction.py # Extract the summary of issues
│   ├── process_non_bot.py # Process the non-bot issues 
│   ├── query_reject_reason.py # Query the reject reason
│   ├── role_determination.py # Determine the role of the issue to Provider and Seeker
│   ├── rq1
│   │   └── count_taxonomy.py # Count the taxonomy of issues
│   ├── rq2
│   │   └── count_taxo_distribution.py # Count the distribution of taxonomy
│   ├── rq3
│   │   ├── reopen_analysis.py # Analyze the reopen of issues
│   │   └── rs_distri_evolution.py # Analyze the evolution of remediation strategies
│   ├── rq4
│   │   └── map_issue_with_advisory.py # Map the issue with advisory
│   ├── sort_issue_by_date.py # Sort the issue by date
│   ├── statistics.py # Statistics utilities
│   ├── time_reversion_analysis.py # Analyze the time reversion
│   └── tmp_seperate_column.py # A tempoary script to seperate the column
└── utils
    ├── github_utils.py # GitHub utilities
    ├── graphql.py # GraphQL utilities
    └── miscellaneous.py # Miscellaneous utilities
```
