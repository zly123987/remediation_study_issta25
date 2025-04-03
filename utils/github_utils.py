import requests
import json
import time
from config import github_token, github_secondary_token, github_third_token

# Initialize the token index
token_index = 0
tokens = [github_third_token, github_secondary_token, github_token]


def get_rate_limit(token):
    """
    Check the remaining rate limit for the given GitHub token.
    """
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    try:
        response = requests.get('https://api.github.com/rate_limit', headers=headers)
    except:
        print("Retrying...")
        time.sleep(10)
        return 0, 0

    if response.status_code == 200:
        rate_limit_data = response.json()

        print(f"Token index, {token_index}, Rate limit remaining: {rate_limit_data['rate']['remaining']}")
        return rate_limit_data['rate']['remaining'], rate_limit_data['rate']['reset']
    else:
        return 0, 0





def get_repo_stars(repo):
    """
    Fetches the star count of a given GitHub repository using the GitHub API.
    Handles token switching when rate limits are approached.
    """
    global token_index

    while True:
        token = tokens[token_index]
        remaining, reset = get_rate_limit(token)

        if remaining > 0:
            url = f"https://api.github.com/repos/{repo}"
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }

            try:
                response = requests.get(url, headers=headers)
            except:
                # print('Retrying')
                return -1

            if response.status_code == 200:
                repo_data = response.json()
                return repo_data['stargazers_count']
            else:
                print(f"Failed to fetch repository data: {response.status_code} - {response.text}")
                return -1
        else:
            # Wait for rate limit reset if all tokens are exhausted
            if token_index == len(tokens) - 1:
                # wait_time = reset - time.time() + 10  # Adding 10 seconds margin
                # print(f"Rate limit exceeded. Waiting for {int(wait_time)} seconds.")
                # time.sleep(max(wait_time, 0))
                time.sleep(10)
                token_index = 0  # Reset token index after wait
            else:
                # Switch to the next token
                token_index += 1

