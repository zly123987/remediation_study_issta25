import csv
import os.path
from datetime import datetime

from tqdm import tqdm


def calculate_days_difference(date_str1, date_str2):
    # Parsing the datetime strings
    if isinstance(date_str1, str):
        datetime1 = datetime.strptime(date_str1, "%Y-%m-%dT%H:%M:%SZ")
    else:
        datetime1 = date_str1
    if isinstance(date_str2, str):
        datetime2 = datetime.strptime(date_str2, "%Y-%m-%dT%H:%M:%SZ")
    else:
        datetime2 = date_str2

    # Calculating the difference in days
    day_difference = abs((datetime2 - datetime1).days)
    return day_difference

def count_contributor(events, comments, repo, c):
    contributor_coll = c['remediation']['github_contributors']
    participants = []
    for comment in comments:
        if comment and comment['user']:
            participants.append(comment['user']['login'])
    for event in events:
        if event and event['actor']:
            participants.append(event['actor']['login'])
    doc = contributor_coll.find_one({'owner_repo': repo})
    if doc:
        contributors = doc['contributors']
        intersection = set(participants).intersection(contributors)
        return intersection
    else:
        return set()

def analyze_close_event(c):
    coll = c['remediation']['github_issues_non_bots']
    target_ids = []
    with open('data_collection/target_issue_ids.csv', 'r') as f:
        for line in csv.reader(f):
            if line:
                target_ids.append(int(line[0]))
    processed_ids = set()
    if os.path.exists('data_processed/event/close_event_analysis.csv'):
        with open('data_processed/event/close_event_analysis.csv', 'r') as f:
            processed_ids = [int(line.split(',')[0]) for line in f]

    for id in tqdm(target_ids, 'Analyzing close events'):
        if id in processed_ids:
            continue
        doc = coll.find_one({'id': id})
        events = doc.get('events', [])
        comments = doc.get('comments_data', [])

        repo = doc['url'].replace('https://api.github.com/repos/', '').split('/issues')[0]
        for event in events:
            if event['event'] == 'closed':
                close_date = event['created_at']
                break
        if close_date:
            last_comment_date = comments[-1]['updated_at']
            created_at = doc['created_at']
            for event in events:
                if event['event'] == 'reopened':
                    created_at = event['created_at']
                    break
            contributors = count_contributor(events, doc['comments_data'], repo, c)
            close_duration = calculate_days_difference(created_at, close_date)
            fix_duration = calculate_days_difference(created_at, last_comment_date)
            if last_comment_date > close_date:
                category = 'comment_after_close'
                discussion_duration = calculate_days_difference(close_date, last_comment_date)
            else:
                category = 'closed_without_comment'
                discussion_duration = 0
            with open('data_processed/event/close_event_analysis.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow([id, close_duration, discussion_duration, category, created_at, close_date, last_comment_date, len(contributors)])
        else:
            with open('data_processed/event/close_event_analysis.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow([id, close_date])
