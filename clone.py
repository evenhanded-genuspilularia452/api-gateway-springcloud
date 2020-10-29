#!/usr/bin/env python3
"""
clone_all_repos_debug.py
Clones all repositories for the authenticated user (uses a PAT).
- Automatically detects username from the token.
- URL-encodes token to safely insert into HTTPS clone URLs.
- Prints repo list and detailed errors when clone fails.
"""

import os
import sys
import subprocess
from github import Github, GithubException
from urllib.parse import quote_plus

# ========== CONFIG ==========
GITHUB_TOKEN = "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"  # <-- Put your PAT here
DESTINATION_DIR = "cloned_repos"  # folder where repos will be cloned
# ===========================

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def safe_clone_url(repo, token):
    """
    Insert a URL-encoded token into the HTTPS clone URL safely.
    Example result: https://<token>@github.com/owner/repo.git
    """
    # repo.clone_url is like: https://github.com/owner/repo.git
    encoded_token = quote_plus(token)  # safe encoding
    return repo.clone_url.replace("https://", f"https://{encoded_token}@")

def run_cmd(cmd, cwd=None):
    """Run command and return (returncode, stdout, stderr)."""
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def clone_all_repos(token, dest_dir):
    if not token or token.startswith("ghp_xxx"):
        print("⚠️  Please edit the script and set GITHUB_TOKEN to a valid PAT (with 'repo' scope for private repos).")
        return

    g = Github(token)
    try:
        auth_user = g.get_user()
        username = auth_user.login
        print(f"🔐 Authenticated as: {username}")
    except GithubException as e:
        print("❌ Failed to authenticate with provided token:", e)
        return

    ensure_dir(dest_dir)

    print("\n📥 Fetching repositories (this may take a moment)...")
    try:
        repos = list(auth_user.get_repos())  # loads all repos (paginated internally)
    except GithubException as e:
        print("❌ Failed to retrieve repositories:", e)
        return

    if not repos:
        print("ℹ️ No repositories found for this account.")
        return

    print(f"🔎 Found {len(repos)} repositories. Starting clone into '{dest_dir}'\n")

    for repo in repos:
        repo_name = repo.name
        target_path = os.path.join(dest_dir, repo_name)

        if os.path.exists(target_path):
            print(f"⏭️  Skipping {repo_name} — target folder already exists.")
            continue

        clone_url = safe_clone_url(repo, token)
        print(f"⬇️  Cloning {repo.full_name} → {target_path}")
        print(f"    clone_url: {clone_url}")

        cmd = ["git", "clone", clone_url, target_path]
        rc, out, err = run_cmd(cmd)

        if rc == 0:
            print(f"   ✅ Successfully cloned {repo.full_name}\n")
        else:
            print(f"   ❌ Failed to clone {repo.full_name} (exit {rc})")
            if out:
                print("   stdout:", out)
            if err:
                print("   stderr:", err)
            print("   Hint: if the repo is private ensure the PAT has 'repo' scope and is valid.\n")

    print("🎉 Done.")

if __name__ == "__main__":
    clone_all_repos(GITHUB_TOKEN, DESTINATION_DIR)
