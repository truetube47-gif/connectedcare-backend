import requests
import json

# Test the drug endpoint
try:
    response = requests.get("http://localhost:8000/drug/drugs")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        drugs = response.json()
        print(f"Found {len(drugs)} drugs")
        for drug in drugs[:3]:
            print(f"- {drug['trade_name']} ({drug.get('strength', 'N/A')})")
    else:
        print("Endpoint not working")
        
except Exception as e:
    print(f"Error: {e}")

# Test root endpoint
try:
    response = requests.get("http://localhost:8000/")
    print(f"\nRoot Status: {response.status_code}")
    print(f"Root Response: {response.text}")
except Exception as e:
    print(f"Root Error: {e}")
