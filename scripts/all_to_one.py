import csv

target_ids = []

accept = {}
with open('data_processed/acceptance.csv') as f:
    for line in csv.reader(f):
        if line[0]=='id':
            continue
        accept[int(line[0])] = line[1]
cve_strategies = {}
with open('data_processed/cve_strategies.csv') as f:
    for line in csv.reader(f):
        cve_strategies[int(line[0])] = line[2]

non_cve_strategies = {}
with open('data_processed/non_cve_strategies.csv') as f:
    for line in csv.reader(f):
        non_cve_strategies[int(line[0])] = line[2]

role = {}
with open('data_processed/roles.csv') as f:
    for line in csv.reader(f):
        role[int(line[0])] = line[1]

reject = {}
with open('data_processed/rejected_reasons/rejected fix final.csv') as f:
    for line in csv.reader(f):
        reject[int(line[0])] = line[2]
with open('data_collection/target_issue_ids.csv', 'r') as f:
    for line in csv.reader(f):
        target_ids.append(int(line[0]))

event = {}
with open('data_processed/close_event_analysis.csv') as f:
    for line in csv.reader(f):
        event[int(line[0])] = [line[1], line[2], line[3], line[4], line[5], line[6]]
with open('data_processed/all_in_one.csv', 'w') as fw:
    writer = csv.writer(fw)
    writer.writerow(['id', 'accept', 'strategies', 'is_cve', 'role', 'reject_reason', 'close_duration', 'discussion_duration', 'category', 'created_at', 'close_date', 'last_comment_date'])
    for id in target_ids:
        if id in cve_strategies:
            writer.writerow([id, accept.get(id, ''), cve_strategies[id], True, role[id], reject.get(id, 'N/A'), event[id][0], event[id][1], event[id][2], event[id][3], event[id][4], event[id][5]])
        elif id in non_cve_strategies:
            # print(id in accept, id in non_cve_strategies, id in role)
            writer.writerow([id, accept.get(id, ''), non_cve_strategies[id], False, role[id], reject.get(id, 'N/A'), event[id][0], event[id][1], event[id][2], event[id][3], event[id][4], event[id][5]])