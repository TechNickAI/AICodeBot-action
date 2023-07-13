#!/usr/bin/env python3
from aicodebot.cli import cli
from aicodebot.config import get_config_file
from click.testing import CliRunner
from github import Github
from pathlib import Path
import json, os, subprocess, sys

# ---------------------------------------------------------------------------- #
#                                    Set up                                    #
# ---------------------------------------------------------------------------- #

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

# Set the OPENAI_API_KEY environment variable
os.environ["OPENAI_API_KEY"] = openai_api_key

# Set up the personality, defaulting to "Her"
os.environ["AICODEBOT_PERSONALITY"] = os.getenv("INPUT_AICODEBOT_PERSONALITY", "Her")

# Set up the git configuration. Allow the user to override the safe directory
subprocess.run(["git", "config", "--global", "--add", "safe.directory", "/github/workspace"])

# Test the CLI
cli_runner = CliRunner()
result = cli_runner.invoke(cli, ["-V"])
print("AICodeBot version:", result.output)
assert result.exit_code == 0

# ---------------------------------------------------------------------------- #
#                              Run the code review                             #
# ---------------------------------------------------------------------------- #

# Set up the aicodebot configuration from the OPENAI_API_KEY
result = cli_runner.invoke(cli, ["configure", "--openai-api-key", openai_api_key])
print(f"Configure: {result.output}")
assert result.exit_code == 0
assert Path(get_config_file()).exists()

# Run a code review on the current commit
result = cli_runner.invoke(cli, ["review", "-c", os.getenv("GITHUB_SHA"), "--output-format", "json"])
print("Review:", result.output)
assert result.exit_code == 0

review_output = json.loads(result.output)
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
print(f"Repository name: {repo.name}")
print(f"Repository owner: {repo.owner.login}")
print(f"Repository pushed at: {repo.pushed_at}")

# Get the commit
commit = repo.get_commit(os.getenv("GITHUB_SHA"))
print(f"Commit: {commit}")
print(f"Commit message: {commit.commit.message}")
print(f"Commit author: {commit.commit.author.name}")
print(f"Commit date: {commit.commit.author.date}")

# ---------------------------------------------------------------------------- #
#                         Leave a comment on the commit                        #
# ---------------------------------------------------------------------------- #

# First leave a comment on the commit
if review_comments:
    print(f"Review: {review_comments}")

comment = (
    "🤖AICodeBot Review Comments:\n\n" + review_comments + "\n\n[AICodeBot](https://github.com/gorillamania/AICodeBot)"
)

# Then add a reaction to the comment
if review_status == "PASSED":
    if os.getenv("INPUT_COMMENT_ON_PASSED"):
        commit_comment = commit.create_comment(comment)
        commit.create_reaction("heart")
    print("✅️ Code review passed!")
elif review_status == "FAILED":
    commit_comment = commit.create_comment(comment)
    commit_comment.create_reaction("-1")
    print("👎 Code review failed!")
    sys.exit(1)
elif review_status == "COMMENTS":
    commit_comment = commit.create_comment(comment)
    commit_comment.create_reaction("eyes")
    print("👍 Code review has comments, take a look")
    sys.exit(0)
