import os
import subprocess
import random
from datetime import datetime, timedelta

# ==========================
# CONFIGURATION
# ==========================
REPO_DIR = "."  # Directory of your local git repo (use "." for current folder)
NUM_COMMITS_PER_DAY = (1, 3)  # Random number of commits between min and max
YEARS_BACK = 5  # How many years to backdate
COMMIT_MESSAGE_FILE = "commit_messages.txt"  # Optional: list of commit messages
# ==========================


def load_commit_messages():
    if os.path.exists(COMMIT_MESSAGE_FILE):
        with open(COMMIT_MESSAGE_FILE, "r") as f:
            messages = [line.strip() for line in f if line.strip()]
        return messages
    return [
        "Refactor code",
        "Fix bug in service",
        "Improve API performance",
        "Update dependencies",
        "Add unit tests",
        "Enhance error handling",
        "Code cleanup",
        "Improve documentation"
    ]


def generate_commit_dates(years=5):
    """Generate all weekdays (Mon–Fri) for the past N years."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years * 365)
    date_list = []
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # 0=Mon, 6=Sun — skip weekends
            date_list.append(current)
        current += timedelta(days=1)
    return date_list


def make_commit(commit_date, messages):
    """Make a commit with a given date and random message."""
    num_commits = random.randint(*NUM_COMMITS_PER_DAY)
    for _ in range(num_commits):
        message = random.choice(messages)
        with open(os.path.join(REPO_DIR, "activity_log.txt"), "a") as f:
            f.write(f"{commit_date.isoformat()} - {message}\n")
        subprocess.run(["git", "add", "."], cwd=REPO_DIR)
        env = os.environ.copy()
        date_str = commit_date.strftime("%Y-%m-%dT%H:%M:%S")
        env["GIT_AUTHOR_DATE"] = date_str
        env["GIT_COMMITTER_DATE"] = date_str
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=REPO_DIR,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def backdate_commits():
    print(f"📅 Generating commits for the past {YEARS_BACK} years (weekdays only)...")
    messages = load_commit_messages()
    commit_dates = generate_commit_dates(YEARS_BACK)
    total_days = len(commit_dates)
    count = 0

    for date in commit_dates:
        make_commit(date, messages)
        count += 1
        if count % 50 == 0:
            print(f"✅ {count}/{total_days} days completed...")

    print(f"\n🎉 Done! {count} weekdays of commits have been created.")
    print("🚀 Push to GitHub with:")
    print("\n   git push origin main\n")


if __name__ == "__main__":
    backdate_commits()
