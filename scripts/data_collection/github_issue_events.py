import csv

import requests
import json

from tqdm import tqdm

from config import github_token, github_secondary_token, github_forth_token, github_third_token
def fetch_issue_events(owner, repo, issue_number, tokens):
    """Fetches all events associated with a GitHub issue, handling pagination and token rotation."""
    token_index = 0  # Start with the first token
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/events"

    all_events = []

    while url:
        headers = {
            'Authorization': f'Bearer {tokens[token_index]}',
            'Accept': 'application/vnd.github.v3+json'
        }
        response = requests.get(url, headers=headers)

        # Check if we need to switch tokens due to rate limiting
        if response.status_code == 403 and 'rate limit exceeded' in response.text.lower():
            token_index += 1
            if token_index >= len(tokens):
                print("All tokens are rate limited. Try again later.")
                break
            continue  # Retry with a new token

        if response.status_code == 200:
            events = response.json()
            all_events.extend(events)
            # Check the Link header for a next page URL
            link_header = response.headers.get('Link', '')
            next_link = [link.split(';')[0].strip('<> ').split(',')[0] for link in link_header.split(',') if 'rel="next"' in link]
            url = next_link[0] if next_link else None
        else:
            print(f"Failed to fetch events: {response.status_code}\n{response.text}")
            break

    return all_events


def fetch_events_for_all_issues(c):
    target_ids = []
    with open('data_collection/target_issue_ids.csv', 'r') as f:
        for line in csv.reader(f):
            target_ids.append(int(line[0]))
    coll = c['remediation']['github_issues_non_bots']
    for id in tqdm(target_ids, 'Fetching events for issues'):
        doc = coll.find_one({'id': id})
        if 'events' in doc:
            continue

        html_url = doc['html_url']

        _, _, _, owner, repo, _, issue_number = html_url.split('/')
        tokens = [github_token, github_secondary_token, github_third_token, github_forth_token]
        events = fetch_issue_events(owner, repo, issue_number, tokens)
        coll.update_one({'id': id}, {'$set': {'events': events}})