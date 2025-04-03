import pymongo
from scripts.categorize_rejected_fix import categorize_rejcted_fixes
from scripts.issue_events_anaylsis import analyze_close_event
from scripts.issues_summary_extraction import extract_and_save_cve_issues, print_cve_issue, summarize_for_cve
from scripts.statistics import count_accepeted_rejected
from scripts.rq4.map_issue_with_advisory import map_github_issue_with_advisory, extract_remediation_from_advisory, \
    categorize_cve_description_rs, check_advisory_with_cve
from scripts.process_non_bot import summerize_github_issues
from config import mongo_host, mongo_port
from scripts.query_reject_reason import query_reject_reason
from scripts.role_determination import determine_role
from scripts.rq1.count_taxonomy import count_tax
from scripts.rq2.count_taxo_distribution import calculate_quadrant_distribution_of_taxo
from scripts.rq3.reopen_analysis import add_link_2_csv, analyze_rediscussion
from scripts.rq3.rs_distri_evolution import get_evolution_data_major_cate, reformat_all_in_one
from scripts.rq4.map_issue_with_advisory import check_issue_multiple_cve

# Connect to MongoDB
c = pymongo.MongoClient(mongo_host, port=mongo_port)
# Instantiate a collection for CVE-related issues
cve_coll = c['remediation']['github_cve_issues']

# Summarize GitHub issues by print it to the console for manual labeling
summerize_github_issues(c) # Print first 5 issues for verification

# Interactively print the CVE-related issues
print_cve_issue(c)

# Summarize the CVE-related issues
summarize_for_cve(c)

# Extract and save the CVE-related issues
extract_and_save_cve_issues(c, 'github_issues_non_bots', 'github_cve_issues')

# Map GitHub issues with advisories by updating the advisory collection
map_github_issue_with_advisory(c)

# Query the rejection reasons for the issues for manual labeling
query_reject_reason(c)

# Categorize the rejected fixes by printing to the console for manual labeling
categorize_rejcted_fixes()

# Extract the remediation from the advisory
extract_remediation_from_advisory(c)

# Determine the role of the issues to Provider and Seeker
determine_role(c)

# Close event analysis for the issues
analyze_close_event(c)

# Temporary scripts to quickly count the number of high level categories in the taxonomy
count_tax()

# Calculate the quadrant distribution of the taxonomy
calculate_quadrant_distribution_of_taxo()

# get the evolution data by the major categories of the taxonomy
get_evolution_data_major_cate()

# Reformat the data in all_in_one.csv
reformat_all_in_one(c)

# Add the link to the csv
add_link_2_csv(c)

# Analyze the rediscussion phenomena of the issues
analyze_rediscussion(c)

# Check the issues with multiple CVEs
check_issue_multiple_cve(c)

# Categorize the description of the CVEs based on RS
categorize_cve_description_rs(c)

# Check the advisory with CVE
check_advisory_with_cve(c)

# Count the number of accepted and rejected issues
count_accepeted_rejected(c)

c.close()





