"""
1. Populates the database with the -l lotteries for the next -l days starting with date -s.
2. Creates -u users.
3. Each user randomly sumbits -b ballots for the lotteries.

Run python scripts/populate.py --help for more information.
"""

import argparse
import random
import requests
from datetime import date, timedelta
from http import HTTPStatus


class PopulateLottery:

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def register_user(self, username, email, password="DemoPassword123!"):
        payload = {
            "username": username,
            "email": email,
            "password": password
        }
        response = requests.post(f"{self.base_url}/user/register", json=payload)
        print(f"Register user {username}: {response.status_code}")
        if response.status_code == HTTPStatus.CREATED:
            d = response.json()
            print(f"    User registered with email: {d['email']}, id: {d['id']}")
        return response.json()


    def login_user(self, email, password="DemoPassword123!"):
        payload = {
            "username": email,
            "password": password
        }
        response = requests.post(f"{self.base_url}/auth/login", data=payload)
        return response.json()["access_token"]


    def create_lottery(self, token, closure_date):
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"closure_date": closure_date}
        response = requests.post(f"{self.base_url}/lotteries/", json=payload, headers=headers)
        print(f"Create Lottery {closure_date}: {response.status_code}")
        if response.status_code == HTTPStatus.CREATED:
            d = response.json()
            print(f"    Lottery created with name: {d['name']}, id: {d['id']}")
        return response.json()


    def submit_ballot(self, token, closure_date):
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{self.base_url}/ballots/", params={"lottery_date": closure_date}, headers=headers)
        print(f"Submit Ballot {closure_date}: {response.status_code}")
        if response.status_code == HTTPStatus.CREATED:
            d = response.json()
            print(f"    Ballot submitted with id: {d['id']} to lottery id: {d['lottery_id']} by user id: {d['user_id']}")
        return response.json()


def main(base_url:str, admin_email: str, admin_password: str,
         lotteries: int, users: int, ballots_per_user: int,
         first_closure_date: date):
    print("Populating demo data...")

    populate = PopulateLottery(base_url)

    # Step 1: Admin login
    admin_token = populate.login_user(admin_email, admin_password)

    # Step 2: Create lotteries for the next N days startin today
    upcoming_dates = [(first_closure_date + timedelta(days=i)).isoformat() for i in range(lotteries)]
    for closure_date in upcoming_dates:
        populate.create_lottery(admin_token, closure_date)

    # Step 3: Create users and simulate ballot submissions
    for i in range(1, users + 1):
        username = f"user{i}"
        email = f"user{i}@example.com"
        populate.register_user(username, email)
        user_token = populate.login_user(email)

        for _ in range(ballots_per_user):
            # Pick a random lottery date for each ballot
            chosen_date = random.choice(upcoming_dates)
            populate.submit_ballot(user_token, chosen_date)

    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Populate demo data via API")
    parser.add_argument("-l", "--lotteries", type=int, default=30, help="Number of lotteries to create")
    parser.add_argument("-u", "--users", type=int, default=10, help="Number of users to create")
    parser.add_argument("-b", "--ballots", type=int, default=100, help="Number of ballots per user")
    parser.add_argument("-e", "--email", type=str, default="admin@example.com", help="Admin account email")
    parser.add_argument("-p", "--password", type=str, default="admin_password", help="Admin account password")
    parser.add_argument("-U", "--base_url", type=str, default="http://localhost:8000", help="Base URL")
    parser.add_argument("-d", "--first_closure_date", type=date, default=date.today(), help="First closure date of the created lotteries")
    args = parser.parse_args()

    main(args.base_url, args.email, args.password, args.lotteries, args.users, args.ballots, args.first_closure_date)