"""
Close lottery and draw winner script.

Run python scripts/close_and_draw.py --help for more information.
"""

import argparse
from datetime import date, timedelta
import requests
from http import HTTPStatus


def login_admin(base_url, email, password):
    payload = {
        "username": email,
        "password": password
    }
    response = requests.post(f"{base_url}/auth/login", data=payload)
    response.raise_for_status()
    return response.json()["access_token"]


def close_lottery(base_url, closure_date, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{base_url}/lotteries/close_and_draw/?lottery_date={closure_date}", headers=headers)
    if response.status_code == HTTPStatus.OK:
        print(f"Lottery for {closure_date} successfully closed.")

        response = requests.get(f"{base_url}/lotteries/{closure_date}/winner", headers=headers)
        if response.status_code == HTTPStatus.OK:
            print("Winning ballot:", response.json())
        else:
            print("No ballots were submitted - no winner.")
    else:
        print(f"Failed to close lottery for {closure_date}: {response.status_code} {response.text}")


def main(base_url, closure_date, admin_email, admin_password):
    print(f"Closing lottery for {closure_date}...")
    try:
        token = login_admin(base_url, admin_email, admin_password)
    except requests.HTTPError as e:
        print(f"Failed to authenticate admin: {e.response.status_code} {e.response.text}")
        return

    close_lottery(base_url, closure_date, token)


if __name__ == "__main__":
    default_date = (date.today() - timedelta(days=1)).isoformat()

    parser = argparse.ArgumentParser(description="Close lottery and draw winner.")
    parser.add_argument("-d", "--date", type=str, default=default_date, help="Closure date in YYYY-MM-DD format (default: yesterday)")
    parser.add_argument("-e", "--email", type=str, default="admin@example.com", help="Admin email")
    parser.add_argument("-p", "--password", type=str, default="admin_password", help="Admin password")
    parser.add_argument("-U", "--base_url", type=str, default="http://localhost:8000", help="Base URL")
    args = parser.parse_args()

    main(args.base_url, args.date, args.email, args.password)