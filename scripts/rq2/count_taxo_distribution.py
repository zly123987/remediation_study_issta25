import json



def check_in_taxo_major(key, major, taxonomy):
    if key in str(taxonomy[major]):
        return True
    return False
def calculate_quadrant_distribution_of_taxo():

    with open('data_processed/taxonomy_flatten.json', 'r') as f:
        taxonomy = json.load(f)
    major_counts = {key: 0 for key in taxonomy.keys()}
    with open('data_processed/category_counts.csv', 'r') as f:
        category_counts = {}
        for line in f:
            category, count = line.split(',')
            category_counts[category] = int(count)
    for major in major_counts.keys():
        for category in category_counts.keys():
            if category in taxonomy[major] or category == major:
                major_counts[major] += category_counts[category]

    for major, count in major_counts.items():
        print(f"{major},{count}")
