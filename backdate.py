import os
import subprocess
import random
from datetime import datetime, timedelta

# ==========================
# CONFIGURATION
# ==========================
GITHUB_USERNAME = "saleem-shaik-git"
GITHUB_EMAIL = "shaik.saleem@outlook.com"  # Replace with verified GitHub email
REPO_DIR = "."  # Use "." for current repo
NUM_COMMITS_PER_DAY = (1, 3)
YEARS_BACK = 5
COMMIT_MESSAGE_FILE = "commit_messages.txt"
BRANCH_NAME = "main"
# ==========================


def run_cmd(cmd, cwd=None, env=None):
    """Run a shell command and return output."""
    result = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"⚠️ Error: {' '.join(cmd)}\n{result.stderr}")
    return result.stdout.strip()


def setup_git_identity():
    """Set Git user identity globally and locally."""
    print("🧩 Setting up Git identity...")
    subprocess.run(["git", "config", "--global", "user.name", GITHUB_USERNAME])
    subprocess.run(["git", "config", "--global", "user.email", GITHUB_EMAIL])
    subprocess.run(["git", "config", "user.name", GITHUB_USERNAME], cwd=REPO_DIR)
    subprocess.run(["git", "config", "user.email", GITHUB_EMAIL], cwd=REPO_DIR)


def fix_remote_origin():
    """Ensure repo remote points to user's GitHub account."""
    print("🔗 Checking remote origin...")
    remote_url = run_cmd(["git", "remote", "get-url", "origin"], cwd=REPO_DIR)

    if GITHUB_USERNAME not in remote_url:
        repo_name = os.path.basename(os.getcwd())
        new_url = f"https://github.com/{GITHUB_USERNAME}/{repo_name}.git"
        print(f"🔄 Updating remote URL to: {new_url}")
        subprocess.run(["git", "remote", "set-url", "origin", new_url], cwd=REPO_DIR)
    else:
        print("✅ Remote URL already correct.")


def load_commit_messages():
    """Load commit messages from file or fallback defaults."""
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
        if current.weekday() < 5:  # Mon–Fri only
            date_list.append(current)
        current += timedelta(days=1)
    return date_list


def make_commit(commit_date, messages):
    """Create commits for a given date."""
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
        env["GIT_AUTHOR_NAME"] = GITHUB_USERNAME
        env["GIT_COMMITTER_NAME"] = GITHUB_USERNAME
        env["GIT_AUTHOR_EMAIL"] = GITHUB_EMAIL
        env["GIT_COMMITTER_EMAIL"] = GITHUB_EMAIL
        subprocess.run(["git", "commit", "-m", message], cwd=REPO_DIR, env=env,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def backdate_commits():
    setup_git_identity()
    fix_remote_origin()
    print(f"📅 Generating weekday commits for the past {YEARS_BACK} years...")
    messages = load_commit_messages()
    commit_dates = generate_commit_dates(YEARS_BACK)
    total_days = len(commit_dates)
    count = 0

    for date in commit_dates:
        make_commit(date, messages)
        count += 1
        if count % 50 == 0:
            print(f"✅ {count}/{total_days} weekdays processed...")

    print(f"\n🎉 Done! Created commits for {count} weekdays.")
    print("🚀 Pushing to GitHub...")
    subprocess.run(["git", "push", "origin", BRANCH_NAME], cwd=REPO_DIR)
    print("✅ All commits pushed successfully!")


if __name__ == "__main__":
    backdate_commits()
