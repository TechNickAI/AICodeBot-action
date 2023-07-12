import json
import os
import subprocess
import sys

from rich import Markdown

# Check if required inputs are set
openai_api_key = os.getenv('INPUT_OPENAI_API_KEY')
if not openai_api_key:
    print("🛑 The OpenAI API Key is not set. This key is REQUIRED for the AICodeBot.")
    print("You can get one for free at https://platform.openai.com/account/api-keys")
    print()
    print("Please set it as a repository secret named 'OPENAI_API_KEY'.")
    print("For more information on how to set up repository secrets, visit:")
    print("https://docs.github.com/en/actions/security-guides/encrypted-secrets")
    sys.exit(1)

# Set up the git configuration. Allow the user to override the safe directory
subprocess.run(['git', 'config', '--global', '--add', 'safe.directory', '/github/workspace'])

# Set up the aicodebot configuration from the OPENAI_API_KEY
subprocess.run(['aicodebot', '-V'])
subprocess.run(['aicodebot', 'configure'])

# Run a code review on the current commit
review_output = subprocess.run(['aicodebot', 'review', '-c', os.getenv('GITHUB_SHA'), '--output-format=json'], capture_output=True, text=True)
review_output = json.loads(review_output.stdout)
review_status = review_output['review_status']
review_comments = review_output['review_comments']

# Magic to set the output variables for github workflows
with open(os.getenv('GITHUB_STATE'), 'a') as f:
    f.write(f"{review_status}={review_status}\n")

if review_status == "PASSED":
    # TOOD: Add thumbs up reaction to the commit
    print("👍 Code review passed!")
    print(Markdown(review_comments))
elif review_status == "FAILED":
    # TODO: Leave a comment with the review_comments
    print("🛑 Code review failed!")
    print(Markdown(review_comments))
    sys.exit(1)
elif review_status == "COMMENTS":
    print(f"Comments: {review_comments}")
    print(Markdown(review_comments))
    sys.exit(0)
