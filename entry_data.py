import pymongo
from scripts.data_collection.github import get_github_issues, process_github_issues, save_contributors, save_timeline
from scripts.data_collection.github_issue_events import fetch_events_for_all_issues
from scripts.data_collection.github_pr import get_github_pr
from config import mongo_host, mongo_port
from scripts.data_collection.github_advisory import crawl_github_advisories, populate_github_advisory_to_mongodb
from scripts.process_non_bot import acceptance_github_issues
from scripts.statistics import count_accepeted_rejected



# Fetch GitHub PRs
get_github_pr()

# Fetch GitHub issues
get_github_issues()

# Connect to MongoDB
c = pymongo.MongoClient(mongo_host, mongo_port)

# Analyze the acceptance of GitHub issues by printing them to the console for manual labeling
acceptance_github_issues(c)

# Apply filter to crawled GitHub issues
process_github_issues(c)

# Count the number of accepted and rejected issues
count_accepeted_rejected(c)

# Fetch events for all issues via GitHub API
fetch_events_for_all_issues(c)

# Save timeline data from CSV to mongodb
save_timeline(c)

# Save contributors data from CSV to mongodb
save_contributors(c)

# Crawl the vulnerability advisories from GitHub
crawl_github_advisories()

# Store the vulnerability data in MongoDB
populate_github_advisory_to_mongodb()

c.close()





