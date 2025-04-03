import os

import pymongo as pymongo
import requests
import json
import time

from config import github_token, github_secondary_token, mongo_host, mongo_port, github_third_token, github_forth_token

def get_advisories(token, after_date, page=1):
    url = 'https://api.github.com/advisories'
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {token}',
    }
    params = {
        'type': 'reviewed',
        'per_page': 100,  # Max allowed per GitHub's documentation
        'page': page,
        'sort': 'published',  # Sort by the published date
        'direction': 'asc',  # From oldest to newest
        'published': f'>{after_date}'  # Fetch advisories published after this date
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response
    else:
        return None


def handle_rate_limit(response_headers):
    remaining = int(response_headers.get('X-RateLimit-Remaining', 0))
    reset_time = int(response_headers.get('X-RateLimit-Reset', 0))
    return remaining, reset_time


def save_advisories_to_file(advisories, file_index):
    file_name = f"data_collection/github_advisory/advisories_{file_index}.json"
    with open(file_name, 'w') as file:
        json.dump(advisories, file)
    print(f"Saved {len(advisories)} advisories to {file_name}")


def save_last_date(last_date):
    with open('last_date.txt', 'w') as file:
        file.write(last_date)
    print(f"Saved last date {last_date}")

def crawl_github_advisories():
    tokens = [github_third_token, github_secondary_token, github_third_token]  # Replace with your actual GitHub API tokens
    token_index = 0
    all_advisories = []
    if os.path.exists('data_collection/github_advisory/last_page.txt'):
        with open('data_collection/github_advisory/last_page.txt', 'r') as f:
            page = int(f.read())
    else:
        page = 1
    file_index = page
    if os.path.exists('data_collection/github_advisory/last_date.txt'):
        with open('data_collection/github_advisory/last_date.txt', 'r') as f:
            last_date = f.read()
    else:
        last_date = '2000-01-01T00:00:00Z'

    continue_crawl = True

    while continue_crawl:
        token =github_forth_token#tokens[token_index]
        result = get_advisories(token, last_date, page)

        if result:
            all_advisories.extend(result.json())
            last_date = all_advisories[-1]['published_at']
            if len(all_advisories) >= 100:
                save_advisories_to_file(all_advisories[:100], file_index)
                all_advisories = all_advisories[100:]
                file_index += 1

            page += 1
            with open('data_collection/github_advisory/last_page.txt', 'w') as f:   # Save the last page number
                f.write(str(page))

            with open('data_collection/github_advisory/last_date.txt', 'w') as f:   # Save the last date
                f.write(last_date)

            print(f"Fetched page {page} using token {token}")

            # Handle rate limits
            remaining, reset_time = handle_rate_limit(result.headers)
            if remaining < 10:  # If less than 10 requests left, switch token
                print(f"Switching token due to rate limit. Remaining: {remaining}")
                token_index = (token_index + 1) % len(tokens)
                if token_index == 0:  # If all tokens are used, sleep till reset
                    sleep_time = reset_time - int(time.time()) + 10  # Adding 10 seconds buffer
                    print(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
                    time.sleep(sleep_time)

        else:
            print("Failed to fetch data or finished crawling all data.")
            if all_advisories:  # Save any remaining advisories not yet written to file
                save_advisories_to_file(all_advisories, file_index)
            continue_crawl = False


def populate_github_advisory_to_mongodb():
    c = pymongo.MongoClient(mongo_host, mongo_port)
    db = c['remediation']
    collection = db['github_advisories']

    advisories = []
    for file in os.listdir('data_collection/github_advisory/'):
        if file.startswith('advisories_'):
            with open(f'data_collection/github_advisory/{file}', 'r') as f:
                advisories.extend(json.load(f))
    dup = 0
    for advisory in advisories:
        existing = collection.find_one({'id': advisory['ghsa_id']})
        if existing:
            dup += 1
            print(dup, 'Advisory already exists in MongoDB. Skipping...')
            continue
        collection.update_one({'id': advisory['ghsa_id']}, {'$set': advisory}, upsert=True)

    print(f"Added {len(advisories)} advisories to MongoDB")

