# Email Generator Bot

[![DataImpulse](https://app.dataimpulse.com/assets/images/referral-banner.png)](https://dataimpulse.com/?aff=43293)

This bot generates a specified number of email addresses using the `mail.tm` API and saves them into two separate files.

## Prerequisites

- Python 3.x
- `requests` library

## Installation

1. **Install Python:** If you don't have Python installed, download and install it from [python.org](https://python.org).

2. **Install the `requests` library:** Open your terminal or command prompt and run the following command:
   ```bash
   pip install requests
   ```

## How to Run the Script

1. **Open your terminal or command prompt.**

2. **Navigate to the directory where you saved the `email_generator.py` script.**

3. **Run the script using the following command:**
   ```bash
   python email_generator.py
   ```

4. **Follow the on-screen prompts:**
   - Enter the number of emails you want to create.
   - Enter a reason for creating the emails (this will be used in the folder name).
   - Enter the number of threads to use (e.g., 10). This will determine how many emails are created concurrently.

## Proxy Usage

This script is configured to use proxies from DataImpulse to allow for the creation of a large number of emails without being rate-limited.

## Output

The script will create a new folder named `YYYY-MM-DD_reason` (e.g., `2023-10-27_test_run`). Inside this folder, you will find two files:

- `emails_numbered.txt`: A file containing the generated email addresses and passwords, with each line numbered and sorted.
- `emails_unnunbered.txt`: A file containing the generated email addresses and passwords, without line numbers.

Additionally, a `stats.json` file will be created in the root directory to track email generation statistics.

## Statistics

The `stats.json` file tracks the number of emails created over time. It contains the following fields:

- `lifetime_total`: The total number of emails created since the script was first run.
- `today_total`: The number of emails created on the current day.
- `last_run_date`: The date of the last run.