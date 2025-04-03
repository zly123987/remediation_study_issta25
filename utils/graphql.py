import requests
import json
import sys
import re
def query_github_issue(owner, repo, issue_number, auth_token):
    """Queries a GitHub issue using the GitHub GraphQL API."""
    url = 'https://api.github.com/graphql'
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # GraphQL query
    query = """
    query($owner: String!, $repo: String!, $issue_number: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $issue_number) {
          title
          body
          createdAt
          author {
            login
          }
          comments(first: 10) {
              totalCount
              nodes {
                body
                url
                createdAt
                author {
                  login
                }
              }
            }
        }
      }
    }
    """

    variables = {
        'owner': owner,
        'repo': repo,
        'issue_number': issue_number
    }

    # Sending the request
    response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})
    # Sending the request
    response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})
    if response.status_code == 200:
        comments_data = response.json()['data']['repository']['issue']['comments']['nodes']
        analyze_comments(comments_data)
        print("Query failed to run by returning code of {}. {}".format(response.status_code, query))
def analyze_comments(comments):
    """Analyzes comments for links to PRs and commits."""
    pr_link_pattern = re.compile(r'https://github\.com/' + re.escape(owner) + '/' + re.escape(repo) + '/pull/\d+')
    commit_link_pattern = re.compile(r'https://github\.com/' + re.escape(owner) + '/' + re.escape(repo) + '/commit/[0-9a-f]{40}')

    for comment in comments:
        print("Comment by:", comment['author']['login'])
        print("URL:", comment['url'])
        # Search for PR and commit links
        pr_links = pr_link_pattern.findall(comment['body'])
        commit_links = commit_link_pattern.findall(comment['body'])
        if pr_links or commit_links:
            print("Found PR Links:", pr_links)
            print("Found Commit Links:", commit_links)
        else:
            print("No PR or commit links found.")
        print("-----")

def fetch_issue_events(owner, repo, issue_number, auth_token):
    """Fetches events associated with a GitHub issue."""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/events"
    headers = {
        'Authorization': f'token {auth_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        events = response.json()
        print(json.dumps(events, indent=4))
    else:
        print(f"Failed to fetch events: {response.status_code}\n{response.text}")

