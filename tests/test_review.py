import aicodebot_action, os, pytest, subprocess


@pytest.mark.skipif(not os.getenv("INPUT_OPENAI_API_KEY"), reason="skipping live tests without an api key.")
def test_commit_review(tmp_path):
    # Simulate the github environment variables
    os.environ["GITHUB_REPOSITORY"] = (
        subprocess.check_output(["git", "config", "--get", "remote.origin.url"]).decode().strip()
    )
    os.environ["GITHUB_SHA"] = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    os.environ["GITHUB_STATE"] = str(tmp_path / "GITHUB_STATE")
    os.environ["INPUT_GITHUB_TOKEN"] = "test token"

    # Override the config file to a tmp path
    os.environ["AICODEBOT_CONFIG_FILE"] = str(tmp_path / "aicodebot.yaml")
    assert "aicodebot.yaml" in os.getenv("AICODEBOT_CONFIG_FILE")

    # TODO: Mock the github client so we can test the comment on commit as well
    aicodebot_action.main(comment_on_commit=False)
