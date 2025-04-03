import os


def get_commits_from_issues():
    target_ids = []
    with open('data_collection/target_issue_ids.csv', 'r') as f:
        for line in f:
            target_ids.append(int(line))
    issue_coll = c['remediation']['github_issues_non_bots']
    for id in target_ids:
        doc = issue_coll.find_one({'id': id})


def clone_repos(c):
    star_coll = c['remediation']['github_repo_stars']
    # Clone all repos from the list
    os.makedirs('repos', exist_ok=True)
    os.chdir('repos')
    for doc in star_coll.find({'stars':{'$gt':10000}}):
        name = doc['repo']
        url = f'git@github.com:{name}.git'
        os.system('git clone ' + url)