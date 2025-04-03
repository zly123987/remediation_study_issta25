import csv
from datetime import datetime

from tqdm import tqdm

from utils.github_utils import get_repo_stars


def _github_issues(client, issue_limit=None, db_name='remediation', collection_name='github_issues_non_bots'):
    # Connect to MongoDB (Assuming MongoDB is running on the default host and port)

    # filter cve related issues
    cve_issues_coll = client['remediation']['github_cve_issues']
    cve_related_ids = [doc['id'] for doc in cve_issues_coll.find()]

    # Access the specified database and collection
    db = client[db_name]
    collection = db[collection_name]
    summary_coll = db['github_issues_non_bot_summaries']
    target_ids = [doc['id'] for doc in summary_coll.find({}, {'id': 1})]



    ids = list(filter_by_star(client, 10000, target_ids))
    print(len(ids), 'issues are over stars')
    ids = filter_by_date(client, ids)
    ids = filter_by_no_accept(ids, collection)
    #
    issues = list(collection.find({'id': {'$in': ids}}).sort({'_id': -1}).batch_size(30))
    # filter_by_solo_issues(issues)




    # print('Processing {} issues'.format(len(issues)))
    processed_count = 0
    for issue in tqdm(issues, desc='Processing Issues'):
        if issue_limit and processed_count >= issue_limit:
            break
        id = issue['id']
        title = issue['title']
        comments = [comment['body'] for comment in issue['comments_data']]
        analyze_acceptance(id, title, comments, collection)
        processed_count += 1

def acceptance_github_issues(client=None, db_name='remediation', collection_name='github_issues_non_bots'):
    # Connect to MongoDB (Assuming MongoDB is running on the default host and port)


    # Access the specified database and collection
    db = client[db_name]
    collection = db[collection_name]
    summary_coll = db['github_issues_non_bot_summaries']
    target_ids = set()
    with open('data_collection/target_issue_ids.csv', 'r') as f:
        for line in csv.reader(f):
            target_ids.add(int(line[0]))
    issues = []
    for each in collection.find({'id': {'$in': list(target_ids)}}).sort({'_id': -1}).batch_size(30):
        if 'accept' not in each:
            issues.append(each)
    processed_count = 0
    for issue in tqdm(issues, desc='Processing Issues'):
        id = issue['id']
        title = issue['title']
        comments = [comment['body'] for comment in issue['comments_data']]
        analyze_acceptance(id, title, comments, collection)
        processed_count += 1

def summerize_github_issues(client, issue_limit=None, db_name='remediation', collection_name='github_issues_non_bots'):
    # Connect to MongoDB (Assuming MongoDB is running on the default host and port)
    summary_collection = client['remediation']['github_issues_non_bot_summaries']
    summary_collection.create_index('id', unique=True)

    # filter cve related issues
    cve_issues_coll = client['remediation']['github_cve_issues']
    cve_related_ids = [doc['id'] for doc in cve_issues_coll.find()]

    # Access the specified database and collection
    db = client[db_name]
    collection = db[collection_name]
    summary_coll = db['github_issues_non_bot_summaries']
    processed_ids = [doc['id'] for doc in summary_coll.find({}, {'id': 1})]

    ids = list(filter_by_star(client, 10000))
    print(len(ids), 'issues are over stars')
    # Query to select non-processed ids

    # ids = filter_by_dependency_tag(client, ids)
    # print(len(ids), 'issues are dep labeled')

    ids = filter_by_date(client, ids)
    issues = list(collection.find({'id': {'$nin': processed_ids, '$in': ids}}).sort({'_id': -1}).batch_size(30))





    # print('Processing {} issues'.format(len(issues)))
    processed_count = 0
    for issue in tqdm(issues, desc='Processing Issues'):
        if issue_limit and processed_count >= issue_limit:
            break
        id = issue['id']
        title = issue['title']
        comments = [comment['body'] for comment in issue['comments_data']]
        summarize_issue(id, title, comments, summary_collection)
        processed_count += 1





def summarize_issue(id, title, comments, collection):

    summaries = []
    # Construct a single text block from title and comments
    full_text = 'title: '+ title + " conversations: " + " ".join(comments)
    print(full_text)


def filter_by_star(client, star_threshold=1000, previous_ids=None):
    db = client['remediation']
    collection = db['github_issues_non_bots']
    star_collection = db['github_repo_stars']
    star_collection.create_index('repo', unique=True)
    ids = set()
    count = 0
    if previous_ids:
    # filter by star over threshold
        for doc in collection.find({'id': {'$in': previous_ids}, 'stars':{'$gt': star_threshold}}).sort({'_id': 1}).batch_size(30):
            id = doc['id']
            count+=1
            url = doc['html_url']
            repo = url.split('github.com/')[1].split('/issues/')[0]
            star_doc = star_collection.find_one({'repo': repo})
            if star_doc:
                star_count = star_doc['stars']
            else:
                star_count = get_repo_stars(repo)
                print(f"Stars for {repo}: {star_count}", 'ids size', len(ids), 'All', count)
                star_collection.update_one({'repo': repo}, {'$set': {'stars': star_count}}, upsert=True)
            collection.update_one({'id': id}, {'$set': {'stars': star_count}})
            print(count,  '\r', end='')
            # if star_count >= star_threshold:
            ids.add(doc['id'])

        return ids
    else:
        for doc in collection.find({'stars':{'$gt': star_threshold}}).sort({'_id': 1}).batch_size(30):
            id = doc['id']
            count+=1
            url = doc['html_url']
            repo = url.split('github.com/')[1].split('/issues/')[0]
            star_doc = star_collection.find_one({'repo': repo})
            if star_doc:
                star_count = star_doc['stars']
            else:
                star_count = get_repo_stars(repo)
                print(f"Stars for {repo}: {star_count}", 'ids size', len(ids), 'All', count)
                star_collection.update_one({'repo': repo}, {'$set': {'stars': star_count}}, upsert=True)
            collection.update_one({'id': id}, {'$set': {'stars': star_count}})
            print(count,  '\r', end='')
            # if star_count >= star_threshold:
            ids.add(doc['id'])

        return ids

def filter_by_dependency_tag(client, over_stars_ids):
    db = client['remediation']
    collection = db['github_issues_non_bots']
    return_ids = []
    count =0
    print()
    for doc in collection.find({'id':{'$in': over_stars_ids}}):
        count+=1
        labels = [each['name'] for each in doc['labels']]
        if 'dependency' in labels or 'dependencies' in labels or  'dep' in labels:
            return_ids.append(doc['id'])
        print(count, '\r', end='')
    return return_ids


def filter_by_date(client, previous_ids):
    db = client['remediation']
    collection = db['github_issues_non_bots']
    return_ids = []
    count = 0
    print()
    for doc in collection.find({'id':{'$in': previous_ids}}):
        count += 1
        date = doc['created_at']
        if date>= datetime(2022, 1, 1):
            return_ids.append(doc['id'])
        print(count, '\r', end='')
    return return_ids

def filter_by_solo_issues(issues):
    # At least one other user has joind the discussion
    ret = set()
    for issue in issues:
        issue_creator = issue['user']['login']
        comments_users =  [comment['user']['login'] for comment in issue['comments_data']]
        for each_user in comments_users:
            if each_user!=issue_creator:
                ret.add(issue['id'])
    return ret

def filter_by_no_accept(ids, collection):
    for doc in collection.find({'id':{'$in': ids}}):
        if 'accept' in doc:
            ids.remove(doc['id'])

    return ids