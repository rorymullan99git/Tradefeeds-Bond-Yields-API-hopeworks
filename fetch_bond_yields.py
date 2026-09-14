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

        # Process and filter for 10Y and 2Y
        filtered_results = []
        for item in results:
            item_type = item.get('type', '').upper()
            if item_type in ('10Y', '2Y'):
                # Normalize date
                if 'date' in item and ':' in item['date']:
                    item['date'] = item['date'].replace(':', '-')

                # Parse yield as float
                if 'yield' in item:
                    try:
                        item['yield'] = float(item['yield'])
                    except ValueError:
                        pass

                filtered_results.append(item)

        output_dir = "data"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_file = os.path.join(output_dir, "australia_bond_yields.json")

        existing_data = []
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r') as f:
                    existing_data = json.load(f)
            except json.JSONDecodeError:
                pass

        # Deduplicate by date and bond type
        seen = set()
        for item in existing_data:
            key = (item.get('date'), item.get('type', '').upper())
            seen.add(key)

        new_records_count = 0
        for item in filtered_results:
            key = (item.get('date'), item.get('type', '').upper())
            if key not in seen:
                existing_data.append(item)
                seen.add(key)
                new_records_count += 1

        # Optionally sort by date
        existing_data.sort(key=lambda x: (x.get('date', ''), x.get('type', '')))

        with open(output_file, 'w') as f:
            json.dump(existing_data, f, indent=4)

        print(f"Successfully saved {new_records_count} new records to {output_file} (Total: {len(existing_data)})")

    except urllib.error.URLError as e:
        print(f"Failed to fetch data: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    fetch_bond_yields()
