import os
import pandas as pd
import requests
import time
import json
from tqdm import tqdm
from config import github_token, github_secondary_token


def make_request(url, headers, params=None):
    """ Helper function to make API requests and handle rate limits, with token switching. """
    while True:
        response = requests.get(url, headers=headers, params=params)
        rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))

        if response.status_code == 200:
            # print(f"Current Rate Limit Remaining: {rate_limit_remaining}")
            return response
        elif response.status_code == 403 and rate_limit_remaining < 10:
            # Check if the secondary token is already in use, switch back if not enough limit
            if github_token in headers['Authorization']:
                headers['Authorization'] = headers['Authorization'].replace(github_token, github_secondary_token)
            elif github_secondary_token in headers['Authorization']:
                headers['Authorization'] = headers['Authorization'].replace(github_secondary_token, github_token)

            print("Switched tokens due to rate limit. Retrying...")
            sleep_time = int(response.headers.get('X-RateLimit-Reset', 0)) - int(time.time()) + 10
            time.sleep(sleep_time)
            continue
        else:
            print(f"Failed to retrieve data: {response.status_code}, Message: {response.text}")
            return None

def check_rate_limits(headers):
    """ Check and display GitHub API rate limits using the rate limit endpoint. """
    rate_limit_url = 'https://api.github.com/rate_limit'
    response = requests.get(rate_limit_url, headers=headers)
    if response.status_code == 200:
        rate_limits = response.json()
        core_limits = rate_limits.get('resources', {}).get('core', {})
        print(f"Core Limit: {core_limits.get('limit')}, Remaining: {core_limits.get('remaining')}, Resets in: {core_limits.get('reset') - int(time.time())} seconds")
    else:
        print("Failed to fetch rate limits.")

def get_github_pr(per_page=100):
    # GitHub base URL for search pr
    url = 'https://api.github.com/search/issues'

    # Headers to include in the request (Add your GitHub token here)
    headers = {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'Authorization': 'Bearer '+github_token  # Replace YOUR_PERSONAL_ACCESS_TOKEN with your actual token
    }
    initial_query= 'security OR vulnerability AND fix in:title,body type:pr is:closed  comments:>=3 '
    current_page = int(open('data_collection/github_pr/current_page.txt').read())
    # Query parameters for the API
    params = {
        'q': initial_query,
        'sort': 'created',  # Sort by creation date
        'order': 'asc',  # Order ascending
        'per_page': per_page,
        'page': 1
    }

    file_index = current_page+1

    total_saved = 0
    if os.path.exists(f'data_collection/github_pr/last_creation_date.txt'):
        last_creation_date = open('data_collection/github_pr/last_creation_date.txt').read()
    else:
        last_creation_date = None


    while True:
        if last_creation_date:
            params['q'] = f'{initial_query} created:>{last_creation_date}'
        response = make_request(url, headers, params)
        if response is None:
            break  # Stop if there was an error

        data = response.json()
        pr = data['items']

        # Process each issue
        for issue in tqdm(pr, desc=f"Processing Page {file_index}"):
            issue['comments_data'] = []
            comments_url = issue['comments_url']
            comments_response = make_request(comments_url, headers)
            if comments_response:
                issue['comments_data'] = comments_response.json()

            # Check for linked PR, if any
            if 'pull_request' in issue:
                pr_url = issue['pull_request']['url']
                pr_response = make_request(pr_url, headers)
                if pr_response:
                    issue['pull_request_details'] = pr_response.json()

        # Save the data to a file
        os.makedirs('data_collection/github_pr', exist_ok=True)
        filename = f'data_collection/github_pr/github_pr_page_{file_index}.json'
        with open(filename, 'w') as file:
            json.dump(pr, file, indent=4)

        total_saved += len(pr)
        print(
            f"Data saved to {filename}. Total records saved: {total_saved}. Last Create Date: {last_creation_date}" )
        last_creation_date = pr[-1]['created_at']  # Taking only the date part

        check_rate_limits(headers)



        # Note down the last page and creation date
        with open('data_collection/github_pr/current_page.txt', 'w') as file:
            file.write(str(file_index))
        with open('data_collection/github_pr/last_creation_date.txt', 'w') as file:
            file.write(last_creation_date)

        file_index += 1
        # Check if there is a next page, otherwise break the loop
        if 'next' in response.links:
            params['page'] = 1
        else:
            break
def save_or_update_data_to_mongodb(dataframe, c):

    # Select the database and collection
    collection = c['remediation']['github_pr_non_bots']

    # Convert DataFrame to a list of dictionaries suitable for insertion into MongoDB
    records = dataframe.to_dict('records')

    # Iterate through each record and update/insert into MongoDB
    for record in records:
        # Assuming 'id' is your unique identifier in the record and the MongoDB document
        record_id = record['id']
        # Update the record with the new values from DataFrame, or insert it if it does not exist
        collection.update_one(
            {'id': record_id},  # Filter by unique identifier
            {'$set': record},  # Update operation
            upsert=True  # If the record does not exist, insert it
        )


def process_github_pr(c):
    def filter_out_bots(df):
        # Assuming there's a 'user' column with 'login' as a key in user information
        # Adjust the column/key names based on your actual data structure
        return df[~df['user'].apply(lambda x: x['login'].endswith('bot') or '[bot]' in x['login'])]

    def filter_by_creation_date(df, start_date, end_date):
        return df[(df['created_at'] >= start_date) & (df['created_at'] <= end_date)]

    def filter_by_label(df, label):
        return df[df['labels'].apply(lambda labels: label in [l['name'] for l in labels])]

    def apply_filters(df):
        df = filter_out_bots(df)
        # Add more filters here as needed
        # Example: df = filter_by_creation_date(df, '2020-01-01', '2020-12-31')
        # Example: df = filter_by_label(df, 'security')
        return df


    # Load your data into a DataFrame
    def load_data(filepath):
        return pd.read_json(filepath)



    coll = c['remediation']['github_pr_non_bots']
    for filename in os.listdir('data_collection/github_pr'):
        if filename.endswith('.json'):
            df = load_data(f'data_collection/github_pr/{filename}')
            filtered_df = apply_filters(df)
            save_or_update_data_to_mongodb(filtered_df, c)
