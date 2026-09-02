# check_api_structure.py
import requests
import json

response = requests.get("http://localhost:3000/api/institutions?limit=2")
print("Status:", response.status_code)

if response.status_code == 200:
    data = response.json()
    print("\n=== API RESPONSE STRUCTURE ===\n")
    print("Top level keys:", data.keys() if isinstance(data, dict) else "Is list")
    
    # Agar list hai to pehla item dekho
    if isinstance(data, list):
        print(f"\nTotal items in list: {len(data)}")
        print("\nFirst college structure:")
        print(json.dumps(data[0], indent=2))
    else:
        # Agar dict hai to
        colleges = data.get('institutions', data.get('data', data.get('colleges', [])))
        if colleges:
            print("\nFirst college structure:")
            print(json.dumps(colleges[0], indent=2))
            