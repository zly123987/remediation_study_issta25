import json

def count_tax():
    def find_and_return_node(node_name, hierarchy):
        if isinstance(hierarchy, dict):
            if node_name in hierarchy:
                return hierarchy[node_name]
            for key, value in hierarchy.items():
                result = find_and_return_node(node_name, value)
                if result is not None:
                    return result
        elif isinstance(hierarchy, list):
            for item in hierarchy:
                result = find_and_return_node(node_name, item)
                if result is not None:
                    return result

    def sum_node(node, counts):
        children = find_and_return_node(node, hierarchy)
        if isinstance(children, dict):
            if len(children) == 0:
                return counts.get(node, 0)
            return sum(sum_node(child, counts) for child in children)+counts.get(node, 0)
        elif isinstance(children, list):
            if children == []:
                return counts.get(node, 0)
            return sum(counts.get(child, 0) for child in children) +counts.get(node, 0)
        else:
            return counts[node]+counts.get(node, 0)
    hierarchy = json.load(open("data_processed/taxonomy.json"))

    # Load the counts from a CSV file
    csv_file = 'data_processed/taxonomy_count.csv'  # Update this with the path to your CSV file
    counts = {}
    with open(csv_file, 'r') as f:
        for line in f:
            if 'count' in line:
                continue
            category, count = line.strip().split(',')
            counts[category] = int(count)

    # Initialize a dictionary to hold the aggregated counts
    aggregated_counts = {key: sum_node(key, counts) for key in counts.keys()}


    # Display the aggregated counts
    for category, count in aggregated_counts.items():
        print(f"{category},{count}")