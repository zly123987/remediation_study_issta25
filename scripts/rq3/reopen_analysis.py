import csv
import json

from tqdm import tqdm



def add_link_2_csv(c):
    coll = c['remediation']['github_issues_non_bots']
    content = []
    with open('data_processed/re-discussion/rediscussion.csv', 'r') as f:
        for line in csv.reader(f):
            content.append(line)
    with (open('data_processed/re-discussion/re-discussion.csv', 'w') as f):
        writer = csv.writer(f)
        for line in content:
            if line[0] == 'id':
                line.append('link')
                line.append('Bot or Not Bot')
                writer.writerow(line)
                continue


            doc = coll.find_one({'id': int(line[0])})
            link = doc['html_url']
            line.append(link)
            last_comment = doc['comments_data'][-1]
            if last_comment['user']['type'] == 'Bot' or 'bot' in last_comment['user']['login'].lower():
                line.append('Bot')
            else:
                line.append('Not Bot')

            writer.writerow(line)

def analyze_rediscussion(c):
    coll = c['remediation']['github_issues_non_bots']
    content = []
    behaviors = []
    reasons = []
    outcomtes = []
    with open('data_processed/re-discussion/rediscussion.csv', 'r') as f:
        for line in csv.reader(f):
            content.append(line)
    visited = set()
    with (open('data_processed/re-discussion/re-discussion.csv', 'r') as f):
        for line in csv.reader(f):
            if line[0] == 'id':
                continue
            if line[1] != '':
                behaviors.append(line[1])
            if line[2] != '':
                reasons.append(line[2])
            if line[3] != '':
                outcomtes.append(line[3])

            visited.add(int(line[0]))

    with (open('data_processed/re-discussion/re-discussion.csv', 'r') as f):
        for line in csv.reader(f):
            if line[0] == 'id':
                continue
            if line[1]!='':
                behaviors.append(line[1])
            if line[2]!='':
                reasons.append(line[2])
            if line[3]!='':
                outcomtes.append(line[3])

            visited.add(int(line[0]))

        for line in tqdm(content):
            if line[0] == 'id':
                continue
            if int(line[0]) in visited:
                continue

            doc = coll.find_one({'id': int(line[0])})
            link = doc['html_url']
            line.append(link)
            last_comment = doc['comments_data'][-1]
            if last_comment['user']['type'] == 'Bot' or 'bot' in last_comment['user']['login'].lower():
                line.append('Bot')
                continue
            else:
                line.append('Not Bot')
            events = doc.get('events', [])
            comments = doc.get('comments_data', [])
            for event in events:
                if event['event'] == 'closed':
                    close_date = event['created_at']
                    break
            if close_date:
                comments_in_between = []
                for comment in comments:
                    if comment['created_at'] > close_date:
                        comments_in_between.append(comment['body'][:200].replace('\n', ' ').replace('\r', ' ').replace('\t', ' '))
            comments_in_between = comments_in_between[-10:]
            behaviors = set(behaviors)
            reasons = set(reasons)
            outcomtes = set(outcomtes)
            behaviors = list(behaviors)
            reasons = list(reasons)
            outcomtes = list(outcomtes)
            behaviors.sort()
            reasons.sort()
            outcomtes.sort()
            print(f"ID: {line[0]}")
            print(f"Title: {doc['title']}")
            print(f"Body: {doc['body']}")
            print(f"Comments: {comments_in_between}")

