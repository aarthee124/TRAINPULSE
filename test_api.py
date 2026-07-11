import requests

key = "rg_94a0c2d9e60b49a3ba4849dfe860b53f"
url = "https://api.railradar.in/v1/trains/12693/live"
headers = {"Authorization": f"Bearer rg_4126ef2bf26c45ea99bd35944f299460"}

response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")