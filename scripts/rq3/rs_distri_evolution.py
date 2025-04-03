import csv
import json
import os
from collections import defaultdict

from tqdm import tqdm


def reformat_all_in_one(c):
    coll = c['remediation']['github_issues_non_bots']
    with open('data_processed/all_in_one.csv', 'r') as f:
        data = []
        for line in tqdm(csv.reader(f)):
            if line[0] == 'id':
                continue
            id = int(line[0])
            doc = coll.find_one({'id': id})
            events = doc.get('events', [])
            for event in events:
                if event['event'] == 'closed':
                    close_date = event['created_at']
                    break
            if close_date:
                last_comment_date = doc['comments_data'][-1]['updated_at']
                if last_comment_date > close_date:
                    bot = True
                    comments = doc['comments_data']
                    for comment in comments:
                        if comment['created_at'] > close_date:
                            if comment['user']['type'] != 'Bot' and 'bot' not in comment['user']['login'].lower():
                                bot = False
                    line.append(bot)
                    data.append(line)
                else:
                    line.append('na')
                    data.append(line)


            else:
                line.append('na')
                data.append(line)
            # for major, sub in taxonomy.items():
            #     if rs == major or rs in sub:
            #         line.append(major)
            # data.append(line)
    with open('data_processed/all_in_one.csv', 'w') as f:
        writer = csv.writer(f)
        for line in data:
            writer.writerow(line)
    exit()

def get_evolution_data_major_cate():
    with open('data_processed/all_in_one.csv', 'r') as f:
        dates = {a: [] for a in range(0,2000)}
        for line in csv.reader(f):
            if line[0] == 'id':
                continue
            duration = int(line[6])
            if duration in dates:
                dates[duration].append(line[2])
    with open('data_processed/taxonomy_flatten.json', 'r') as f:
        taxonomy = json.load(f)



    data = {}
    majors = []
    for day, rs in dates.items():
        data[day] = defaultdict(int)
        for major, sub in taxonomy.items():
            data[day][major] = 0
            for r in rs:
                if r == major or r in sub:
                    data[day][major] +=1
    os.makedirs('data_processed/rq3/', exist_ok=True)
    majors = [k for k,v in data[0].items()]
    smooth_gradient = 7
    tmp = {}
    for day, rs in data.items():

        if day <=180:
            if day % smooth_gradient == 0:
                tmp[int(day / smooth_gradient)]={key: 0 for key in majors}

            for major, count in rs.items():
                tmp[int(day/smooth_gradient)][major] += count
        else:
            for major, count in rs.items():
                tmp[int(180/smooth_gradient)][major] += count
    with open('data_processed/rq3/rs_evolution.csv', 'w') as f:
        f.write('day,'+",".join(majors)+'\n')
        for day, rs in tmp.items():
            f.write(str(day)+','+",".join([str(v) for k,v in rs.items()])+'\n')

