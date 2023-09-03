#!/usr/bin/env python3
from aicodebot.cli import cli
from aicodebot.config import get_config_file
from aicodebot.helpers import logger
from click.testing import CliRunner
from github import Github
from pathlib import Path
import json, os, subprocess, sys


def main(do_comment_on_commit=True):
    """Run the AICodeBot action"""
    cli_runner = setup_cli()
    review_status, review_comments = review_code(cli_runner)
    if review_status == "FAILED":
        exit_status = 1
    else:
        exit_status = 0

    if do_comment_on_commit:
        comment_on_commit(review_status, review_comments)
    sys.exit(exit_status)


def setup_cli():
    """Set up and configure the AICodeBot CLI"""

    # Check if required inputs are set
    openai_api_key = os.getenv("INPUT_OPENAI_API_KEY")  # Note this is prefixed with INPUT_ through actions
    if not openai_api_key:
        logger.error(
            """
    🛑 The OPENAI_API_KEY is not set. This key is required for the AICodeBot.
    You can get one for free at https://platform.openai.com/account/api-keys

    Please set it as a repository secret named 'OPENAI_API_KEY'.
    For more information on how to set up repository secrets, visit:
    https://docs.github.com/en/actions/security-guides/encrypted-secrets
    """
        )
        if os.getenv("GITHUB_BASE_REF"):
            logger.success("Since this failure on a forked repository, we'll let the action pass without code review.")
            sys.exit(0)
        else:
            sys.exit(1)

    # Set the OPENAI_API_KEY environment variable
    os.environ["OPENAI_API_KEY"] = openai_api_key

    # Set up the personality, defaulting to "Her"
    os.environ["AICODEBOT_PERSONALITY"] = os.getenv("INPUT_AICODEBOT_PERSONALITY", "Her")

    # Set up the git configuration. Allow the user to override the safe directory
    subprocess.run(["git", "config", "--global", "--add", "safe.directory", "/github/workspace"])

    cli_runner = CliRunner()
    result = cli_runner.invoke(cli, ["-V"])
    logger.info("AICodeBot version:", result.output)
    assert result.exit_code == 0, f"🛑 Error running AICodeBot version: {result.output}"

    # Set up the aicodebot configuration from the OPENAI_API_KEY
    logger.debug(f"Configuring AICodeBot to write config file to {os.getenv('AICODEBOT_CONFIG_FILE')}")
    result = cli_runner.invoke(cli, ["configure", "--openai-api-key", os.getenv("OPENAI_API_KEY")])
    logger.debug("Configure:", result.output)
    assert result.exit_code == 0, f"🛑 Error running AICodeBot configure: {result.output}"
    config_file = get_config_file()
    assert Path(config_file).exists(), f"🛑 Failed to create the AICodeBot configuration file: {config_file}"

    return cli_runner


def review_code(cli_runner):
    """Run a code review on the current commit"""

    result = cli_runner.invoke(cli, ["review", "-c", os.getenv("GITHUB_SHA"), "--output-format", "json"])
    logger.debug("Review:", result.output)
    assert result.exit_code == 0, f"🛑 Error running AICodeBot review {result.output}, {result.exc_info}"

    review_output = json.loads(result.output)
    review_status = review_output["review_status"]
    review_comments = review_output["review_comments"]

    # Magic to set the output variables for github workflows
    with open(os.getenv("GITHUB_STATE"), "a") as f:  #  noqa: PTH123
        f.write(f"{review_status}={review_status}\n")

    return review_status, review_comments


def comment_on_commit(review_status, review_comments):
    """Comment on the commit with the results of the code review"""

    # ---------------------------------------------------------------------------- #
    #                           Set up the github client                           #
    # ---------------------------------------------------------------------------- #

    github_token = os.getenv("INPUT_GITHUB_TOKEN")  # Note this is prefixed with INPUT_ through actions
    assert github_token, "🛑 The GITHUB_TOKEN is not set. This key is REQUIRED for the AICodeBot."

    g = Github(github_token)

    # Get the repository
    repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))
    logger.info(f"Repository: {repo}, name: {repo.name}, owner: {repo.owner.login}")

    # Get the commit
    commit = repo.get_commit(os.getenv("GITHUB_SHA"))
    logger.info(f"Commit: {commit}")
    logger.info(f"Commit author: {commit.commit.author.name}")
    logger.info(f"Commit message: {commit.commit.message}")
    logger.debug(f"Commit date: {commit.commit.author.date}")

    # ---------------------------------------------------------------------------- #
    #                             Comment on the commit                            #
    # ---------------------------------------------------------------------------- #

    # First leave a comment on the commit
    if review_comments:
        logger.info("Review comments:", review_comments)

    comment = (
        "🤖 AICodeBot Review Comments:\n\n"
        + review_comments
        + "\n\nCode review automatically created with [AICodeBot](https://github.com/gorillamania/AICodeBot)"
    )

    # Then add a reaction to the comment
    if review_status == "PASSED":
        if os.getenv("INPUT_COMMENT_ON_PASSED"):
            commit_comment = commit.create_comment(comment)
            commit_comment.create_reaction("heart")
        logger.success("Code review passed!")
    elif review_status == "FAILED":
        commit_comment = commit.create_comment(comment)
        commit_comment.create_reaction("-1")
        logger.error("👎 Code review failed!")
    elif review_status == "COMMENTS":
        commit_comment = commit.create_comment(comment)
        commit_comment.create_reaction("eyes")
        logger.info("👍 Code review has comments, take a look")
    else:
        logger.error(f"🛑 Unknown review status: {review_status}")


if __name__ == "__main__":
    main()
