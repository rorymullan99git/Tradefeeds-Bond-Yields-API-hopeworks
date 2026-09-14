import os
import json
import urllib.request
import urllib.error

def fetch_bond_yields():
    api_key = os.environ.get('TRADEFEEDS_API_KEY')
    if not api_key:
        print("Error: TRADEFEEDS_API_KEY environment variable not set.")
        return

    # Fetch 10-year and 2-year bond yields for Australia

    # URL structure as per README: https://data.tradefeeds.com/api/v1/bond_yields?key=API-KEY&country=australia
    base_url = "https://data.tradefeeds.com/api/v1/bond_yields"

    try:
        url = f"{base_url}?key={api_key}&country=australia"
        print(f"Fetching data from: {base_url}?key=***&country=australia")

        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

        if 'error' in data:
            print(f"API Error: {data['error']}")
            return

        if data.get('status', {}).get('code') != 200:
            print(f"API Error: {data.get('status', {}).get('message')}")
            return

        results = data.get('result', {}).get('output', [])

        # Filter for 10Y and 2Y
        filtered_results = [item for item in results if item.get('type') in ('10Y', '2Y')]

        output_dir = "data"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_file = os.path.join(output_dir, "australia_bond_yields.json")
        with open(output_file, 'w') as f:
            json.dump(filtered_results, f, indent=4)

        print(f"Successfully saved {len(filtered_results)} records to {output_file}")

    except urllib.error.URLError as e:
        print(f"Failed to fetch data: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    fetch_bond_yields()
