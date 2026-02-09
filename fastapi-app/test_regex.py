import re

def parse_profile(query_lower):
    updates = {}
    
    # Extract Name
    name_match = re.search(r'(name is|nam|naam)\s+([a-zA-Z\s]+)', query_lower)
    if name_match:
         updates["name"] = name_match.group(2).strip()

    # Extract Week
    week_match = re.search(r'(\d+)\s*(weeks|sopta|soptaho)', query_lower)
    if week_match:
         updates["week"] = week_match.group(1)
         
    # Extract Age
    age_match = re.search(r'(\d+)\s*(years|bochor|age)', query_lower)
    if age_match:
         updates["age"] = int(age_match.group(1))

    return updates

# Test Cases
queries = [
    "my name is rahima",
    "amar nam rahima",
    "i am 20 weeks pregnant",
    "20 soptaho cholche",
    "week 20 running",
    "my age is 25",
    "25 bochor boyos",
    "change profile name to sarah",
    "my name is rahima and i am 20 weeks pregnant",
    "name is fatima, 30 weeks"
]

print("🔍 Testing Regex Extraction...")
for q in queries:
    res = parse_profile(q.lower())
    print(f"'{q}' -> {res}")
