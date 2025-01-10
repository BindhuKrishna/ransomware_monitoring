#do not touch the code. - Bindu


import json
import requests
from datetime import datetime, timezone
import time


session = requests.Session()

def fetch_data(url):
    try:
        response = session.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Failed to fetch data: {e}")
        return []

def send_webhook_alerts(alerts, webhook_url):
    
    for alert in alerts:
        payload = {
            "embeds": [{
                "title": "New Data Alert",
                "description": alert,
                "color": 16711680  # Red color
            }]
        }
        print(f"Sending webhook: {payload}")  
        try:
            response = session.post(webhook_url, json=payload)
            response.raise_for_status()
            print("Webhook sent successfully.")
        except requests.RequestException as e:
            print(f"Failed to send alert: {e}")
        time.sleep(1)

def load_processed_data(filename):
    
    try:
        with open(filename, 'r') as f:
            data_list = json.load(f)
            return {tuple(sorted(d.items())) for d in data_list}
    except FileNotFoundError:
        return set()

def save_processed_data(filename, data):
    
    with open(filename, 'w') as f:
        json.dump([dict(t) for t in data], f)

def main():
    # Configuration
    data_url = 'https://ransomwhat.telemetry.ltd/posts'
    processed_data_file = 'processed_data.json'
    webhook_url = "ADD YOUR WEBHOOK URL HERE"

    cutoff_date = datetime(2024, 11, 20, tzinfo=timezone.utc)

    while True:
        print("Loading previously processed data...")
        processed_data = load_processed_data(processed_data_file)

        print("Fetching current data...")
        current_data = fetch_data(data_url)

        if not current_data:
            print("No data fetched. Exiting...")
            return

        print(f"Processing {len(current_data)} items...")
        new_alerts = []
        for post in current_data:
            post_tuple = tuple(sorted(post.items()))
            post_date = datetime.fromisoformat(post['discovered']).replace(tzinfo=timezone.utc)
            if post_date > cutoff_date and post_tuple not in processed_data:
                alert = f"Post Title: {post['post_title']}, Group Name: {post['group_name']}, Discovered: {post['discovered']}"
                print(f"New alert: {alert}")
                new_alerts.append(alert)
                processed_data.add(post_tuple)

        if new_alerts:
            print("Sending alerts...")
            send_webhook_alerts(new_alerts, webhook_url)
            save_processed_data(processed_data_file, processed_data)
        else:
            print("No new alerts to send.")

        print("Sleeping for 15 minutes...")
        time.sleep(900)

if __name__ == "__main__":
    main()
