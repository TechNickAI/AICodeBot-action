#!/usr/bin/env python3
from github import Github
import json, os, subprocess, sys

# Check if required inputs are set
openai_api_key = os.getenv("INPUT_OPENAI_API_KEY")  # Note this is prefixed with INPUT_ through actions
if not openai_api_key:
    print("🛑 The OpenAI API Key is not set. This key is REQUIRED for the AICodeBot.")
    print("You can get one for free at https://platform.openai.com/account/api-keys")
    print()
    print("Please set it as a repository secret named 'OPENAI_API_KEY'.")
    print("For more information on how to set up repository secrets, visit:")
    print("https://docs.github.com/en/actions/security-guides/encrypted-secrets")
    sys.exit(1)

# Set up the git configuration. Allow the user to override the safe directory
subprocess.run(["git", "config", "--global", "--add", "safe.directory", "/github/workspace"])

# ---------------------------------------------------------------------------- #
#                              Run the code review                             #
# ---------------------------------------------------------------------------- #

# Set up the aicodebot configuration from the OPENAI_API_KEY
subprocess.run(["aicodebot", "-V"])
subprocess.run(["aicodebot", "configure", "--openai-api-key", openai_api_key])

# Run a code review on the current commit
review_output = subprocess.run(
    ["aicodebot", "review", "-c", os.getenv("GITHUB_SHA"), "--output-format=json"],
    capture_output=True,
    text=True,
)
review_output = json.loads(review_output.stdout)
review_status = review_output["review_status"]
review_comments = review_output["review_comments"]

# Magic to set the output variables for github workflows
with open(os.getenv("GITHUB_STATE"), "a") as f:  #  noqa: PTH123
    f.write(f"{review_status}={review_status}\n")

# ---------------------------------------------------------------------------- #
#                           Set up the github client                           #
# ---------------------------------------------------------------------------- #

github_token = os.getenv("INPUT_GITHUB_TOKEN")  # Note this is prefixed with INPUT_ through actions
assert github_token, "🛑 The GITHUB_TOKEN is not set. This key is REQUIRED for the AICodeBot."

g = Github(github_token)

# Get the repository
repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))
print(f"Repo: {repo}")

# Get the commit
commit = repo.get_commit(os.getenv("GITHUB_SHA"))
print(f"Commit: {commit}")

# ---------------------------------------------------------------------------- #
#                            Helpful debugging info                            #
# ---------------------------------------------------------------------------- #
print(f"Repository name: {repo.name}")
print(f"Repository owner: {repo.owner.login}")
print(f"Repository pushed at: {repo.pushed_at}")

print(f"Commit message: {commit.commit.message}")
print(f"Commit author: {commit.commit.author.name}")
print(f"Commit date: {commit.commit.author.date}")

# ---------------------------------------------------------------------------- #
#                         Leave a comment on the commit                        #
# ---------------------------------------------------------------------------- #

# First leave a comment on the commit
if review_comments:
    comment = "🤖AICodeBot Review Comments:\n" + review_comments
    print(f"Comments: {comment}")
    commit_comment = commit.create_comment(comment)

# Then add a reaction to the comment
if review_status == "PASSED":
    commit_comment.create_reaction("heart")
    print("❤️ Code review passed!")
elif review_status == "FAILED":
    commit_comment.create_reaction("-1")
    print("👎 Code review failed!")
    sys.exit(1)
elif review_status == "COMMENTS":
    commit_comment.create_reaction("eyes")
    print("👍 Code review has comments.")
    sys.exit(0)
