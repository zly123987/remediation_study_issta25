import re
def extract_json_from_string(s):
    pattern = r'\{\s*"category"\s*:\s*"[^"]*"\s*\}'

    # Search for the pattern
    match = re.search(pattern, s)
    if match:
        extracted_json = match.group(0)
        print("Extracted JSON:", extracted_json)
        return extracted_json
    else:
        print("No JSON-like data found.")
        return s