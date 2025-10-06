import requests
import json
import os
import random
import string
import threading
import time
from datetime import datetime
from queue import Queue, Empty

# Locks for thread-safe operations
file_lock = threading.Lock()
stats_lock = threading.Lock()

# Global counter for successful creations
success_counter = 0

def get_random_string(length):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def create_account(proxy):
    retries = 3
    backoff_factor = 0.5
    for i in range(retries):
        try:
            # Get a random domain
            response = requests.get("https://api.mail.tm/domains", proxies=proxy, timeout=10)
            response.raise_for_status()
            domains = response.json()["hydra:member"]
            domain = random.choice(domains)["domain"]

            # Create a random username and password
            username = get_random_string(10)
            password = get_random_string(12)
            address = f"{username}@{domain}"

            # Create the account
            payload = {
                "address": address,
                "password": password
            }
            response = requests.post("https://api.mail.tm/accounts", json=payload, proxies=proxy, timeout=10)
            response.raise_for_status()
            return address, password
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}. Retrying in {backoff_factor * (2 ** i)} seconds...")
            time.sleep(backoff_factor * (2 ** i))
    print("Failed to create account after several retries.")
    return None, None

def worker(queue, folder_name, proxies):
    global success_counter
    while True:
        try:
            i = queue.get_nowait()
            address, password = create_account(proxies)
            if address and password:
                print(f"[{i}] Created email: {address}")
                with file_lock:
                    with open(os.path.join(folder_name, "emails_numbered.txt"), "a") as f_numbered, \
                         open(os.path.join(folder_name, "emails_unnunbered.txt"), "a") as f_unnumbered:
                        f_numbered.write(f"{i}. {address}:{password}\n")
                        f_unnumbered.write(f"{address}:{password}\n")
                
                with stats_lock:
                    success_counter += 1
            queue.task_done()
        except Empty:
            break

def update_stats(count):
    stats_file = "stats.json"
    today_str = datetime.now().strftime("%Y-%m-%d")
    stats = {
        "lifetime_total": 0,
        "today_total": 0,
        "last_run_date": ""
    }

    if os.path.exists(stats_file):
        with open(stats_file, "r") as f:
            try:
                stats = json.load(f)
            except json.JSONDecodeError:
                pass  # File is corrupt or empty, use default stats

    if stats.get("last_run_date") == today_str:
        stats["today_total"] = stats.get("today_total", 0) + count
    else:
        stats["today_total"] = count

    stats["lifetime_total"] = stats.get("lifetime_total", 0) + count
    stats["last_run_date"] = today_str

    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=4)

def main():
    num_emails = int(input("Enter the number of emails to create: "))
    reason = input("Enter the reason for creating these emails: ")
    num_threads = int(input("Enter the number of threads to use (e.g., 10): "))

    # Create folder
    today_date = datetime.now().strftime("%Y-%m-%d")
    folder_name = f"{today_date}_{reason}"
    os.makedirs(folder_name, exist_ok=True)

    # Proxy configuration
    proxy_url = "http://login:password@gw.dataimpulse.com:823"
    proxies = {
        "http": proxy_url,
        "https": proxy_url
    }

    # Create queue and threads
    queue = Queue()
    for i in range(1, num_emails + 1):
        queue.put(i)

    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=worker, args=(queue, folder_name, proxies))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Sort the numbered emails file
    numbered_file_path = os.path.join(folder_name, "emails_numbered.txt")
    if os.path.exists(numbered_file_path):
        with open(numbered_file_path, "r") as f:
            lines = f.readlines()
        
        # Sort the lines based on the leading number
        lines.sort(key=lambda line: int(line.split('.')[0]))

        with open(numbered_file_path, "w") as f:
            f.writelines(lines)

    # Update stats
    update_stats(success_counter)

    print(f"Email generation complete. {success_counter} emails created.")

if __name__ == "__main__":
    main()